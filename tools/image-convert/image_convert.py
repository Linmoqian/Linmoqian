# 将图集批量转换为 WebP 并限制长边，输出到独立目录便于快速预览
# Created on 2026-10-14
# @author: https://github.com/Linmoqian

import os
import sys
from pathlib import Path

from PIL import Image, ImageOps

# 仅处理常见位图格式，HEIC、RAW 等需要额外解码器
SOURCE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
DEFAULT_QUALITY = 82
DEFAULT_MAX_EDGE = 1920
# 编码 method 取 6，在压缩率与耗时之间取平衡
WEBP_METHOD = 6
# 动画帧缺少时长信息时的兜底值，单位毫秒
DEFAULT_FRAME_DURATION = 100

GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
CYAN = "\033[36m"
RESET = "\033[0m"
# 重定向输出、CI 或设置 NO_COLOR 时降级为纯文本标签
USE_COLOR = sys.stdout.isatty() and not os.environ.get("NO_COLOR")


def tagged(tag: str, color: str) -> str:
    if not USE_COLOR:
        return f"[{tag}]"
    return f"{color}[{tag}]{RESET}"


def size_text(num_bytes: int) -> str:
    if num_bytes >= 1024 * 1024:
        return f"{num_bytes / 1024 / 1024:.2f} MB"
    return f"{num_bytes / 1024:.1f} KB"


def default_output(source: Path) -> Path:
    # 输出放在图集同级目录，不把结果混进原图集
    return source.parent / f"{source.name}_webp"


def prompt_text(prompt: str, default: str) -> str:
    try:
        value = input(f"{tagged('输入', CYAN)} {prompt} [{default}]: ").strip()
    except EOFError:
        return default
    return value or default


def prompt_dir(prompt: str, default: Path, must_exist: bool) -> Path:
    # 输入目录必须存在，否则后续扫描会静默返回空结果；输出目录允许尚未创建
    current = str(default)
    for _ in range(3):
        # 从资源管理器复制来的路径常带引号，这里一并去掉
        raw = prompt_text(prompt, current).strip('"').strip("'")
        path = Path(raw).expanduser()
        if path.is_file():
            print(f"{tagged('错误', RED)} 这是文件而不是目录: {path}")
        elif path.is_dir() or (not must_exist and path.parent.is_dir()):
            return path.resolve()
        else:
            print(f"{tagged('错误', RED)} 目录不存在: {path}")
        current = raw
    print(f"{tagged('错误', RED)} 连续 3 次未给出有效目录，退出")
    raise SystemExit(1)


def prompt_int(prompt: str, default: int, low: int, high: int) -> int:
    for _ in range(3):
        raw = prompt_text(prompt, str(default))
        try:
            value = int(raw)
        except ValueError:
            print(f"{tagged('错误', RED)} 需要整数: {raw}")
            continue
        if low <= value <= high:
            return value
        print(f"{tagged('错误', RED)} 取值范围 {low}-{high}: {value}")
    print(f"{tagged('错误', RED)} 连续 3 次未给出有效数值，退出")
    raise SystemExit(1)


def env_int(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        message = f"环境变量 {name} 不是整数，改用默认值 {default}: {raw}"
        print(f"{tagged('警告', YELLOW)} {message}")
        return default


def env_dir(name: str, must_exist: bool) -> Path | None:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return None
    path = Path(raw).expanduser()
    # 输出目录允许不存在，但父目录必须存在，否则视为路径写错
    if path.is_file() or (must_exist and not path.is_dir()) or not path.parent.is_dir():
        print(f"{tagged('错误', RED)} 环境变量 {name} 指向的不是有效目录: {path}")
        raise SystemExit(1)
    return path.resolve()


def resolve_settings() -> tuple[Path, Path, int, int]:
    # 交互式终端逐项询问；CI 与管道场景改用环境变量，避免阻塞等待输入
    if sys.stdin.isatty():
        source = prompt_dir("图集目录", Path.cwd(), True)
        output = prompt_dir("输出目录", default_output(source), False)
        quality = prompt_int("WebP 质量 (1-100)", DEFAULT_QUALITY, 1, 100)
        max_edge = prompt_int("长边像素 (0 表示不缩放)", DEFAULT_MAX_EDGE, 0, 20000)
        return source, output, quality, max_edge

    source = env_dir("IMG_SOURCE", True)
    if source is None:
        message = "非交互环境需要在环境变量 IMG_SOURCE 中指定图集目录"
        print(f"{tagged('错误', RED)} {message}")
        raise SystemExit(1)
    output = env_dir("IMG_OUTPUT", False) or default_output(source)
    quality = env_int("IMG_QUALITY", DEFAULT_QUALITY)
    max_edge = env_int("IMG_MAX_EDGE", DEFAULT_MAX_EDGE)
    return source, output, quality, max_edge


def collect_files(source: Path, output: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(source.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in SOURCE_SUFFIXES:
            continue
        # 输出目录可能落在图集内部，跳过自己的产物防止反复转码
        if output != source and (output == path or output in path.parents):
            continue
        files.append(path)
    return files


def plan_targets(files: list[Path], source: Path, output: Path) -> dict[Path, Path]:
    plan: dict[Path, Path] = {}
    claimed: dict[Path, Path] = {}
    for path in files:
        target = output / path.relative_to(source).with_suffix(".webp")
        # a.jpg 与 a.png 会撞到同一个目标名，追加序号避免相互覆盖
        if target in claimed:
            index = 1
            while True:
                candidate = target.with_name(f"{target.stem}_{index}{target.suffix}")
                if candidate not in claimed:
                    target = candidate
                    break
                index += 1
        claimed[target] = path
        plan[path] = target
    return plan


def frame_has_alpha(image: Image.Image) -> bool:
    if image.mode in ("RGBA", "LA"):
        return True
    return image.mode == "P" and "transparency" in image.info


def fit_frame(frame: Image.Image, max_edge: int) -> Image.Image:
    if max_edge <= 0:
        return frame
    longest = max(frame.size)
    if longest <= max_edge:
        return frame
    scale = max_edge / longest
    size = (
        max(1, round(frame.width * scale)),
        max(1, round(frame.height * scale))
    )
    return frame.resize(size, Image.Resampling.LANCZOS)


def load_frames(
    image: Image.Image,
    max_edge: int
) -> tuple[list[Image.Image], list[int], int]:
    # 动图逐帧取出，保留帧时长与循环次数，转成 WebP 后仍能播放
    count = getattr(image, "n_frames", 1)
    frames: list[Image.Image] = []
    durations: list[int] = []
    # 透明模式按首帧判断，逐帧重新判断会让同一动图出现混合模式，保存时报错
    image.seek(0)
    mode = "RGBA" if frame_has_alpha(image) else "RGB"
    for index in range(count):
        image.seek(index)
        frame = image.convert(mode)
        frames.append(fit_frame(frame, max_edge))
        durations.append(int(image.info.get("duration", DEFAULT_FRAME_DURATION)))
    loop = int(image.info.get("loop", 0))
    return frames, durations, loop


def convert_file(path: Path, target: Path, quality: int, max_edge: int) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(path) as image:
        # 手机照片常带方向标记，需要按 EXIF 摆正；exif_transpose 会丢掉动图其余帧，
        # 因此只对静态图使用
        if getattr(image, "n_frames", 1) == 1:
            image = ImageOps.exif_transpose(image)
        frames, durations, loop = load_frames(image, max_edge)
        if len(frames) > 1:
            frames[0].save(
                target,
                format="WEBP",
                save_all=True,
                append_images=frames[1:],
                duration=durations,
                loop=loop,
                quality=quality,
                method=WEBP_METHOD
            )
            return
        frames[0].save(
            target,
            format="WEBP",
            quality=quality,
            method=WEBP_METHOD
        )


def run(source: Path, output: Path, quality: int, max_edge: int) -> int:
    files = collect_files(source, output)
    if not files:
        print(f"{tagged('警告', YELLOW)} 目录内没有可转换的图片: {source}")
        return 0
    plan = plan_targets(files, source, output)
    total_in = 0
    total_out = 0
    converted = 0
    skipped = 0
    failed = 0
    for index, path in enumerate(files, 1):
        target = plan[path]
        # 已转换过的图片直接跳过，需要重转时删除输出目录里的对应文件
        if target.exists():
            skipped += 1
            print(f"{tagged('跳过', YELLOW)} {target.relative_to(output)} 已有输出")
            continue
        before = path.stat().st_size
        try:
            convert_file(path, target, quality, max_edge)
        except Exception as error:
            failed += 1
            # 清掉半成品，避免下次运行把它当成已完成而跳过
            target.unlink(missing_ok=True)
            print(f"{tagged('错误', RED)} {path.relative_to(source)}: {error}")
            continue
        after = target.stat().st_size
        total_in += before
        total_out += after
        converted += 1
        message = (
            f"{tagged('成功', GREEN)} {index}/{len(files)}"
            f" {path.relative_to(source)} -> {target.relative_to(output)}"
            f"  {size_text(before)} -> {size_text(after)}"
        )
        print(message)
    print(f"转换 {converted} 张，跳过 {skipped} 张，失败 {failed} 张")
    if converted:
        saved = (1 - total_out / total_in) * 100
        before_text = size_text(total_in)
        after_text = size_text(total_out)
        print(f"总体积 {before_text} -> {after_text}，节省 {saved:.0f}%")
    return 1 if failed else 0


def main() -> int:
    # 管道与重定向时 Python 默认按本地代码页编码，PowerShell 7 按 UTF-8 读取会乱码
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    source, output, quality, max_edge = resolve_settings()
    if source == output:
        print(f"{tagged('警告', YELLOW)} 输出目录与图集目录相同，转换结果会与原图混放")
    print(f"图集目录: {source}")
    print(f"输出目录: {output}")
    print(f"质量: {quality}，长边: {max_edge if max_edge > 0 else '不缩放'}")
    return run(source, output, quality, max_edge)


if __name__ == "__main__":
    raise SystemExit(main())

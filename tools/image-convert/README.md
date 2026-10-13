# image-convert

把图集批量转成 WebP，长边限制 1920px，输出到图集同级的 `<图集名>_webp` 目录，便于快速预览。

处理 `.jpg`、`.jpeg`、`.png`、`.webp`、`.gif`，递归子目录。动图转成动画 WebP 并保留帧时长与循环次数；带透明通道的 PNG 保留透明；按 EXIF 方向摆正后再缩放。

## 运行

```powershell
cd tools/image-convert
uv sync
uv run image_convert.py
```

命令不带参数，运行后逐项询问，回车接受默认值：

| 项目 | 默认值 |
| --- | --- |
| 图集目录 | 当前目录 |
| 输出目录 | `<图集名>_webp`，与图集同级 |
| WebP 质量 | 82 |
| 长边像素 | 1920，填 0 表示不缩放 |

原图不修改，只读不写。已有同名输出且不比原图旧的图片会跳过；原图被替换过（文件时间更新）会重新转换。输出目录与图集目录相同时，已生成的 `.webp` 原样保留，不会自我重压。

## 非交互运行

CI 或管道环境不会弹出询问，改为读取环境变量；缺少 `IMG_SOURCE` 时报错并以非零码退出。

```powershell
$env:IMG_SOURCE = 'D:\photos'
$env:IMG_OUTPUT = 'D:\photos_webp'
$env:IMG_QUALITY = '82'
$env:IMG_MAX_EDGE = '1920'
uv run image_convert.py
```

| 环境变量 | 默认值 | 说明 |
| --- | --- | --- |
| `IMG_SOURCE` | 无，必填 | 图集目录，非交互运行必须提供 |
| `IMG_OUTPUT` | `<图集名>_webp` | 输出目录，允许尚不存在 |
| `IMG_QUALITY` | `82` | WebP 质量 |
| `IMG_MAX_EDGE` | `1920` | 长边像素，`0` 表示不缩放 |
| `IMG_FORCE` | 不设 | 设为 `1` 时忽略已有输出强制重压 |

仓库的 `.github/workflows/image-compress.yml` 用同一脚本做自动化：推送到 main 且改动涉及 `assets/images/**` 时，在 CI 里强制重压并把新的 `.webp` 提交回仓库。CI 使用 `IMG_FORCE=1`，因为干净检出后的文件时间不可靠。

网络无法直连 PyPI 时，同步依赖可指定镜像源：`uv sync --default-index https://mirrors.aliyun.com/pypi/simple/`。

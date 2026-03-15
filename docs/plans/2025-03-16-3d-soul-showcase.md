# 3D灵魂展示页面实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 创建单HTML文件的3D交互页面，展示DNA螺旋星云灵魂形态

**Architecture:** 使用Three.js构建粒子系统，单文件内联CSS/JS，无需打包工具

**Tech Stack:** Three.js r160 (CDN), ES Modules, Vanilla JS

---

## Task 1: 创建HTML骨架结构

**Files:**
- Create: `soul.html`

**Step 1: 创建HTML基础结构**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>灵魂归处 | Soul's Home</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { overflow: hidden; background: #0f0f23; font-family: 'Georgia', serif; }
        #canvas-container { width: 100vw; height: 100vh; position: fixed; top: 0; left: 0; }
        #quote {
            position: fixed;
            bottom: 10%;
            left: 50%;
            transform: translateX(-50%);
            text-align: center;
            color: rgba(192, 132, 252, 0.9);
            text-shadow: 0 0 20px rgba(124, 58, 237, 0.5);
            pointer-events: none;
            z-index: 10;
        }
        #quote .zh { font-size: 1.5rem; margin-bottom: 0.5rem; }
        #quote .en { font-size: 1rem; opacity: 0.8; font-style: italic; }
        #loading {
            position: fixed;
            top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            color: #c084fc;
            font-size: 1.2rem;
            z-index: 100;
        }
    </style>
</head>
<body>
    <div id="loading">灵魂正在凝聚...</div>
    <div id="canvas-container"></div>
    <div id="quote">
        <div class="zh">非选择的战场，乃灵魂的归处。</div>
        <div class="en">Not a battlefield of choice, but the home of the soul.</div>
    </div>
    <script type="module">
        import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';
        import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/controls/OrbitControls.js';

        // 代码将在后续任务中添加
    </script>
</body>
</html>
```

**Step 2: 在浏览器中测试打开**

打开: `file:///d:/project/Linmoqian/soul.html`
Expected: 显示加载文字"灵魂正在凝聚..."，紫色背景

**Step 3: Commit**

```bash
git add soul.html
git commit -m "feat: 添加3D灵魂页面HTML骨架

- 响应式画布容器
- 名言展示组件
- 紫色主题样式

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 2: 初始化Three.js场景

**Files:**
- Modify: `soul.html` (script部分)

**Step 1: 添加场景初始化代码**

在 `<script type="module">` 标签内添加:

```javascript
// === 场景初始化 ===
const container = document.getElementById('canvas-container');
const loading = document.getElementById('loading');

// 创建场景
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0f0f23);
scene.fog = new THREE.FogExp2(0x0f0f23, 0.0008);

// 创建相机
const camera = new THREE.PerspectiveCamera(
    75,
    window.innerWidth / window.innerHeight,
    0.1,
    5000
);
camera.position.set(0, 0, 500);

// 创建渲染器
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
container.appendChild(renderer.domElement);

// 轨道控制器
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.minDistance = 100;
controls.maxDistance = 1500;
controls.autoRotate = true;
controls.autoRotateSpeed = 0.2;

// 窗口自适应
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

// 隐藏加载提示
loading.style.opacity = '0';
setTimeout(() => loading.remove(), 500);

console.log('✓ 场景初始化完成');
```

**Step 2: 测试场景初始化**

刷新浏览器
Expected: 黑紫色背景，可以拖动旋转视角，无报错

**Step 3: Commit**

```bash
git add soul.html
git commit -m "feat: 初始化Three.js场景

- 场景、相机、渲染器配置
- OrbitControls轨道控制
- 响应式窗口适配
- 雾效深度感

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 3: 创建星空背景

**Files:**
- Modify: `soul.html` (script部分)

**Step 1: 添加星空粒子系统代码**

在场景初始化代码后添加:

```javascript
// === 星空背景 ===
function createStarField() {
    const starGeometry = new THREE.BufferGeometry();
    const starCount = 1000;
    const positions = new Float32Array(starCount * 3);
    const colors = new Float32Array(starCount * 3);
    const sizes = new Float32Array(starCount);

    const colorPalette = [
        new THREE.Color(0xffffff),
        new THREE.Color(0xc4b5fd),
        new THREE.Color(0x818cf8),
        new THREE.Color(0x22d3ee)
    ];

    for (let i = 0; i < starCount; i++) {
        const i3 = i * 3;

        // 球形分布
        const radius = 1500 + Math.random() * 1000;
        const theta = Math.random() * Math.PI * 2;
        const phi = Math.acos(2 * Math.random() - 1);

        positions[i3] = radius * Math.sin(phi) * Math.cos(theta);
        positions[i3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
        positions[i3 + 2] = radius * Math.cos(phi);

        // 随机颜色
        const color = colorPalette[Math.floor(Math.random() * colorPalette.length)];
        colors[i3] = color.r;
        colors[i3 + 1] = color.g;
        colors[i3 + 2] = color.b;

        sizes[i] = Math.random() * 2 + 0.5;
    }

    starGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    starGeometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    starGeometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));

    const starMaterial = new THREE.PointsMaterial({
        size: 2,
        vertexColors: true,
        transparent: true,
        opacity: 0.8,
        sizeAttenuation: true
    });

    const stars = new THREE.Points(starGeometry, starMaterial);
    scene.add(stars);

    // 缓慢旋转动画
    stars.userData.rotationSpeed = {
        x: (Math.random() - 0.5) * 0.0001,
        y: (Math.random() - 0.5) * 0.0001
    };

    return stars;
}

const starField = createStarField();
console.log('✓ 星空背景创建完成');
```

**Step 2: 在动画循环中更新星空**

添加基础动画循环:

```javascript
// === 动画循环 ===
function animate() {
    requestAnimationFrame(animate);

    // 星空旋转
    starField.rotation.x += starField.userData.rotationSpeed.x;
    starField.rotation.y += starField.userData.rotationSpeed.y;

    controls.update();
    renderer.render(scene, camera);
}

animate();
```

**Step 3: 测试星空效果**

刷新浏览器
Expected: 看到1000颗星星缓慢旋转，不同颜色

**Step 4: Commit**

```bash
git add soul.html
git commit -m "feat: 添加星空背景粒子系统

- 1000颗球形分布粒子
- 多色星光（白/紫/蓝/青）
- 缓慢自转动画

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 4: 创建DNA螺旋核心

**Files:**
- Modify: `soul.html` (script部分)

**Step 1: 添加螺旋结构代码**

```javascript
// === DNA螺旋灵魂形态 ===
function createSpiralSoul() {
    const group = new THREE.Group();

    // 螺旋参数
    const turns = 3;           // 螺旋圈数
    const pointsPerTurn = 200; // 每圈点数
    const radius = 80;         // 螺旋半径
    const height = 400;        // 螺旋高度
    const tubeRadius = 3;      // 粒子管径

    // 两条链的颜色
    const chain1Color = new THREE.Color(0x7c3aed);
    const chain2Color = new THREE.Color(0xc084fc);

    for (let chain = 0; chain < 2; chain++) {
        const geometry = new THREE.BufferGeometry();
        const positions = [];
        const colors = [];

        for (let i = 0; i <= turns * pointsPerTurn; i++) {
            const t = i / pointsPerTurn;
            const angle = t * Math.PI * 2;
            const y = (t / turns - 0.5) * height;

            // 双螺旋偏移
            const phase = chain * Math.PI;
            const x = Math.cos(angle + phase) * radius;
            const z = Math.sin(angle + phase) * radius;

            positions.push(x, y, z);

            // 颜色渐变
            const color = chain === 0 ? chain1Color : chain2Color;
            const gradient = (Math.sin(t * Math.PI) + 1) / 2;
            colors.push(
                color.r * (0.5 + gradient * 0.5),
                color.g * (0.5 + gradient * 0.5),
                color.b * (0.5 + gradient * 0.5)
            );
        }

        geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

        const material = new THREE.PointsMaterial({
            size: tubeRadius * 2,
            vertexColors: true,
            transparent: true,
            opacity: 0.9,
            blending: THREE.AdditiveBlending
        });

        const points = new THREE.Points(geometry, material);
        group.add(points);
    }

    // 添加连接线（碱基对）
    const baseGeometry = new THREE.BufferGeometry();
    const basePositions = [];
    const baseColors = [];

    for (let i = 0; i < turns * pointsPerTurn; i += 5) {
        const t = i / pointsPerTurn;
        const angle = t * Math.PI * 2;
        const y = (t / turns - 0.5) * height;

        // 链1位置
        basePositions.push(
            Math.cos(angle) * radius,
            y,
            Math.sin(angle) * radius
        );

        // 链2位置
        basePositions.push(
            Math.cos(angle + Math.PI) * radius,
            y,
            Math.sin(angle + Math.PI) * radius
        );

        // 流光颜色
        const hue = (t + performance.now() * 0.0001) % 1;
        const color = new THREE.Color().setHSL(0.75 + hue * 0.15, 0.8, 0.6);
        baseColors.push(color.r, color.g, color.b);
        baseColors.push(color.r, color.g, color.b);
    }

    baseGeometry.setAttribute('position', new THREE.Float32BufferAttribute(basePositions, 3));
    baseGeometry.setAttribute('color', new THREE.Float32BufferAttribute(baseColors, 3));

    const baseMaterial = new THREE.LineBasicMaterial({
        vertexColors: true,
        transparent: true,
        opacity: 0.4,
        blending: THREE.AdditiveBlending
    });

    const baseLines = new THREE.LineSegments(baseGeometry, baseMaterial);
    group.add(baseLines);

    scene.add(group);

    // 动画数据
    group.userData = {
        breathePhase: 0,
        breatheSpeed: 0.001
    };

    return group;
}

const spiralSoul = createSpiralSoul();
console.log('✓ 螺旋灵魂形态创建完成');
```

**Step 2: 添加呼吸动画**

在animate()函数中添加:

```javascript
// 呼吸效果
spiralSoul.userData.breathePhase += spiralSoul.userData.breatheSpeed;
const breatheScale = 1 + Math.sin(spiralSoul.userData.breathePhase) * 0.1;
spiralSoul.scale.set(breatheScale, breatheScale, breatheScale);

// 缓慢旋转
spiralSoul.rotation.y += 0.002;
```

**Step 3: 测试螺旋效果**

刷新浏览器
Expected: 看到双螺旋结构，呼吸缩放，旋转动画

**Step 4: Commit**

```bash
git add soul.html
git commit -m "feat: 添加DNA双螺旋灵魂形态

- 双链螺旋结构
- 碱基对连接线
- 呼吸缩放动画
- 流光颜色渐变

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 5: 添加流动粒子系统

**Files:**
- Modify: `soul.html` (script部分)

**Step 1: 添加流动粒子代码**

在螺旋创建后添加:

```javascript
// === 流动粒子系统 ===
function createFlowingParticles() {
    const particleCount = 2000;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);
    const sizes = new Float32Array(particleCount);
    const velocities = [];

    const colorPalette = [
        new THREE.Color(0x7c3aed),  // 紫色
        new THREE.Color(0xc084fc),  // 浅紫
        new THREE.Color(0x22d3ee),  // 青色
        new THREE.Color(0xe879f9)   // 粉色
    ];

    for (let i = 0; i < particleCount; i++) {
        const i3 = i * 3;

        // 随机位置（球形分布）
        const radius = 50 + Math.random() * 150;
        const theta = Math.random() * Math.PI * 2;
        const phi = Math.random() * Math.PI;

        positions[i3] = radius * Math.sin(phi) * Math.cos(theta);
        positions[i3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
        positions[i3 + 2] = radius * Math.cos(phi);

        // 随机颜色
        const color = colorPalette[Math.floor(Math.random() * colorPalette.length)];
        colors[i3] = color.r;
        colors[i3 + 1] = color.g;
        colors[i3 + 2] = color.b;

        sizes[i] = Math.random() * 3 + 1;

        // 速度（向中心或向外）
        velocities.push({
            x: (Math.random() - 0.5) * 0.3,
            y: (Math.random() - 0.5) * 0.3,
            z: (Math.random() - 0.5) * 0.3,
            orbitRadius: radius,
            orbitSpeed: (Math.random() - 0.5) * 0.01,
            orbitAngle: theta
        });
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));

    const material = new THREE.PointsMaterial({
        size: 2,
        vertexColors: true,
        transparent: true,
        opacity: 0.6,
        blending: THREE.AdditiveBlending,
        sizeAttenuation: true
    });

    const particles = new THREE.Points(geometry, material);
    particles.userData.velocities = velocities;

    return particles;
}

const flowingParticles = createFlowingParticles();
spiralSoul.add(flowingParticles);
console.log('✓ 流动粒子系统创建完成');
```

**Step 2: 添加粒子运动动画**

在animate()函数中添加:

```javascript
// 粒子流动
const positions = flowingParticles.geometry.attributes.position.array;
const velocities = flowingParticles.userData.velocities;

for (let i = 0; i < velocities.length; i++) {
    const i3 = i * 3;

    // 轨道运动
    velocities[i].orbitAngle += velocities[i].orbitSpeed;

    // 更新位置
    positions[i3] = Math.cos(velocities[i].orbitAngle) * velocities[i].orbitRadius;
    positions[i3 + 1] += Math.sin(performance.now() * 0.001 + i) * 0.1;
    positions[i3 + 2] = Math.sin(velocities[i].orbitAngle) * velocities[i].orbitRadius;
}

flowingParticles.geometry.attributes.position.needsUpdate = true;
```

**Step 3: 测试粒子效果**

刷新浏览器
Expected: 2000个粒子围绕螺旋流动

**Step 4: Commit**

```bash
git add soul.html
git commit -m "feat: 添加流动粒子系统

- 2000个多色粒子
- 轨道运动动画
- 加法混合发光效果

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 6: 实现交互效果

**Files:**
- Modify: `soul.html` (script部分)

**Step 1: 添加交互代码**

```javascript
// === 交互系统 ===
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
let isHovering = false;

// 鼠标移动
window.addEventListener('mousemove', (event) => {
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
});

// 点击效果
window.addEventListener('click', () => {
    if (isHovering) {
        explodeParticles();
    }
});

// 粒子爆炸效果
function explodeParticles() {
    const positions = flowingParticles.geometry.attributes.position.array;
    const velocities = flowingParticles.userData.velocities;

    for (let i = 0; i < velocities.length; i++) {
        const i3 = i * 3;
        const burstStrength = 50;

        velocities[i].orbitRadius += (Math.random() - 0.5) * burstStrength;
        positions[i3] += (Math.random() - 0.5) * burstStrength;
        positions[i3 + 1] += (Math.random() - 0.5) * burstStrength;
        positions[i3 + 2] += (Math.random() - 0.5) * burstStrength;
    }

    flowingParticles.geometry.attributes.position.needsUpdate = true;

    // 1秒后重组
    setTimeout(() => {
        resetParticles();
    }, 1000);
}

// 重置粒子
function resetParticles() {
    const positions = flowingParticles.geometry.attributes.position.array;
    const velocities = flowingParticles.userData.velocities;

    for (let i = 0; i < velocities.length; i++) {
        const i3 = i * 3;
        velocities[i].orbitRadius = 50 + Math.random() * 150;
    }
}
```

**Step 2: 添加悬停检测**

在animate()函数中添加:

```javascript
// 悬停检测
raycaster.setFromCamera(mouse, camera);
const intersects = raycaster.intersectObject(flowingParticles);

if (intersects.length > 0 && !isHovering) {
    isHovering = true;
    document.body.style.cursor = 'pointer';
    flowingParticles.material.size = 4;
} else if (intersects.length === 0 && isHovering) {
    isHovering = false;
    document.body.style.cursor = 'default';
    flowingParticles.material.size = 2;
}
```

**Step 3: 测试交互效果**

刷新浏览器
Expected: 鼠标悬停粒子变大，点击爆炸后重组

**Step 4: Commit**

```bash
git add soul.html
git commit -m "feat: 添加交互系统

- Raycaster悬停检测
- 点击粒子爆炸效果
- 自动重组动画
- 鼠标指针反馈

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 7: 优化和最终调整

**Files:**
- Modify: `soul.html`

**Step 1: 添加性能优化**

在场景初始化后添加:

```javascript
// 性能优化
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

// 帧率监控（可选）
let frameCount = 0;
let lastTime = performance.now();
setInterval(() => {
    const fps = frameCount;
    frameCount = 0;
    if (fps < 30) {
        console.warn('低帧率:', fps);
    }
}, 1000);

// 在animate函数开始添加
frameCount++;
```

**Step 2: 添加键盘快捷键**

```javascript
// 快捷键
window.addEventListener('keydown', (event) => {
    switch(event.key) {
        case 'r': // 重置视角
            camera.position.set(0, 0, 500);
            controls.reset();
            break;
        case ' ': // 空格爆炸
            explodeParticles();
            break;
    }
});
```

**Step 3: 完善加载体验**

```javascript
// 渐进式加载
async function loadProgressively() {
    // 先显示星空
    const starField = createStarField();
    await new Promise(r => setTimeout(r, 100));

    // 再显示螺旋
    const spiralSoul = createSpiralSoul();
    await new Promise(r => setTimeout(r, 100));

    // 最后显示粒子
    const flowingParticles = createFlowingParticles();
    spiralSoul.add(flowingParticles);

    loading.style.opacity = '0';
    setTimeout(() => loading.remove(), 500);
}

loadProgressively();
```

**Step 4: 最终测试**

在浏览器中完整测试:
1. 页面加载流畅
2. 星空旋转正常
3. 螺旋呼吸动画
4. 粒子流动效果
5. 鼠标交互响应
6. 点击爆炸效果
7. 快捷键功能

**Step 5: 最终提交**

```bash
git add soul.html
git commit -m "feat: 3D灵魂展示页面完成

- 完整3D场景
- DNA螺旋星云形态
- 交互式粒子系统
- 性能优化完成

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 8: 更新README添加入口

**Files:**
- Modify: `README-ZH.md`
- Modify: `README.md`

**Step 1: 在自述部分添加3D展示入口**

在README-ZH.md的"关于我"部分添加:

```markdown
<div align="center">

[![3D展示](https://img.shields.io/badge/🌌_探索灵魂空间-7c3aed?style=for-the-badge)](soul.html)

</div>
```

在README.md的"About Me"部分添加:

```markdown
<div align="center">

[![3D Soul](https://img.shields.io/badge/🌌_Explore_Soul_Space-7c3aed?style=for-the-badge)](soul.html)

</div>
```

**Step 2: 测试链接**

点击README中的徽章
Expected: 正确跳转到soul.html页面

**Step 3: 提交**

```bash
git add README.md README-ZH.md
git commit -m "docs: 添加3D灵魂展示入口

- README中添加展示入口徽章
- 中英文版本同步更新

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## 验收标准

- [ ] 页面在浏览器中正常加载
- [ ] 星空背景缓慢旋转
- [ ] DNA双螺旋呼吸动画流畅
- [ ] 2000粒子持续流动
- [ ] 鼠标悬停有反馈
- [ ] 点击触发粒子爆炸
- [ ] 快捷键(r/空格)正常工作
- [ ] 帧率稳定在60fps
- [ ] README入口链接正确

---

## 预计时间

约45-60分钟

---

**设计文档**: [docs/plans/2025-03-16-3d-soul-showcase-design.md](./2025-03-16-3d-soul-showcase-design.md)

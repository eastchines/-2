# 蓝白金键盘桌宠

一个会跟着你打字抬手敲击的桌面小精灵。中文输入法时是蓝发女孩，英文输入法时是蓝白羽翼神兽，按 Shift 一键切换形态。

---

## 功能一览

| 功能 | 说明 |
|------|------|
| 打字动画 | 按键盘任意键 → 播放「抬手→抬高→下落→触键」4帧敲击动画 |
| 形态切换 | 按 Shift 键切换 女孩（中文）↔ 神兽（英文） |
| 自动待机 | 停止按键 2 秒后自动回到待机姿势 |
| 窗口属性 | 置顶、无边框、透明背景、鼠标可拖动 |

---

## 快速开始（Windows）

### 1. 安装 Python

到官网下载 Python 3.8+：
https://www.python.org/downloads/

> 安装时务必勾选 **Add Python to PATH**

### 2. 安装依赖

打开 CMD，进入项目文件夹，执行：

```bash
pip install -r requirements.txt
```

### 3. 运行桌宠

```bash
python keyboard_pet.py
```

---

## 操作说明

| 操作 | 效果 |
|------|------|
| 按键盘任意字母/数字键 | 播放敲击动画 |
| 按 Shift 键 | 切换 女孩 ↔ 神兽 |
| 鼠标左键按住拖动 | 移动桌宠位置 |
| 停止按键 2 秒 | 自动回到待机姿势 |

---

## 项目文件结构

```
keyboard_deskpet/
├── keyboard_pet.py      # 主程序
├── requirements.txt     # Python 依赖
├── README.md            # 说明文档
└── images/              # 动画帧图片
    ├── girl_idle.png        # 女孩待机
    ├── girl_type_01.png     # 女孩打字帧1：手抬起
    ├── girl_type_02.png     # 女孩打字帧2：手抬最高
    ├── girl_type_03.png     # 女孩打字帧3：手向下落
    ├── girl_type_04.png     # 女孩打字帧4：手触键
    ├── animal_idle.png       # 神兽待机
    ├── animal_type_01.png    # 神兽打字帧1：爪抬起
    ├── animal_type_02.png    # 神兽打字帧2：爪抬最高
    ├── animal_type_03.png    # 神兽打字帧3：爪向下落
    └── animal_type_04.png    # 神兽打字帧4：爪触键
```

---

## 打包成 EXE（免安装直接运行）

有两种方式，推荐用 **GitHub Actions 云端打包**，本地什么都不用装。

---

### 方式一：GitHub Actions 云端自动打包（推荐，零本地安装）

项目里已经自带了 `.github/workflows/build.yml` 配置，只要传到 GitHub 就能自动编译出 exe。

#### 步骤：

1. 注册/登录 GitHub，新建一个仓库（比如叫 `keyboard-deskpet`）
2. 把这个项目文件夹里的**所有文件**都上传到仓库 main 分支
   - 可以直接在网页上拖拽上传，包括 `.github` 隐藏文件夹
3. 上传后 GitHub Actions 会自动开始打包（大约 1-2 分钟）
4. 进入仓库的 **Actions** 标签页，点进去最新的一次构建
5. 页面下方 **Artifacts** 区域，下载「键盘桌宠EXE」
6. 解压后得到单个 `keyboard_pet.exe`，**双击直接运行，不需要装任何软件**

> 打出来的 exe 是单文件，图片已经打包进去了，不用额外带 images 文件夹。

---

### 方式二：本地打包（需要先装 Python）

#### 1. 安装 PyInstaller

```bash
pip install pyinstaller
```

#### 2. 打包命令（图片自动打包进 exe）

```bash
pyinstaller -F -w --noconsole --add-data "images;images" keyboard_pet.py
```

参数说明：
- `-F`：打包成单个 exe 文件
- `-w`：不弹出黑色控制台窗口
- `--add-data "images;images"`：把 images 文件夹一起打包进 exe

#### 3. 获取 EXE

打包完成后，在 `dist` 文件夹里找到 `keyboard_pet.exe`，双击即可运行。

> 本地打出来的是单文件 exe，图片已经内嵌，不用额外带 images 文件夹。

---

## 替换图片（重要）

打包后的 exe **支持外部替换图片**，无需重新打包：

1. 在 `keyboard_pet.exe` **旁边**新建一个 `images` 文件夹
2. 把你自己的 PNG 图片按同名放进去
3. 重新启动 exe，就会自动用你替换的图

读取顺序：**exe 旁边的 images 文件夹 → 内置默认图**。
也就是说，你不建 images 文件夹也能正常跑（用内置默认图）；一旦放了同名图，就优先用你的。

可替换的文件名（必须一字不差）：

```
girl_idle.png          少女待机
girl_type_01.png       少女打字帧1（手抬起）
girl_type_02.png       少女打字帧2（手抬最高）
girl_type_03.png       少女打字帧3（手向下落）
girl_type_04.png       少女打字帧4（手触键）
animal_idle.png        神兽待机
animal_type_01.png     神兽打字帧1
animal_type_02.png     神兽打字帧2
animal_type_03.png     神兽打字帧3
animal_type_04.png     神兽打字帧4
switch_01.png          切换过渡帧1
switch_02.png          切换过渡帧2
switch_03.png          切换过渡帧3
switch_04.png          切换过渡帧4
girl_walk_01.png       少女走路帧1
girl_walk_02.png       少女走路帧2
girl_walk_03.png       少女走路帧3
girl_walk_04.png       少女走路帧4
```

要求：**透明背景 PNG**（JPG 会有白底），同组动作帧角色和位置保持一致。

---

## 自定义修改

打开 `keyboard_pet.py`，顶部有配置区：

```python
IDLE_DELAY = 2000      # 停止按键后多久回到待机（毫秒）
IDLE_TO_WALK_MS = 60000  # 空闲多久后自动游走（毫秒）
PET_W = 360           # 桌宠窗口宽度（像素）
PET_H = 360           # 桌宠窗口高度（像素）
```

如果想换图片风格，按上面「替换图片」操作即可，不需要改代码。

---

## 常见问题

**Q：启动后图片不显示？**
A：检查 `images` 文件夹是否和 `keyboard_pet.py`/exe 在同一目录，图片文件名是否正确。

**Q：按键盘没有动画？**
A：先点击一下桌宠窗口让它获得焦点，再按键测试。

**Q：打包后 exe 打不开？**
A：路径不要有中文或空格。图片替换方式见上面「替换图片」。

**Q：替换了图片没生效？**
A：确认文件名和上面列表完全一致、放在 exe 同级的 images 文件夹里，然后重启 exe。

<h1 align="center">🐋 DeepSeek-Window-Pet</h1>

<p align="center">
  <b>一只蹲在屏幕角落、时不时冒一句怪话的 Windows 桌面宠物</b>
</p>

<p align="center">
  <img src="docs/images/hero.png" width="360" alt="DeepSeek-Window-Pet 桌宠形象">
</p>

<h3 align="center">用 Python + PySide6 写的 Windows 桌面宠物</h3>

<p align="center">
  把 DSH 余额挂件里那只小鲸鱼独立出来，做成一只蹲在屏幕角落、时不时冒一句怪话的桌宠。
</p>

<p align="center">
  <b>不联网 · 不读余额 · 不接 AI · 不写注册表 · 不写 AppData · 没有开机自启</b><br>
  删掉文件夹，系统里什么都不剩。
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-203170.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/platform-Windows%2010%20%2F%2011%20x64-0078D4.svg" alt="Platform: Windows 10/11 x64">
  <img src="https://img.shields.io/badge/python-3.9%2B-3776AB.svg" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/GUI-PySide6-41CD52.svg" alt="PySide6">
</p>

---

<p align="center">
  <img src="docs/images/pet-demo.png" width="820" alt="桌宠实际效果：四档台词长度 + 贴左镜像（文字仍正着读）">
</p>

<p align="center">
  <sub>离屏渲染出的真实效果：四档不同长度的台词，最后一张是「拖到左半边自动镜像」——
  形象和气泡都翻转，<b>台词文字仍然正着读</b>。</sub>
</p>

> 📖 English README: [README.en.md](README.en.md)

---

## ⬇️ 下载

**不想装 Python，只想直接玩 → 点这里：**

<p align="center">
  <a href="https://github.com/wo-atmy/DeepSeek-Window-Pet/releases/latest">
    <img src="https://img.shields.io/badge/下载-Whale--Pet--Portable.zip-203170?style=for-the-badge&logo=windows&logoColor=white" alt="下载便携版">
  </a>
</p>

下载 `Whale-Pet-Portable.zip`（约 23 MB），**解压后双击 `WhalePet.exe`** 就能跑。

目标电脑**不需要装 Python / PySide6**，也不需要装 DSH 插件。
整个文件夹拷到任何 Windows 10 / 11 电脑上都能直接用（桌面 / D 盘 / U 盘都行）。

> ⚠️ 未签名的可执行文件，首次运行 Windows SmartScreen 可能提示"未知发布者"，
> 点「更多信息 → 仍要运行」即可。

---

## ✨ 她会做什么

| 交互 | 反应 |
|---|---|
| 等她一会儿 | 随机冒一句怪话（频率可调，能调成完全不说话） |
| **按下去** | 响一声按压音效 + 弹一下 |
| **松开** | 响一声松开音效 |
| 单击 | 弹一下（Q 弹）+ 回你一句（"别戳我。"这类） |
| 双击 | 立刻冒一句怪话 |
| 按住拖动 | 拖到任意位置，松手吸附屏幕边缘，位置会记住 |
| **拖到左半边** | **自动水平镜像**：形象和气泡翻转，**台词文字仍正着读** |
| **托盘图标** | **左键点、右键点都直接打开设置面板** |
| **右键她** | **没有反应** —— 设置入口刻意只留在托盘，免得随手点到她就弹面板 |

**设置面板**（223×434，弹在鼠标光标上方并自动夹进屏幕可用区）：

- **说一句** —— 立刻让她冒一句
- **说话频率** —— 闭嘴 / 安静 / 正常 / 话多 / 话痨
- **大小** —— 滑块，180 ~ 460 px，拖着当场变大变小
- **形象** —— 列出 `assets/skins/` 里的每个形象，点一下立刻换
- **音效** —— 开启 / 试听 / 切换音效组 + 音量滑块
- **其他** —— 总在最前 / 锁定位置 / 鼠标穿透 / 形象目录 / 音效目录 /
  编辑台词 / 重载台词 / 回到右下角 / 显示·隐藏 / 退出

<br clear="right">

### 说话频率

| 档位 | 自动冒话间隔 | 启动打招呼 |
|---|---|---|
| **闭嘴** | 完全不主动说话 | ❌ |
| **安静**（默认） | 5 ~ 15 分钟 | ❌ |
| 正常 | 1.5 ~ 3.5 分钟 | ✅ |
| 话多 | 30 ~ 70 秒 | ✅ |
| 话痨 | 8 ~ 20 秒 | ✅ |

### 全部设置都会记住

位置 / 大小 / 形象 / 音效组 / 音量 / 音效开关 / 说话频率 / 总在最前 /
锁定位置 / 鼠标穿透 / 贴左镜像 —— 都存在同目录的 `config.json` 里，
纯文本，可以直接用记事本改。**删掉 `config.json` = 恢复出厂设置。**

唯一**故意不记**的是「隐藏桌宠」：不然下次打开你什么都看不见，容易以为程序坏了。

---

## 🚀 怎么跑

### 方式一：下载便携版（推荐，不用装任何东西）

见上面的 [**下载**](#️-下载) 一节 → 从 [Releases](https://github.com/wo-atmy/DeepSeek-Window-Pet/releases/latest)
下载 `Whale-Pet-Portable.zip`。

### 方式二：从源码跑

```bash
git clone https://github.com/wo-atmy/DeepSeek-Window-Pet.git
cd DeepSeek-Window-Pet
python -m pip install -r requirements.txt
```

然后双击 **`start-pet.bat`**（用 `pythonw` 启动，不弹黑窗口），
或者直接 `python whale_pet.py`。

关掉：**托盘图标 → 退出**，或设置面板最下面的「退出」。

> 只想跑源码、不打包的话，只需要 **Python 3.9+** 和 **PySide6-Essentials**。
> 国内网络慢可以加清华源：`-i https://pypi.tuna.tsinghua.edu.cn/simple`

### 方式三：自己打包便携版

双击 **`build.bat`**，跑完会得到：

```
dist\WhalePet-Portable\        ← 把这个文件夹拷到别的电脑
    WhalePet.exe               ← 双击它就行
    _internal\                 ← Qt + Python 运行库（别删）
    assets\                    ← 形象 + 音效
    lines.json                 ← 台词库
    README.txt                 ← 便携版说明
    LICENSE.txt / THIRD-PARTY-NOTICES.txt
dist\Whale-Pet-Portable.zip    ← 或者直接拷这个压缩包
```

需要额外装 PyInstaller：`python -m pip install pyinstaller`

实测：目录约 **55 MB** / zip 约 **23 MB**，Windows 10、11 64 位通用。

打包时会剔除 Qt 里用不到的部件（其中 `opengl32sw.dll` 一个就占 20 MB ——
那是软件 OpenGL 回退库，本程序用 QPainter 光栅绘制，从不申请 OpenGL 表面），
以及未使用的平台后端、图像格式插件与翻译文件。详见 `build.bat` 内的注释。

**为什么 `assets\` 放在 exe 外面**（而不是打进去）：

1. 换形象 / 换音效不用重新打包，改文件就行；
2. **授权边界一眼可见** —— 见下面的[素材授权](#-素材授权重要)一节。

打包含几个优化：`--onedir` 而不是 `--onefile`（onefile 每次启动都要解压 Qt 到临时目录，
又慢又容易被杀软误报）；排除掉 QtQml / QtQuick / QtNetwork / QtSql / QtOpenGL 等没用的模块；
删掉 Qt 自带的约 7 MB 翻译文件。exe 图标由默认形象裁切生成。

代码里的 `app_dir()` 在冻结运行时取 **exe 自己的目录**（而不是 PyInstaller 的临时解包目录），
所以 `config.json` / `lines.json` / `assets/` 都跟 exe 待在一起，整个文件夹搬走即可。

### 方式四：让 GitHub 帮你打包（不用装 Python）

[`.github/workflows/release.yml`](.github/workflows/release.yml) 会在 GitHub 的
Windows 机器上自动打包，**你的电脑什么都不用装**。

**不会用 git 也没关系** —— 网页上点两下就行：

1. 打开仓库页面 → 顶部 **Actions** 标签
2. 左边选 **Release portable build** → 右边 **Run workflow** → 绿色按钮
3. 等两三分钟跑完，点开这次运行，页面底部 **Artifacts** 里就能下到
   `Whale-Pet-Portable.zip`

会 git 的话更省事，打个 tag 就全自动（构建 + 建好 Release + 挂上附件）：

```bash
git tag v1.0.0
git push origin v1.0.0
```

---

## 🎭 换形象（一个形象一个文件夹）

```
assets/skins/
    DSniang/                 ← 文件夹名 = 面板里显示的名字（默认形象）
        char.png             ← 纯角色（透明底）**必须**，程序画的就是这张
        bubble.png           ← 含对话框的整图，可选
    example/                 ← 代码生成的占位形象，可删
        char.png
        bubble.png
    我的角色/                 ← 你自己加的形象
        char.png
        bubble.png
    散图形象.png              ← 也认：一张散图直接当形象（图省事）
```

`char` 也可以叫 `character` / `角色` / `本体`；文件夹里找不到就跳过。
面板「形象」那一段会多一个按钮，点一下立刻换，**不影响原来的形象**。
鼠标悬停在按钮上会显示这个形象有没有配 `bubble.png`。

> **为什么建议放两张图**：这是插件自己的约定（纯角色裁切图 + 含空白气泡的整图）。
> 本项目**渲染只用纯角色那张** —— 气泡是代码画的 SVG，所以**台词多长都能自适应**，
> 不会被图片里那个固定大小的气泡挤爆。`bubble.png` 留着当参考。
>
> **摆放规则**（照抄插件 `.dshwv-img`）：图片缩到窗口边长的 **59.45%**、**贴右下角**，
> 气泡占据上方。所以选图时主角最好居中或偏右下。

## 🔊 换音效（一个音效组一个文件夹）

```
assets/sounds/
    example/     press.wav  release.wav
    我的音效/     press.mp3  release.mp3
```

扩展名 `mp3 / wav / m4a / ogg / aac` 都行，只放一个也能用（另一个不响）。

播放走 **Windows 原生 MCI**（`ctypes` 调 `winmm.mciSendString`），
**不用装 QtMultimedia**。MP3 支持调音量；WAV 不支持（MCI 限制），
失败会静默忽略、不影响播放。

## 💬 改台词（核心玩法）

编辑 `lines.json`：

```json
{
  "lines":       ["自己冒出来的怪话，一行一句", "..."],
  "click_lines": ["戳她时的回应", "..."]
}
```

存盘后托盘 →「重新载入台词」，**不用重启**。自带 75 条怪话 + 15 条回嘴。

---

## 🔒 独立性

程序**不联网、不读余额**，代码里没有任何 HTTP / socket / API 调用
（唯一命中的 `http://www.w3.org/2000/svg` 是 SVG 的命名空间标识，不是请求）。

**只认自己目录下的 `assets/`**：启动时最多 `mkdir` 一下 `assets/skins` 和
`assets/sounds`，**不扫描任何外部目录、不复制任何文件**。

> 早期版本启动时会去 DSH 插件目录翻默认形象和音效并搬过来，**已整个删除** ——
> 这个程序本质是个启动器，`assets/` 里有什么就用什么。

注册表、开机启动项、后台服务、AppData：**一个都不碰**。删掉文件夹 = 系统里什么都不剩。

---

## ⚖️ 素材授权（重要，要转发给别人时看这条）

这是**发布这个项目时最容易踩的坑**，所以单独说清楚。

本项目的**视觉参数**参考了
[MeteorNOX/DeepSeek-Balance-Whale-Widget](https://github.com/MeteorNOX/DeepSeek-Balance-Whale-Widget)
（MIT）。那个插件的 `PROVENANCE.md` 明确写着：

> `assets/` 下的美术素材（图片 / 动图 / 音效）**不在 MIT 覆盖范围内**，
> 仅供运行本插件使用，**不授予再许可**。

所以：

| 内容 | 协议 | 能不能再分发 |
|---|---|---|
| 本项目的代码（`whale_pet.py`、脚本、文档） | MIT (c) 2025 wo-atmy | ✅ 随便 |
| 合成音效 `assets/sounds/default/` | MIT (c) 2025 wo-atmy | ✅ 随便 |
| 角色形象 `assets/skins/DSniang/` 与宣传图 `docs/images/hero.png` | ⚠️ **二次创作，不在 MIT 内** | ⚠️ 非本项目原创，不视为可自由再分发 |
| 上游插件的**音效** | ❌ 不在 MIT 内 | ❌ **不能** |
| PySide6 运行时（便携版里） | LGPL v3 | ✅ 遵守 LGPL 即可 |

**具体说明：**

- **代码**（`whale_pet.py`、各脚本、文档）以 MIT 发布，随便用。
- **音效** `assets/sounds/default/` 的两声提示音是**合成的原创音频**，
  同样按 MIT 发布，可以随意替换、再分发。
- **角色形象**（`assets/skins/DSniang/` 和 README 顶部的宣传图）是**基于上游角色
  形象的二次创作**，不是本项目原创，因此**不在 MIT 范围内**。
  想正式发布或商用，建议换成**你有完整权利**的作品
  （替换方式见上面「换形象」一节，程序代码不受影响）。
- **上游插件的音效**未包含在本仓库中，已用合成音效替代。

完整说明见 [**THIRD-PARTY-NOTICES.md**](THIRD-PARTY-NOTICES.md)。

---

## 📁 仓库结构

```
.
├── whale_pet.py                  # 主程序（PySide6，单文件，约 1300 行）
├── lines.json                    # 台词库（改这个）
├── Whale-Pet-Portable.zip        # 便携版压缩包（约 23 MB，直接下载即用）
├── requirements.txt              # PySide6-Essentials
├── build.bat                     # 一键打包便携版
├── start-pet.bat / stop-pet.bat  # 源码方式启动 / 停止
├── app.ico                       # exe 图标
├── README.md / README.en.md      # 中文 / 英文说明
├── CHANGELOG.md                  # 更新日志
├── LICENSE                       # MIT 协议
├── THIRD-PARTY-NOTICES.md        # 第三方声明 / 素材授权边界
├── .gitignore                    # 运行时文件与打包产物不进版本库
├── .github/workflows/release.yml # 打 tag 自动出 Release
├── assets/                       # 素材
│   ├── skins/                    #   ← 一个文件夹一个形象（DSniang 为默认形象）
│   └── sounds/                   #   ← 一个文件夹一组音效
└── docs/
    ├── portable-readme.txt       # 给便携版用户看的简版说明（会打进 zip）
    └── images/                   # README 用图（hero / 实际渲染效果）
```

运行时生成（已在 `.gitignore` 里）：`config.json`、`pet.pid`、`build/`、`dist/`。

---

## 🧪 关于绘制验证

> **不要用 `CopyFromScreen` 截图验证这类窗口**：Windows 的 DWM 合成层抓不全，
> 白色泡体会被抓成半透明暗色、文字丢失 —— 看着像 bug，其实程序是对的。
> 要检查绘制结果，用 `QWidget.grab()` 做离屏渲染（README 顶部那张效果图就是这么出的）。

---

## ⚠️ 已知限制

- **只在 Windows 上验证过**（音效走 MCI、穿透走 `WS_EX_TRANSPARENT`，都是 Win32）。
- 形象是静态图，没有眨眼 / 呼吸动画（插件本体也是静态图 + 动态气泡）。
- 屏幕全屏游戏 / 视频会盖住她（系统级置顶行为，任何置顶窗口都一样）。
- 便携版未签名，首次运行可能有 SmartScreen 提示。
- 如果 DSH 正开着，页面右下角那个余额挂件会和她重叠；两个是同款形象，
  建议把其中一个拖开，或者干脆用这个独立版、把 DSH 里的挂件关掉。

---

## 🤝 参与 / 反馈

- 提 Bug、想要新功能：开 [Issue](../../issues)
- 改代码：欢迎 PR。动手前建议先通读 `whale_pet.py` 的模块文档字符串 ——
  窗口渲染、托盘事件、DPI 处理与音频实现的约束都写在那里。
- **作者**：[wo-atmy](https://github.com/wo-atmy)
- **个人项目开发交流 QQ**：`3982885755`

如果这只小鲸鱼让你的屏幕角落热闹了一点，给个 ⭐ 就是最好的支持。

---

## 📄 许可

本项目以 **MIT 许可**发布，全文见 [LICENSE](LICENSE)。

```
Copyright (c) 2025 wo-atmy
```

第三方组件与素材的授权情况见 [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md)。

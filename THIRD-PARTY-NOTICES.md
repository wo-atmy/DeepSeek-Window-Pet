# 第三方声明 / Third-Party Notices

本文件说明**本仓库里哪些东西是谁的**、各自适用什么协议。二次分发前请先读一遍。

---

## 1. 代码 —— MIT

`whale_pet.py`、`tools/` 下的全部脚本、`build.bat` / `start-pet.bat` /
`stop-pet.bat`、`lines.json` 的台词、以及 `docs/` 下的文档，均为 **wo-atmy 原创**，
以 **MIT 许可**发布，全文见 [LICENSE](LICENSE)。

```
Copyright (c) 2025 wo-atmy
```

## 2. 随代码生成的素材 —— MIT

以下素材由仓库内的脚本**用代码合成**，不含任何第三方内容，随仓库一并按 MIT 发布，
可自由修改与再分发：

| 路径 | 内容 | 生成脚本 |
|---|---|---|
| `assets/sounds/default/` | 两声合成提示音（press / release） | `tools/make_placeholder_assets.py` |
| `app.ico` | 由当前默认形象裁切生成的多尺寸图标 | `tools/make_icon.py` |

`tools/make_placeholder_assets.py` 在 `assets/skins/` 为空时还会补一个占位角色，
以便在没有任何形象素材的情况下程序仍能启动。

---

## 3. 角色形象 `assets/skins/DSniang/` 与 `docs/images/hero.png` —— **二次创作，不在 MIT 范围内**

仓库自带的角色形象（`assets/skins/DSniang/char.png`、`bubble.png`，
以及 README 顶部用的宣传图 `docs/images/hero.png`）是**基于上游插件的角色形象
二次创作的衍生作品（二创图）**，不是本项目原创，也**不包含在 MIT 许可范围内**。

- **原作者**：上游插件 `DeepSeek-Balance-Whale-Widget` 的角色形象作者
- **状态**：衍生作品，本项目作者不持有该形象的全部权利，**无法授予再许可**
- **使用范围**：仅作为本项目的默认示例形象与展示图随仓库提供

因此：

- ✅ 本项目的**代码**部分（第 1、2 节）可以自由使用、修改、按 MIT 再分发。
- ⚠️ **角色形象本身不在 MIT 内**。如果这个形象不是你画的，请勿将其视为可自由
  再分发的素材，也不要在商业场合使用。
- 🔁 准备正式发布或商用前，建议把 `assets/skins/DSniang/` 和
  `docs/images/hero.png` 换成**你有完整权利**的作品。
  替换方式见 README 的「换形象」一节，程序代码不受影响。

> 如果你是这个角色的原作者，或认为本仓库的使用侵犯了你的权利，请通过
> README 中的联系方式告知，我们会立即移除相关文件。

---

## 4. 参考的上游项目 —— DeepSeek-Balance-Whale-Widget

本项目的**视觉参数**参考了：

- **项目**：[MeteorNOX/DeepSeek-Balance-Whale-Widget](https://github.com/MeteorNOX/DeepSeek-Balance-Whale-Widget)
- **协议**：MIT
- **参考范围**：气泡 SVG 形状、形象摆放比例（59.45% 贴右下角）、
  配色（`#FFFFFF` / `#203170` / `#536ba9`）、字号换算（`66u`）、
  设置面板样式（底色 / 描边 / 圆角 / 阴影）、贴左镜像的实现思路。
  这些数值取自该插件 `0.3.17` 版的 `assets/whale-widget.js`。

**本项目没有复制该插件的源代码**，只是按 MIT 允许的方式参考了其视觉参数并独立实现
（Python + PySide6 绘制，而非原插件的 HTML/CSS/SVG）。
按 MIT 的要求，在此保留其版权声明：

```
MIT License — Copyright (c) MeteorNOX
https://github.com/MeteorNOX/DeepSeek-Balance-Whale-Widget/blob/main/LICENSE
```

> ⚠️ 如果你把本项目的实现方式回移进上游插件，或反过来复制上游代码，
> 请同时保留上游的 LICENSE 与版权声明。

---

上面提到的角色形象版权归**上游项目作者**，本仓库对它的使用属于二次创作与展示用途，
不改变其原有权利归属，也**不授予任何再许可**。使用本项目代码时，请把形象素材与代码分开看待。

---

## 5. 上游插件的美术素材 —— **不在 MIT 范围内**

上游插件仓库里的 `PROVENANCE.md` 明确声明：

> `assets/` 下的美术素材（图片 / 动图 / 音效）**不在 MIT 覆盖范围内**，
> 仅供运行该插件使用，**不授予再许可（no sublicense）**。

本仓库对此的处理：

| 素材 | 在本仓库里 | 说明 |
|---|---|---|
| 原插件的音效（`Ya1.mp3` / `D1.mp3` 等） | ❌ **不包含** | 无法再分发，已用合成音效替代 |
| 原插件的代码 | ❌ **不包含** | 本项目为独立实现 |

- ✅ 本仓库 clone 下来就能跑，`assets/sounds/default/` 里的合成音效可以随便用、随便改。
- ✅ 你想换成原插件那套音效**给自己用**，没问题 —— 自己从插件里拷贝即可，
  那是你本地的事，不会进这个仓库。
- ❌ **不要**把原插件的音效或未授权的形象素材打进 Release 压缩包再对外分发。

---

## 6. 运行依赖 —— PySide6

打包 / 运行时使用的 Qt for Python（PySide6）采用
**LGPL v3 / 商业双许可**，版权归 The Qt Company 所有。
本仓库不包含 PySide6 的二进制文件；Release 里的便携版**内含**其运行时，
分发时请遵守 LGPL v3 的要求（保留许可文本、允许替换该库）。

- 许可说明：https://www.qt.io/licensing/
- LGPL v3 全文：https://www.gnu.org/licenses/lgpl-3.0.html

Python 本身（PSF License）与 PyInstaller（GPL v2 + 例外条款）同理，
均只在打包产物中出现，不在本仓库源码中。

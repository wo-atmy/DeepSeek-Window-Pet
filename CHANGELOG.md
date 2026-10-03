# 更新日志

本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [1.0.0] — 首个公开发布

第一次整理成可以放到 GitHub 上的版本。

### 桌宠本体

- 小鲸鱼蹲在屏幕角落，按可调频率随机冒怪话（自带 75 条）
- 按下 / 松开双音效，单击 Q 弹 + 回嘴（自带 15 条），双击立刻冒一句
- 拖拽 + 松手吸附屏幕边缘，位置会记住
- **贴左自动水平镜像**：形象和气泡翻转，**台词文字仍正着读**
- 托盘图标左键 / 右键都直接开设置面板（无二级菜单）
- 在她身上点右键无反应 —— 设置入口刻意只留在托盘

### 设置面板

- 说一句 / 说话频率（闭嘴·安静·正常·话多·话痨）/ 大小滑块（180~460 px）
- 形象切换（扫描 `assets/skins/`）/ 音效切换 + 试听 + 音量滑块
- 总在最前 / 锁定位置 / 鼠标穿透 / 形象目录 / 音效目录
- 编辑台词 / 重载台词 / 回到右下角 / 显示·隐藏 / 退出
- 全部设置持久化到同目录 `config.json`，删掉即恢复出厂

### 独立性

- **不联网、不读余额、不接 AI**：代码里没有任何 HTTP / socket / API 调用
- 只认自己目录下的 `assets/`，不扫描任何外部目录、不复制任何文件
- 不写注册表、不写 AppData、没有开机自启 —— 删掉文件夹什么都不剩

### 打包

- `build.bat` 一键出便携版（PyInstaller `--onedir`），目标电脑不需要 Python
- 排除 QtQml / QtQuick / QtNetwork / QtSql / QtOpenGL 等模块，并删掉 Qt 翻译文件瘦身
- GitHub Actions：打 `v*` tag 自动打包并发布 Release

### 授权

- 代码以 **MIT** 发布，`Copyright (c) 2025 wo-atmy`
- 新增 `THIRD-PARTY-NOTICES.md`，逐项说明协议归属：
  - 参考了 [MeteorNOX/DeepSeek-Balance-Whale-Widget](https://github.com/MeteorNOX/DeepSeek-Balance-Whale-Widget)（MIT）的视觉参数，并保留其版权声明
  - 代码与脚本合成的音频按 MIT 发布
  - 角色形象（`assets/skins/DSniang/`、`docs/images/hero.png`）标注为**二次创作衍生图，不在 MIT 范围内**
  - 上游插件的音效不在 MIT 内，未包含在本仓库
- 便携版压缩包内附带 `LICENSE.txt` 与 `THIRD-PARTY-NOTICES.txt`

### 素材

- 新增 `assets/skins/DSniang/` 作为默认形象，同时用作 README 宣传图
- `assets/sounds/default/` 为脚本合成的原创提示音，可自由替换

### 仓库工程化

- `.gitignore`：运行时文件（`config.json` / `pet.pid`）、打包产物、自检截图不进版本库
- `requirements.txt`：只依赖 `PySide6-Essentials`
- `.bat` 全部改为 ASCII 文件名与 ASCII 内容，中文说明移到 `docs/`
- README 重写为 GitHub 版本，另附 `README.en.md`
- `tools/` 仅保留必要脚本：离屏渲染自检、图标生成、素材重建
- 打包体积优化：剔除 Qt 中未使用的部件，zip 由 34 MB 降至 23 MB

# -*- coding: utf-8 -*-
"""
小鲸鱼桌宠：蹲在屏幕角落、主要功能就是冒怪话。

定位：**它就是个启动器** —— 脱离 DSH、不联网、不读余额、不接 AI；只认自己
目录下的 assets/，不扫描外部目录、不复制文件；不写注册表、不写 AppData、
没有开机自启，删掉文件夹就什么都不剩。

形象与气泡 1:1 复刻 dsh-whale-widget 0.3.17 的视觉参数：形象贴方块右下角、
占 59.45%×59.45%，整块 Q 弹（原点 50% 100%），气泡 SVG viewBox 1026x700、
填充 #FFFFFF、描边 #203170 stroke-width 18，文字 #536ba9、字号 66u；贴左时
整体 scaleX(-1)，文字再翻一次抵消。

音效走 Windows 原生 MCI（ctypes 调 winmm），因此不需要 QtMultimedia。

授权：代码部分为 MIT，Copyright (c) 2025 wo-atmy。第三方代码与素材的授权边界
见 THIRD-PARTY-NOTICES.md：assets/sounds/ 下为合成的原创占位音效；默认角色形象
（assets/skins/DSniang/）为基于上游角色形象的二次创作，不在 MIT 许可范围内。
"""

import ctypes
import json
import os
import random
import sys
import time
import traceback

from PySide6.QtCore import QByteArray, QEvent, QPoint, QRect, QRectF, Qt, QTimer
from PySide6.QtGui import (QColor, QCursor, QFont, QFontMetrics, QIcon,
                           QPainter, QPen, QPixmap)
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QLabel,
                               QMessageBox, QPushButton, QSlider,
                               QSystemTrayIcon, QVBoxLayout, QWidget)

APP_NAME = "WhalePet"

# ---------------------------------------------------------------- 插件样式常量
SVG_W, SVG_H = 1026.0, 700.0          # 气泡 SVG 的 viewBox
CHAR_FRAC = 0.5945                    # 形象占方块的比例（插件 .dshwv-img 的 59.45%）
BUBBLE_SVG = (
    '<svg viewBox="0 0 1026 700" preserveAspectRatio="xMidYMid meet" '
    'xmlns="http://www.w3.org/2000/svg">'
    '<path fill="#FFFFFF" stroke="#203170" stroke-width="18" stroke-linejoin="round" '
    'stroke-linecap="round" d="M 827 248 A 373 232 0 1 0 81 246 A 373 232 0 0 0 301 465 '
    'A 57 32 10 0 0 413 484 A 373 232 0 0 0 827 248 Z"/>'
    '<ellipse cx="352" cy="561" rx="37.5" ry="26" fill="#FFFFFF" stroke="#203170" stroke-width="18"/>'
    '<ellipse cx="442" cy="646" rx="24.5" ry="18" fill="#FFFFFF" stroke="#203170" stroke-width="18"/>'
    '</svg>'
)
NAVY = "#203170"
TEXT_COLOR = "#536ba9"
TEXT_CENTER = (0.4425, 0.36)          # 泡体视觉中心（相对气泡层宽高）
TEXT_BOX = (99.0 / SVG_W, 33.0 / SVG_H, 809.0 / SVG_W, 461.0 / SVG_H)
LABEL_U = 66.0                        # 字号 = LABEL_U * (方块边长 / 1026)

# ---------------------------------------------------------------- 可调项
SIZE_DEFAULT, SIZE_MIN, SIZE_MAX = 300, 180, 460   # 窗口边长（逻辑像素）
# 说话频率档位：(名字, 间隔下限秒, 间隔上限秒)
#   lo == 0 表示该档完全不主动说话（点她、拖她、锁定/穿透的确认提示照旧）。
SPEAK_LEVELS = [
    ("闭嘴", 0, 0),          # 完全不主动冒话
    ("安静", 300, 900),      # 5 ~ 15 分钟
    ("正常", 90, 210),       # 1.5 ~ 3.5 分钟
    ("话多", 30, 70),
    ("话痨", 8, 20),
]
# 从这一档起（含）启动时才主动打招呼；闭嘴 / 安静档不打扰。
GREET_FROM_LEVEL = 2
SPEAK_CFG_VERSION = 2        # 档位表版本，用于把老配置里的索引平移过来

DEFAULT_LINES = ["又摸鱼？我什么都没看见。", "喵。", "别看我，看屏幕。"]
DEFAULT_CLICK_LINES = ["别戳我。", "干嘛？", "我在呢。"]

# 素材组织（形象与音效互相独立，各自随时切换）：
#
#   assets/skins/<形象名>/char.png      纯角色（透明底）—— 只有这张参与渲染
#   assets/skins/<形象名>/bubble.png    含对话框的整图 —— 文件规范 / 参考图
#   assets/skins/<形象名>.png           也接受：一张散图直接当形象
#   assets/sounds/<音效组名>/press.*    按下去响的
#   assets/sounds/<音效组名>/release.*  松开响的
#
# 一个形象两张图沿用插件的约定（DSniang1 = 纯角色裁切图，DSniang02 = 含空白
# 气泡的整图）。渲染只用纯角色那张，气泡由代码画成 SVG，好处是台词多长都能
# 自适应，不会被图片里的固定气泡挤爆；bubble.png 因此只作参考，不参与绘制。
# 往这两个目录丢文件就多一个可选项，不用改代码、不动现有素材。
DEFAULT_SKIN = "DSniang"
DEFAULT_SFX = "default"
CHAR_STEMS = ("char", "character", "角色", "本体")
IMAGE_EXT = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif")
AUDIO_EXT = (".mp3", ".wav", ".m4a", ".ogg", ".aac")

# 程序只认自己目录下的 assets/，不扫描外部目录，也不向外部位置写任何东西。


def app_dir():
    """程序所在目录。

    打包成 exe 后（PyInstaller），`__file__` 指向临时解包目录，而配置/台词/素材
    要跟 exe 放在一起才能"拷到别的电脑直接用"，所以冻结时必须取 exe 自己的目录。
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


ASSETS_DIR = os.path.join(app_dir(), "assets")
SKINS_DIR = os.path.join(ASSETS_DIR, "skins")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
CONFIG_PATH = os.path.join(app_dir(), "config.json")
LINES_PATH = os.path.join(app_dir(), "lines.json")
PID_PATH = os.path.join(app_dir(), "pet.pid")

DEFAULT_CONFIG = {
    "x": None, "y": None,
    "size_px": SIZE_DEFAULT,
    "speak": 1,
    "sound": True,
    "volume": 0.9,
    "sfx": DEFAULT_SFX,        # assets/sounds/ 下的子文件夹名
    "skin": DEFAULT_SKIN,      # assets/skins/ 下的形象文件夹名
    "topmost": True,
    "locked": False,           # 锁定位置：拖不动，但点她照常有反应
    "click_through": False,    # 鼠标穿透：点她等于点在后面的窗口上
    "mirror_left": True,       # 跑到屏幕左半边时自动水平镜像（文字仍正着）
}


# ---------------------------------------------------------------- 小工具
def load_json(path, fallback):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return fallback


def save_json(path, data):
    try:
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
        return True
    except Exception:
        return False


def load_lines():
    data = load_json(LINES_PATH, None)
    lines, clicks = list(DEFAULT_LINES), list(DEFAULT_CLICK_LINES)
    if isinstance(data, dict):
        if isinstance(data.get("lines"), list) and data["lines"]:
            lines = [str(s) for s in data["lines"] if str(s).strip()]
        if isinstance(data.get("click_lines"), list) and data["click_lines"]:
            clicks = [str(s) for s in data["click_lines"] if str(s).strip()]
    elif isinstance(data, list) and data:
        lines = [str(s) for s in data if str(s).strip()]
    return lines, clicks


def ensure_lines_file():
    """首次运行（或拷到新电脑）时，把内置默认台词写成 lines.json，方便用户直接改。"""
    if os.path.exists(LINES_PATH):
        return False
    data = {
        "_说明": "lines = 自己冒出来的怪话；click_lines = 戳它时的回应。"
                 "改完保存，右键菜单点『重新载入台词』即可生效。",
        "lines": list(DEFAULT_LINES),
        "click_lines": list(DEFAULT_CLICK_LINES),
    }
    return save_json(LINES_PATH, data)


def list_skins():
    """扫描 assets/skins/，返回 [(形象名, char 图片路径), ...]，默认形象排最前。

    两种摆法都认：
        skins/DSniang/char.png     ← 推荐：一个形象一个文件夹
        skins/DSniang.png          ← 也行：一张散图直接当形象
    文件夹里找不到 char.* 就跳过（说明这个文件夹不是形象）。
    """
    out = []
    if not os.path.isdir(SKINS_DIR):
        return out
    for entry in sorted(os.listdir(SKINS_DIR)):
        p = os.path.join(SKINS_DIR, entry)
        if os.path.isdir(p):
            for f in sorted(os.listdir(p)):
                stem, ext = os.path.splitext(f)
                if stem.lower() in CHAR_STEMS and ext.lower() in IMAGE_EXT:
                    out.append((entry, os.path.join(p, f)))
                    break
        elif os.path.splitext(entry)[1].lower() in IMAGE_EXT:
            out.append((os.path.splitext(entry)[0], p))
    return sorted(out, key=lambda t: (t[0] != DEFAULT_SKIN, t[0].lower()))


def skin_extra(name):
    """形象文件夹里的附带图（含对话框的那张），只用于展示信息。"""
    d = os.path.join(SKINS_DIR, name)
    if not os.path.isdir(d):
        return ""
    for f in sorted(os.listdir(d)):
        stem, ext = os.path.splitext(f)
        if stem.lower() in CHAR_STEMS:
            continue
        if ext.lower() in IMAGE_EXT:
            return os.path.join(d, f)
    return ""


def resolve_skin(cfg):
    """把 config 里的 skin 解析成 (形象名, 图片路径)。

    只在本程序的 assets/skins/ 里找；找不到就退回列表第一个；
    一个形象都没有就返回空（她就不画形象，只剩下气泡）。
    不去任何外部目录兜底：目录里有什么用什么。
    """
    skins = list_skins()
    want = cfg.get("skin") or ""
    for name, path in skins:
        if name == want:
            return name, path
    if skins:
        return skins[0]
    return "", ""


def find_sound(folder, kind):
    """在音效组目录里找 press.* / release.*（扩展名不限）。"""
    if not os.path.isdir(folder):
        return ""
    for f in sorted(os.listdir(folder)):
        stem, ext = os.path.splitext(f)
        if stem.lower() == kind and ext.lower() in AUDIO_EXT:
            return os.path.join(folder, f)
    return ""


def list_sound_sets():
    """assets/sounds/ 下所有「至少有 press 或 release」的音效组。"""
    if not os.path.isdir(SOUNDS_DIR):
        return []
    out = [d for d in os.listdir(SOUNDS_DIR)
           if os.path.isdir(os.path.join(SOUNDS_DIR, d))
           and (find_sound(os.path.join(SOUNDS_DIR, d), "press")
                or find_sound(os.path.join(SOUNDS_DIR, d), "release"))]
    return sorted(out, key=lambda s: (s != DEFAULT_SFX, s.lower()))


def resolve_sfx_dir(cfg):
    """把 config 里的 sfx 解析成实际音效组目录。"""
    want = cfg.get("sfx") or ""
    if want and os.path.isdir(os.path.join(SOUNDS_DIR, want)):
        return os.path.join(SOUNDS_DIR, want)
    sets = list_sound_sets()
    return os.path.join(SOUNDS_DIR, sets[0]) if sets else ""


def ensure_asset_dirs():
    """确保 assets/skins 和 assets/sounds 两个目录存在，方便用户往里丢文件。

    只做 mkdir：不扫描任何外部目录、不复制任何文件，assets/ 里有什么就用什么。
    """
    os.makedirs(SKINS_DIR, exist_ok=True)
    os.makedirs(SOUNDS_DIR, exist_ok=True)


# ---------------------------------------------------------------- 音效
class Sound:
    """Windows 原生 MCI 播放（零依赖，MP3 / WAV 都行）。

    QtMultimedia 在 PySide6-Essentials 里没有，而 winsound 只能放 WAV，
    所以这里直接用 winmm 的 mciSendString。MP3 支持 setaudio volume，
    WAV(waveaudio) 不支持 —— 失败就忽略，不影响播放。
    """

    def __init__(self, enabled=True, volume=0.9):
        self.enabled = enabled
        self.volume = volume
        self._alias = {}
        self._n = 0

    @staticmethod
    def _mci(cmd):
        try:
            buf = ctypes.create_unicode_buffer(300)
            return ctypes.windll.winmm.mciSendStringW(cmd, buf, 298, None)
        except Exception:
            return 1

    def _open(self, path):
        if path in self._alias:
            return self._alias[path]
        typ = "waveaudio" if path.lower().endswith(".wav") else "mpegvideo"
        alias = "wp_snd_%d" % self._n
        self._n += 1
        if self._mci('open "%s" type %s alias %s' % (path, typ, alias)) != 0:
            self._alias[path] = None
            return None
        self._alias[path] = alias
        return alias

    def play(self, path):
        if not self.enabled or not path or not os.path.exists(path):
            return
        alias = self._open(path)
        if not alias:
            return
        self._mci("setaudio %s volume to %d"
                  % (alias, max(0, min(1000, int(self.volume * 1000)))))
        self._mci("seek %s to start" % alias)
        self._mci("play %s" % alias)


# ==========================================================================
# 右键设置面板 —— 外观沿用余额插件的菜单
# ==========================================================================
# 样式参数取自 dsh-whale-widget 0.3.17 的 assets/whale-widget.js：
#
#   .dshwv-menu   底 rgba(255,255,255,.92)，边 rgba(32,49,112,.35)，圆角 10px，
#                 出现动画 scale(.96) translateY(10px)，origin top right
#   .dshwv-bubsec 分组标题 #9fb0d9，上方边框 rgba(32,49,112,.12)
#   按钮          边 rgba(32,49,112,.4)，底 rgba(32,49,112,.08)，字 #203170
#   选中/主按钮   底 #203170、字 #fff
#   滑块          轨道 rgba(32,49,112,.15)，已填充 rgba(32,49,112,.45)，
#                 手柄 14px 深蓝 + 2px 白边
NAVY_RGB = "32,49,112"
MUTED = "#9fb0d9"

PANEL_QSS = """
QPushButton {
    border: 1px solid rgba(%(n)s,0.4);
    border-radius: 5px;
    background: rgba(%(n)s,0.08);
    color: %(navy)s;
    font-size: 11px;
    padding: 3px 6px;
}
QPushButton:hover   { background: rgba(%(n)s,0.18); }
QPushButton:pressed { background: rgba(%(n)s,0.28); }
QPushButton:checked { background: %(navy)s; color: #ffffff; }
QLabel#sec {
    color: %(muted)s;
    font-size: 11px;
    border-top: 1px solid rgba(%(n)s,0.12);
    padding-top: 6px;
    margin-top: 0px;
}
QLabel#val  { color: %(navy)s; font-size: 11px; }
QLabel#name { color: %(navy)s; font-size: 11px; }
QSlider::groove:horizontal   { height: 4px; background: rgba(%(n)s,0.15); border-radius: 2px; }
QSlider::sub-page:horizontal { height: 4px; background: rgba(%(n)s,0.45); border-radius: 2px; }
QSlider::handle:horizontal {
    width: 11px; height: 11px; margin: -5px 0; border-radius: 6px;
    background: %(navy)s; border: 2px solid #ffffff;
}
""" % {"n": NAVY_RGB, "navy": NAVY, "muted": MUTED}


class PetPanel(QWidget):
    """设置面板。

    刻意不用 `Qt.Popup`：Popup 会自己抢鼠标 grab，在"由鼠标事件触发的那一刻"
    弹出时会被后续事件立刻关掉，表现为面板一闪而过。改用 `Qt.Tool` + 失焦自动
    关闭（与托盘菜单同一套路），行为稳定可预期。
    """

    W_MIN = 196
    W_MAX = 340

    def __init__(self, pet):
        # 面板自己永远置顶：否则用户关掉「总在最前」时，面板会被别的窗口盖住
        super().__init__(None, Qt.Tool | Qt.FramelessWindowHint
                         | Qt.NoDropShadowWindowHint | Qt.WindowStaysOnTopHint)
        self.pet = pet
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet(PANEL_QSS)
        self.setMinimumWidth(self.W_MIN)
        self.setMaximumWidth(self.W_MAX)
        self._build()
        self.adjustSize()

    # 失焦 / 按 Esc 就收起来
    def event(self, e):
        t = e.type()
        if t == QEvent.WindowDeactivate:
            self.close()
            return True
        if t == QEvent.KeyPress and e.key() == Qt.Key_Escape:
            self.close()
            return True
        return super().event(e)

    # ---- 背景：白底半透明 + 深蓝描边 + 圆角 + 阴影 ----
    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        r = QRectF(self.rect()).adjusted(6, 6, -7, -7)
        # 阴影（插件是 box-shadow:0 6px 18px rgba(0,0,0,.18)）
        for i in range(6, 0, -1):
            a = int(10 * (1 - i / 7.0))
            p.setPen(QPen(QColor(0, 0, 0, a), 1))
            p.setBrush(Qt.NoBrush)
            p.drawRoundedRect(r.adjusted(-i, -i + 3, i, i + 3), 10 + i, 10 + i)
        p.setPen(QPen(QColor(32, 49, 112, int(0.35 * 255)), 1))
        p.setBrush(QColor(255, 255, 255, int(0.92 * 255)))
        p.drawRoundedRect(r, 10, 10)

    # ---- 小工具 ----
    def _section(self, text):
        lb = QLabel(text)
        lb.setObjectName("sec")
        return lb

    def _row(self, spacing=6):
        h = QHBoxLayout()
        h.setSpacing(spacing)
        h.setContentsMargins(0, 0, 0, 0)
        return h

    def _toggle(self, text, checked, on_click):
        b = QPushButton(text)
        b.setCheckable(True)
        b.setChecked(bool(checked))
        b.clicked.connect(on_click)
        return b

    def _slider(self, lo, hi, value, on_change):
        s = QSlider(Qt.Horizontal)
        s.setRange(lo, hi)
        s.setValue(int(value))
        s.valueChanged.connect(on_change)
        return s

    def _grid(self, entries, current, on_pick, per_row=3):
        """一排排的可选项按钮（选中态实心深蓝）。
        entries = [(显示文字, 取值)] 或 [(显示文字, 取值, 悬浮提示)]
        """
        g = QGridLayout()
        g.setSpacing(5)
        g.setContentsMargins(0, 0, 0, 0)
        for i, item in enumerate(entries):
            label, value = item[0], item[1]
            t = self._toggle(label, value == current,
                             lambda _=False, v=value: on_pick(v))
            t.setToolTip(item[2] if len(item) > 2 else value)
            g.addWidget(t, i // per_row, i % per_row)
        return g

    def _skin_entries(self):
        """形象按钮列表；带对话框那张图存在的话写进提示里，方便确认文件配对。"""
        out = []
        for name, _path in list_skins():
            extra = skin_extra(name)
            tip = name
            if extra:
                tip += "\n含对话框版：%s" % os.path.basename(extra)
            else:
                tip += "\n（没有含对话框的那张图，用内置 SVG 气泡）"
            out.append((name, name, tip))
        return out

    # ---- 面板内容（尽量紧凑：能并排的并排）----
    def _build(self):
        pet = self.pet
        v = QVBoxLayout(self)
        v.setContentsMargins(14, 12, 14, 12)
        v.setSpacing(5)

        b = QPushButton("说一句")
        b.clicked.connect(lambda: (pet.say(random.choice(pet.lines)), self.close()))
        v.addWidget(b)

        # 说话频率（5 档，网格排一行 3 个）
        v.addWidget(self._section("说话频率"))
        v.addLayout(self._grid(
            [(label, i, ("不主动说话" if lo <= 0 else "每隔 %d~%d 秒冒一句" % (lo, hi)))
             for i, (label, lo, hi) in enumerate(SPEAK_LEVELS)],
            pet.speak_idx(), self._set_speak))

        # 大小（对应插件的「大小滑块」）
        v.addWidget(self._section("大小"))
        row = self._row(5)
        self.size_val = QLabel("%d px" % pet.side())
        self.size_val.setObjectName("val")
        self.size_val.setFixedWidth(42)
        row.addWidget(self._slider(SIZE_MIN, SIZE_MAX, pet.side(), self._on_size_slide))
        row.addWidget(self.size_val)
        v.addLayout(row)

        # 形象：丢进 assets/skins/<名字>/char.png 就能在这里选，和音效互不影响
        v.addWidget(self._section("形象"))
        entries = self._skin_entries()
        if entries:
            v.addLayout(self._grid(entries, pet.skin, pet.set_skin))
        else:
            v.addWidget(self._hint("assets\\skins\\ 里还没有形象"))

        # 音效：丢进 assets/sounds/<名字>/ 就能在这里选
        v.addWidget(self._section("音效"))
        sets = list_sound_sets()
        row = self._row(5)
        row.addWidget(self._toggle("开启", pet.cfg.get("sound", True),
                                   self._toggle_sound))
        row.addWidget(self._btn("试听", pet.audition, close=False))
        v.addLayout(row)
        if sets:
            v.addLayout(self._grid([(s, s) for s in sets],
                                   pet.cfg.get("sfx") or sets[0], self._set_sfx))
        else:
            v.addWidget(self._hint("assets\\sounds\\ 里还没有音效组"))

        row = self._row(5)
        self.vol_val = QLabel("%d%%" % int(float(pet.cfg.get("volume", 0.9)) * 100))
        self.vol_val.setObjectName("val")
        self.vol_val.setFixedWidth(42)
        row.addWidget(self._slider(0, 100, float(pet.cfg.get("volume", 0.9)) * 100,
                                   self._on_vol_slide))
        row.addWidget(self.vol_val)
        v.addLayout(row)

        # 其他：都并排，省竖排空间
        v.addWidget(self._section("其他"))
        row = self._row(5)
        row.addWidget(self._toggle("总在最前", pet.cfg.get("topmost", True),
                                   pet.toggle_topmost))
        row.addWidget(self._toggle("锁定位置", pet.cfg.get("locked", False),
                                   pet.toggle_locked))
        row.addWidget(self._toggle("鼠标穿透", pet.cfg.get("click_through", False),
                                   pet.toggle_click_through))
        v.addLayout(row)

        row = self._row(5)
        row.addWidget(self._btn("形象目录", pet.open_skin_dir, close=False))
        row.addWidget(self._btn("音效目录", pet.open_sound_dir, close=False))
        row.addWidget(self._btn("编辑台词", pet.edit_lines, close=False))
        v.addLayout(row)

        row = self._row(5)
        row.addWidget(self._btn("重载台词", pet.reload_lines, close=False))
        row.addWidget(self._btn("回到右下角", pet.reset_pos))
        row.addWidget(self._btn("显示/隐藏", pet.toggle_visible))
        v.addLayout(row)

        row = self._row(5)
        row.addWidget(self._btn("退出", pet.quit))
        v.addLayout(row)

    def _hint(self, text):
        lb = QLabel(text)
        lb.setObjectName("sec")
        return lb

    def _btn(self, text, fn, close=True):
        """close=True 时点完就收起面板（改了状态、要立刻看到效果的按钮用 False）。"""
        b = QPushButton(text)
        if close:
            b.clicked.connect(lambda _=False: (fn(), self.close()))
        else:
            b.clicked.connect(lambda _=False: fn())
        return b

    # ---- 各项操作（改完就地刷新面板）----
    def _set_speak(self, i):
        self.pet.set_speak(i)
        self._rebuild()

    def _on_size_slide(self, val):
        self.size_val.setText("%d px" % val)
        self.pet.set_size_px(val)

    def _on_vol_slide(self, val):
        self.vol_val.setText("%d%%" % val)
        self.pet.cfg["volume"] = val / 100.0
        save_json(CONFIG_PATH, self.pet.cfg)

    def _toggle_sound(self):
        self.pet.toggle_sound()
        self._rebuild()

    def _set_sfx(self, key):
        self.pet.set_sfx(key)
        self._rebuild()

    def _rebuild(self):
        """状态变了就重建内容。

        必须延到事件循环下一轮再做：调用方正是被销毁的那个按钮的信号处理函数，
        当场销毁自己会让 Qt 崩掉。
        """
        QTimer.singleShot(0, self._do_rebuild)

    def _do_rebuild(self):
        try:
            w = self.width()
            old = self.layout()
            if old is not None:
                QWidget().setLayout(old)      # 把旧布局交给临时对象，随之销毁
            self._build()
            self.adjustSize()
            self.resize(max(w, self.width()), self.height())
        except RuntimeError:
            pass                              # 面板已经关掉了

    # ---- 定位：贴着鼠标光标弹出（和系统托盘菜单一样）----
    def popup_at_cursor(self):
        """在光标上方展开，并夹进屏幕可用区内。

        可用区（availableGeometry）已经排除了任务栏，所以从托盘图标点开时
        面板会自然落在任务栏上方，而不是飘到桌宠那边去。
        """
        self.adjustSize()
        c = QCursor.pos()
        scr = QApplication.screenAt(c) or QApplication.primaryScreen()
        a = scr.availableGeometry()
        w, h = self.width(), self.height()

        x = c.x() - w + 20          # 往左展开，右下角点开时不会顶出屏幕
        y = c.y() - h - 10          # 往上展开
        if y < a.top() + 2:         # 上面放不下就翻到光标下方
            y = c.y() + 10
        x = max(a.left() + 2, min(x, a.right() - w - 2))
        y = max(a.top() + 2, min(y, a.bottom() - h - 2))
        self.move(int(x), int(y))
        self.show()
        self.raise_()
        self.activateWindow()      # 拿焦点，才能靠"失焦"自动关闭


# ==========================================================================
# 桌宠窗口
# ==========================================================================

class WhalePet(QWidget):
    def __init__(self):
        super().__init__()
        raw = load_json(CONFIG_PATH, {}) or {}
        self.cfg = dict(DEFAULT_CONFIG)
        self.cfg.update(raw)

        # 档位表改过（新增「闭嘴」并整体拉长间隔），老配置里的索引要平移一位，
        # 否则「正常」会被解释成「安静」、与用户当初选的档位不符。
        #
        # 判据必须是 `raw and "speak_v" not in raw`：全新安装时 raw 是空字典，
        # "speak_v" 当然也不在里面 —— 少了 `raw` 这个条件，全新安装也会被平移，
        # 默认档位就从「安静」变成「正常」。
        if raw and "speak_v" not in raw:
            self.cfg["speak"] = min(int(self.cfg.get("speak", 1)) + 1,
                                    len(SPEAK_LEVELS) - 1)
        self.cfg["speak_v"] = SPEAK_CFG_VERSION

        self.lines, self.click_lines = load_lines()

        self.skin, self.char_path = resolve_skin(self.cfg)
        self.char_pix = QPixmap()
        self.bubble_renderer = QSvgRenderer(QByteArray(BUBBLE_SVG.encode("utf-8")))
        self.bubble_cache = None
        self.bubble_cache_key = None

        self.sound = Sound(bool(self.cfg.get("sound", True)),
                           float(self.cfg.get("volume", 0.9)))

        # 动画状态
        self.sq = [1.0, 1.0]
        self.sq_v = [0.0, 0.0]
        self.sq_target = [1.0, 1.0]
        self.bubble_t = 0.0
        self.bubble_dir = 0
        self.speaking = False
        self._msg = ""

        self._drag = None
        self._press_gp = QPoint()
        self._moved = 0

        self._setup_window()
        self._setup_timers()
        self._load_char()
        self._restore_geometry()
        self._write_pid()

        # 按记住的档位排第一句（「闭嘴」档不会排）
        self.schedule_talk()

    # ------------------------------------------------------------ 窗口
    def _setup_window(self):
        self.setWindowTitle(APP_NAME)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setWindowIcon(self._make_icon())
        self.apply_window_flags()

    def apply_window_flags(self):
        """把 config.json 里记住的三个窗口标志类设置一次性生效。

        注意：topmost / click_through 必须在这里统一读配置，不能写死：窗口标志
        只在 _setup_window() 里应用一次，硬编码会造成"关掉置顶 → 重启又变回开"。
        其余设置各有各的生效点（都在 __init__ 里）：
              x / y / size_px      → _restore_geometry()
              skin                 → _load_char()（resolve_skin 已读 cfg）
              sfx / volume / sound → Sound 实例 + play_sfx() / sfx_path()
              speak                → speak_idx() → schedule_talk()
              locked               → mouseMoveEvent() / mouseReleaseEvent()
        """
        flags = Qt.FramelessWindowHint | Qt.Tool
        if self.cfg.get("topmost", True):
            flags |= Qt.WindowStaysOnTopHint
        if self.cfg.get("click_through", False):
            flags |= Qt.WindowTransparentForInput
        self.setWindowFlags(flags)

    def _make_icon(self):
        pm = QPixmap(self.char_path) if self.char_path else QPixmap()
        if pm.isNull():
            pm = QPixmap(64, 64)
            pm.fill(QColor(NAVY))
        return QIcon(pm.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def side(self):
        return max(SIZE_MIN, min(SIZE_MAX, int(self.cfg.get("size_px", SIZE_DEFAULT))))

    def speak_idx(self):
        return int(self.cfg.get("speak", 1)) % len(SPEAK_LEVELS)

    def auto_speaks(self):
        """当前档位会不会主动冒话（「闭嘴」档不会）。"""
        return SPEAK_LEVELS[self.speak_idx()][1] > 0

    def bubble_layer_h(self):
        return int(round(self.side() * SVG_H / SVG_W))

    def _load_char(self):
        self.char_pix = QPixmap(self.char_path) if self.char_path else QPixmap()

    def _restore_geometry(self):
        """按上次记住的设置摆好她（位置 / 大小 / 形象 / 音效等都来自 config.json）。"""
        s = self.side()
        self.resize(s, s)
        x, y = self.cfg.get("x"), self.cfg.get("y")
        if x is None or y is None:
            self._move_default()
        else:
            self.move(int(x), int(y))
        self.bubble_cache = None
        # 首次运行就把 config.json 落盘：这样从这一刻起"记忆"就是完整的，
        # 用户也能立刻在文件夹里看到这个可编辑的配置文件。
        self._save_pos()

    def _work_area(self):
        scr = self.screen() or QApplication.primaryScreen()
        return scr.availableGeometry()

    def _move_default(self):
        a = self._work_area()
        self.move(a.right() - self.width() - 8, a.bottom() - self.height() - 8)

    def _clamp(self, x, y):
        a = self._work_area()
        x = max(a.left() - 4, min(int(x), a.right() - self.width() + 4))
        y = max(a.top() - 4, min(int(y), a.bottom() - self.height() + 4))
        return x, y

    # ------------------------------------------------------------ 定时器
    def _setup_timers(self):
        self.talk_timer = QTimer(self)
        self.talk_timer.setSingleShot(True)
        self.talk_timer.timeout.connect(self.auto_talk)

        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide_bubble)

        self.anim = QTimer(self)
        self.anim.setInterval(16)
        self.anim.timeout.connect(self._tick)
        self.anim.start()
        self._last = None

    def _tick(self):
        now = time.perf_counter()
        dt = 0.016 if self._last is None else min(0.05, now - self._last)
        self._last = now

        k, damp = 220.0, 22.0
        moving = False
        for i in range(2):
            v = self.sq_v[i] + ((self.sq_target[i] - self.sq[i]) * k - self.sq_v[i] * damp) * dt
            s = self.sq[i] + v * dt
            self.sq_v[i], self.sq[i] = v, s
            if abs(v) > 1e-3 or abs(self.sq_target[i] - s) > 1e-3:
                moving = True
        if abs(self.sq[0] - 1.0) < 1e-3 and abs(self.sq[1] - 1.0) < 1e-3 and not moving:
            self.sq = [1.0, 1.0]
            self.sq_v = [0.0, 0.0]

        if self.bubble_dir:
            self.bubble_t = min(1.0, max(0.0, self.bubble_t + self.bubble_dir * dt / 0.18))
            if self.bubble_t in (0.0, 1.0):
                self.bubble_dir = 0
        elif self.bubble_t in (0.0, 1.0) and not moving:
            return
        self.update()

    # ------------------------------------------------------------ 说话
    def say(self, text, ms=6500):
        self._msg = text
        self.speaking = True
        self.bubble_dir = 1
        self.update()
        self.hide_timer.start(ms)

    def hide_bubble(self):
        self.speaking = False
        self.bubble_dir = -1
        self.update()

    def auto_talk(self):
        if not self.speaking:
            self.say(random.choice(self.lines))
        self.schedule_talk()

    def schedule_talk(self):
        """排下一句；「闭嘴」档（lo<=0）直接不排。"""
        _, lo, hi = SPEAK_LEVELS[self.speak_idx()]
        if lo <= 0:
            self.talk_timer.stop()
            return
        self.talk_timer.start(random.randint(lo, hi) * 1000)

    def reschedule_talk(self):
        """用户改了档位：立刻按新档位重排。"""
        self.talk_timer.stop()
        self.schedule_talk()

    # ------------------------------------------------------------ 音效
    def sfx_path(self, which):
        d = resolve_sfx_dir(self.cfg)
        return find_sound(d, "press" if which == "press" else "release") if d else ""

    def play_sfx(self, which):
        self.sound.enabled = bool(self.cfg.get("sound", True))
        self.sound.volume = float(self.cfg.get("volume", 0.9))
        self.sound.play(self.sfx_path(which))

    # ------------------------------------------------------------ 绘制
    def is_mirrored(self):
        """她跑到屏幕左半边时自动水平镜像。

        对应插件的 `.dshwv-left`：贴左吸附时整体 `scaleX(-1)`，再给文字单独
        `scaleX(-1)` 抵消回来 —— 图形和气泡翻，文字仍然正着读。
        这里用"中心点落在工作区左半边"判定；config.json 里 `mirror_left: false`
        可关闭。
        """
        if not self.cfg.get("mirror_left", True):
            return False
        a = self._work_area()
        return (self.x() + self.width() / 2.0) < (a.left() + a.right()) / 2.0

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setRenderHint(QPainter.SmoothPixmapTransform, True)

        w, h = self.width(), self.height()
        dpr = self.devicePixelRatioF()
        mirror = self.is_mirrored()
        bh = self.bubble_layer_h()

        # 整块（形象 + 气泡）一起做 Q 弹，原点 = 底部中心（对应 .dshwv-body 的
        # transform-origin: 50% 100%）
        p.save()
        p.translate(w / 2.0, float(h))
        p.scale(self.sq[0], self.sq[1])
        p.translate(-w / 2.0, -float(h))

        # 水平镜像：绕窗口竖向中线翻，形象和气泡图形都跟着翻
        # （气泡翻过去后尾巴朝向另一侧，仍然指着她）
        if mirror:
            p.translate(float(w), 0.0)
            p.scale(-1.0, 1.0)

        # ---- 形象：贴右下角，只占 59.45%（对应 .dshwv-img 的 right/bottom/59.45%）
        #      透明像素在 Windows 上会穿透鼠标，所以可点的只有她的实心轮廓；
        #      设置入口在托盘，她身上能左键点她 / 拖她就够了。
        if not self.char_pix.isNull():
            cw = max(1, int(round(w * CHAR_FRAC)))
            ch = max(1, int(round(h * CHAR_FRAC)))
            pm = self.char_pix.scaled(int(cw * dpr), int(ch * dpr),
                                      Qt.KeepAspectRatio, Qt.SmoothTransformation)
            pm.setDevicePixelRatio(dpr)
            dw, dh = pm.width() / dpr, pm.height() / dpr
            p.drawPixmap(w - dw, h - dh, pm)

        # ---- 气泡（只画图形，文字稍后单独画）
        if self.bubble_t > 0.001:
            p.setOpacity(self.bubble_t)
            pm = self._bubble_pixmap(int(w * dpr), int(bh * dpr), dpr)

            # 出现时从 scale(.7) 放大到 1，绕泡体视觉中心
            sc = 0.7 + 0.3 * self.bubble_t
            cx, cy = TEXT_CENTER[0] * w, 0.353 * bh
            p.save()
            p.translate(cx, cy)
            p.scale(sc, sc)
            p.translate(-cx, -cy)
            p.drawPixmap(0, 0, pm)
            p.restore()

        p.restore()

        # ---- 文字：在正常坐标系里画，只把位置镜像过去（等价于插件"整体
        #      flip 后文字再 flip 一次抵消"），字形永远正着。
        if self.bubble_t > 0.001 and self._msg:
            p.save()
            p.setOpacity(self.bubble_t)
            self._draw_text(p, w, bh, mirrored=mirror)
            p.restore()

    def _bubble_pixmap(self, pw, ph, dpr):
        key = (pw, ph)
        if self.bubble_cache is not None and self.bubble_cache_key == key:
            return self.bubble_cache
        pm = QPixmap(pw, ph)
        pm.fill(Qt.transparent)
        pp = QPainter(pm)
        pp.setRenderHint(QPainter.Antialiasing, True)
        self.bubble_renderer.render(pp, QRectF(0, 0, pw, ph))
        pp.end()
        pm.setDevicePixelRatio(dpr)
        self.bubble_cache, self.bubble_cache_key = pm, key
        return pm

    def _draw_text(self, p, w, bh, mirrored=False):
        """画台词。

        mirrored=True 时只把文字中心镜像到另一边（气泡已经翻过去了），字形本身
        不翻 —— 等价于插件里"整体 scaleX(-1) 后文字再 scaleX(-1) 抵消"。
        """
        box = QRectF(TEXT_BOX[0] * w, TEXT_BOX[1] * bh,
                     (TEXT_BOX[2] - TEXT_BOX[0]) * w,
                     (TEXT_BOX[3] - TEXT_BOX[1]) * bh)
        cx, cy = TEXT_CENTER[0] * w, TEXT_CENTER[1] * bh
        if mirrored:
            cx = w - cx

        flags = int(Qt.AlignCenter) | int(Qt.TextWordWrap)
        size, f = max(11.0, LABEL_U * w / SVG_W), None
        for _ in range(14):
            f = QFont("Microsoft YaHei UI")
            f.setPixelSize(max(9, int(round(size))))
            f.setWeight(QFont.DemiBold)
            fm = QFontMetrics(f)
            need = fm.boundingRect(box.toRect(), flags, self._msg)
            if need.height() <= box.height() and need.width() <= box.width():
                break
            size *= 0.92
        p.setFont(f)
        p.setPen(QPen(QColor(TEXT_COLOR)))
        p.drawText(QRectF(cx - box.width() / 2.0, cy - box.height() / 2.0,
                          box.width(), box.height()), flags, self._msg)

    # ------------------------------------------------------------ 交互
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            gp = e.globalPosition().toPoint()
            self._press_gp = gp
            self._drag = gp - self.frameGeometry().topLeft()
            self._moved = 0
            self.sq_target = [1.10, 0.90]
            self.play_sfx("press")          # 按压音效
            self.update()
        # 右键不在这里处理：设置入口只留托盘，见 mouseReleaseEvent 的说明。

    def mouseMoveEvent(self, e):
        if self._drag is None or not (e.buttons() & Qt.LeftButton):
            return
        gp = e.globalPosition().toPoint()
        # _moved 照常累计：锁定时虽然不移动，但拖动也不该被当成点击
        self._moved = (gp - self._press_gp).manhattanLength()
        if not self.cfg.get("locked", False):
            self.move(gp - self._drag)

    def mouseReleaseEvent(self, e):
        # 右键刻意不绑任何东西：设置入口只留托盘图标（左键点托盘直接开面板，
        # 右键点托盘走面板），在她身上按右键不会有任何反应，避免随手点到就弹面板。
        if e.button() != Qt.LeftButton:
            return
        dragged = self._moved
        self._drag = None
        self.sq_target = [1.0, 1.0]
        self.play_sfx("release")            # 松开音效
        self.update()
        if dragged < 6:
            self.click_react()
        elif not self.cfg.get("locked", False):
            self._snap()
            self._save_pos()

    def click_react(self):
        self.sq[0], self.sq[1] = 1.06, 0.94
        self.say(random.choice(self.click_lines), ms=4200)

    def _snap(self):
        a = self._work_area()
        x, y, s = self.x(), self.y(), 24
        if abs(x - a.left()) <= s:
            x = a.left() + 4
        if abs((x + self.width()) - a.right()) <= s:
            x = a.right() - self.width() - 4
        if abs((y + self.height()) - a.bottom()) <= s:
            y = a.bottom() - self.height() - 4
        if abs(y - a.top()) <= s:
            y = a.top() + 4
        x, y = self._clamp(x, y)
        self.move(x, y)

    def _save_pos(self):
        self.cfg["x"], self.cfg["y"] = self.x(), self.y()
        save_json(CONFIG_PATH, self.cfg)

    # ------------------------------------------------------------ 设置面板
    def _popup(self, _gpos=None):
        """唤出设置面板。

        位置跟着鼠标光标走 —— 从托盘图标点开时贴在任务栏上方（跟系统托盘菜单
        一样），右键桌宠点开时就出现在她旁边。
        """
        old = getattr(self, "panel", None)
        if old is not None:
            try:
                old.close()
            except RuntimeError:
                pass
        self.panel = PetPanel(self)
        self.panel.popup_at_cursor()

    def show_pet(self):
        self.show()
        self.raise_()

    def toggle_visible(self):
        """显示 / 隐藏她。

        做成开关式：隐藏后没有别的显示入口（设置面板随隐藏一起收起）。
        """
        if self.isVisible():
            self.hide()
        else:
            self.show_pet()

    # ---- 锁定位置 / 鼠标穿透 ----
    def toggle_locked(self):
        self.cfg["locked"] = not bool(self.cfg.get("locked", False))
        save_json(CONFIG_PATH, self.cfg)
        self.say("位置已锁定，拖不动了。" if self.cfg["locked"]
                 else "位置解锁，可以拖了。", ms=3000)

    def toggle_click_through(self):
        self.cfg["click_through"] = not bool(self.cfg.get("click_through", False))
        save_json(CONFIG_PATH, self.cfg)
        self.apply_click_through()
        if self.cfg["click_through"]:
            self.say("鼠标穿透已开：现在点她会点到后面的窗口。"
                     "要关掉，点托盘图标 → 「鼠标穿透」再点一次。", ms=7000)

    def apply_click_through(self):
        self.apply_window_flags()
        self.show()          # 改窗口标志后必须重新显示才生效

    # ---- 对外接口：面板与托盘菜单都调这些 ----
    def set_speak(self, i):
        self.cfg["speak"] = i
        save_json(CONFIG_PATH, self.cfg)
        self.reschedule_talk()          # 改完立刻生效，不等旧定时器到点

    def set_size_px(self, px):
        """滑块连续调大小，保持形象的底部中心不跳。"""
        px = max(SIZE_MIN, min(SIZE_MAX, int(px)))
        if px == self.side():
            return
        bx, by = self.x() + self.width() / 2.0, self.y() + self.height()
        self.cfg["size_px"] = px
        self.resize(px, px)
        self.bubble_cache = None
        self.move(int(bx - px / 2.0), int(by - px))
        save_json(CONFIG_PATH, self.cfg)
        self.update()

    def set_sfx(self, key):
        self.cfg["sfx"] = key
        self.cfg["sound"] = True
        save_json(CONFIG_PATH, self.cfg)
        self.audition()

    def toggle_sound(self):
        self.cfg["sound"] = not bool(self.cfg.get("sound", True))
        save_json(CONFIG_PATH, self.cfg)
        if self.cfg["sound"]:
            self.audition()

    def audition(self):
        self.cfg["sound"] = True
        play = self.play_sfx
        play("press")
        QTimer.singleShot(260, lambda: play("release"))

    def toggle_topmost(self):
        self.cfg["topmost"] = not bool(self.cfg.get("topmost", True))
        save_json(CONFIG_PATH, self.cfg)
        self.apply_window_flags()
        self.show()

    # ---- 形象：丢进 assets/skins/ 就多一个选项，随时切、不影响音效 ----
    def set_skin(self, name):
        path = ""
        for n, p in list_skins():
            if n == name:
                path = p
                break
        if not path:
            return
        self.cfg["skin"] = name
        self.skin = name
        self.char_path = path
        self._load_char()
        self.bubble_cache = None
        self.setWindowIcon(self._make_icon())
        save_json(CONFIG_PATH, self.cfg)
        self.update()

    def open_skin_dir(self):
        self._open_dir(SKINS_DIR)

    def open_sound_dir(self):
        self._open_dir(SOUNDS_DIR)

    def _open_dir(self, path):
        os.makedirs(path, exist_ok=True)
        try:
            os.startfile(path)
        except Exception:
            QMessageBox.information(self, APP_NAME, "目录：\n" + path)

    def edit_lines(self):
        try:
            os.startfile(LINES_PATH)
        except Exception:
            QMessageBox.information(self, APP_NAME, "台词文件：\n" + LINES_PATH)

    def reload_lines(self):
        self.lines, self.click_lines = load_lines()

    def reset_pos(self):
        self._move_default()
        self._save_pos()

    def quit(self):
        self._save_pos()            # 退出前再落一次盘，保证"记住上次的设置"
        try:
            if os.path.exists(PID_PATH):
                os.remove(PID_PATH)  # 清掉 pid，做到"删文件夹就啥也不剩"
        except Exception:
            pass
        QApplication.quit()

    def closeEvent(self, e):
        """被别人关掉窗口（而不是走菜单退出）时，也把设置存一下。"""
        try:
            self._save_pos()
        except Exception:
            pass
        super().closeEvent(e)

    def _write_pid(self):
        try:
            with open(PID_PATH, "w", encoding="utf-8") as f:
                f.write(str(os.getpid()))
        except Exception:
            pass


# ==========================================================================
# 入口
# ==========================================================================

def setup_tray(pet, app):
    """建托盘图标并把"左键 / 右键都直接开设置面板"接上。返回托盘对象（没托盘则 None）。

    独立成函数，便于在不启动完整应用的情况下单独验证托盘事件接线。
    """
    if not QSystemTrayIcon.isSystemTrayAvailable():
        return None

    tray = QSystemTrayIcon(pet.windowIcon(), app)
    tray.setToolTip("小鲸鱼桌宠 —— 左键 / 右键都打开设置")

    # 刻意不调用 setContextMenu()：Qt 的规则是"设了 context menu 就不再发
    # Context 事件"，那样右键只会弹一个菜单、没法直接开设置面板。这里左右键都
    # 直接开面板，退出 / 显示隐藏 / 各项开关都收在面板里，不设菜单不会丢入口。

    def on_tray(reason):
        if reason in (QSystemTrayIcon.Trigger,       # 左键单击
                      QSystemTrayIcon.Context,       # 右键单击
                      QSystemTrayIcon.DoubleClick):
            pet._popup()

    tray.activated.connect(on_tray)
    tray.show()
    pet._tray = tray
    return tray


def main():
    ensure_asset_dirs()             # 只建目录，不扫外部、不搬素材
    ensure_lines_file()

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setQuitOnLastWindowClosed(False)

    pet = WhalePet()
    pet.show()
    pet.raise_()
    pet.apply_click_through()       # 上次退出时开着穿透的话，这次也照旧
    # 启动打招呼也看档位：闭嘴 / 安静档不打扰。
    if pet.speak_idx() >= GREET_FROM_LEVEL:
        QTimer.singleShot(1200, lambda: pet.say(random.choice(pet.lines)))

    setup_tray(pet, app)

    sys.exit(app.exec())


if __name__ == "__main__":
    try:
        main()
    except Exception:
        try:
            _a = QApplication(sys.argv)
            QMessageBox.critical(None, APP_NAME, "桌宠启动失败：\n\n" + traceback.format_exc()[-1500:])
        except Exception:
            sys.stderr.write(traceback.format_exc())

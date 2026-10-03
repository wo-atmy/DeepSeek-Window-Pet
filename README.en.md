<h1 align="center">🐋 DeepSeek-Window-Pet</h1>

<p align="center">
  <b>A Windows desktop pet that sits in a corner of your screen and occasionally says something weird</b>
</p>

<p align="center">
  <img src="docs/images/hero.png" width="360" alt="DeepSeek-Window-Pet character">
</p>

<p align="center">
  A Python + PySide6 desktop pet — the whale from the DSH balance widget,
  spun off into a standalone "Bongo Cat"-style pet.
</p>

<p align="center">
  <b>Offline · no balance reading · no AI · no registry writes · no AppData · no autostart</b><br>
  Delete the folder and nothing is left behind.
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-203170.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/platform-Windows%2010%20%2F%2011%20x64-0078D4.svg" alt="Platform: Windows 10/11 x64">
  <img src="https://img.shields.io/badge/python-3.9%2B-3776AB.svg" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/GUI-PySide6-41CD52.svg" alt="PySide6">
</p>

---

<p align="center">
  <img src="docs/images/pet-demo.png" width="820" alt="Whale pet with speech bubble, four line lengths plus the mirrored case">
</p>

<p align="center">
  <sub>Rendered offscreen by <code>tools/selftest.py</code>: four different line lengths, plus the last frame showing
  the "dragged to the left half" auto-mirror — sprite and bubble flip, <b>text stays readable</b>.</sub>
</p>

> 📖 中文说明见 [README.md](README.md)

---

## ✨ What she does

| Interaction | Reaction |
|---|---|
| Wait a while | Random weird line (frequency is configurable, can be silenced entirely) |
| **Press down** | Press sound effect + squash |
| **Release** | Release sound effect |
| Single click | Bounce + a comeback line ("Don't poke me.") |
| Double click | Say something immediately |
| Press and drag | Drag anywhere; snaps to screen edge on release, position remembered |
| **Drag to left half** | **Auto horizontal mirror**: sprite and bubble flip, **text stays readable** |
| **Tray icon** | **Both left and right click open the settings panel directly** |
| **Right-click her** | **Nothing** — the settings entry deliberately lives only in the tray |

**Settings panel** (223×434, pops up above the cursor and clamps into the
available screen area):

- **Say something** — make her speak right now
- **Talk frequency** — Mute / Quiet / Normal / Chatty / Chatterbox
- **Size** — slider, 180–460 px, live resize
- **Skin** — lists everything in `assets/skins/`, click to switch
- **Sound** — on/off, preview, sound-set switching, volume slider
- **Other** — always on top / lock position / click-through / open skin &
  sound folders / edit lines / reload lines / back to corner / show·hide / quit

<br clear="right">

### Talk frequency

| Level | Auto-talk interval | Greets on launch |
|---|---|---|
| **Mute** | Never speaks on her own | ❌ |
| **Quiet** (default) | 5–15 min | ❌ |
| Normal | 1.5–3.5 min | ✅ |
| Chatty | 30–70 s | ✅ |
| Chatterbox | 8–20 s | ✅ |

### Everything is remembered

Position / size / skin / sound set / volume / sound on-off / talk frequency /
always-on-top / locked / click-through / auto-mirror are stored in `config.json`
next to the executable — plain text, editable in Notepad.
**Delete `config.json` to reset to factory settings.**

The only thing intentionally *not* remembered is "hidden" — otherwise you would
open the app and see nothing.

---

## 🚀 Getting started

### Option 1 — Download the portable build (no install needed)

Grab `Whale-Pet-Portable.zip` from
[**Releases**](https://github.com/wo-atmy/DeepSeek-Window-Pet/releases/latest)
and run `WhalePet.exe`.

No Python, no PySide6, no DSH plugin needed on the target machine. Copy the
folder to any Windows 10 / 11 PC (Desktop, D:, USB stick — anywhere).

> ⚠️ The executable is unsigned. Windows SmartScreen may show "Unknown
> publisher" the first time — click *More info → Run anyway*.

### Option 2 — Run from source

```bash
git clone https://github.com/wo-atmy/DeepSeek-Window-Pet.git
cd DeepSeek-Window-Pet
python -m pip install -r requirements.txt
```

Then double-click **`start-pet.bat`** (launches with `pythonw`, no console
window), or run `python whale_pet.py`.

Quit via **tray icon → Quit**, or the "Quit" button at the bottom of the panel.

> Running from source only needs **Python 3.9+** and **PySide6-Essentials**.

### Option 3 — Build your own portable package

Double-click **`build.bat`** (needs `python -m pip install pyinstaller`):

```
dist\WhalePet-Portable\        <- copy this folder anywhere
    WhalePet.exe
    _internal\                 <- Qt + Python runtime (don't delete)
    assets\                    <- skins + sounds
    lines.json
    README.txt                 <- Chinese readme for portable users
    LICENSE.txt / THIRD-PARTY-NOTICES.txt
dist\Whale-Pet-Portable.zip
```

Measured: ~**55 MB** folder, ~**23 MB** zip, works on Windows 10 / 11 x64.

The build strips the Qt parts this app never touches — notably
`opengl32sw.dll` (20 MB of software-OpenGL fallback; the app renders with
QPainter raster into a layered window and never requests an OpenGL surface),
plus unused platform backends, image-format plugins and translations.
See the comments inside `build.bat`.

`assets\` deliberately stays **outside** the exe so you can swap art and sounds
without rebuilding — and so the **licensing boundary is visible** (see
[Asset licensing](#-asset-licensing-important)).

### Option 4 — Let GitHub build it (no local setup)

[`.github/workflows/release.yml`](.github/workflows/release.yml) builds the
portable package on a Windows runner — nothing needs to be installed locally.

**No git required:** open the **Actions** tab → pick **Release portable build** →
**Run workflow**. When it finishes, download `Whale-Pet-Portable.zip` from the
**Artifacts** section at the bottom of the run.

Or, with git — pushing a `v*` tag builds *and* publishes the Release for you:

```bash
git tag v1.0.0
git push origin v1.0.0
```

You can also trigger it manually from the Actions tab (artifact only, no Release).

---

## 🎭 Skins

```
assets/skins/
    DSniang/                 <- folder name = name shown in the panel (default skin)
        char.png             <- pure character (transparent bg) **required**
        bubble.png           <- full image with bubble, optional
    example/                 <- code-generated placeholder, safe to delete
        char.png
        bubble.png
    my-character/            <- your own skin
        char.png
        bubble.png
    loose-image.png          <- also accepted: a single image as a skin
```

`char` may also be named `character` / `角色` / `本体`. Folders without a
matching image are skipped. Hover a skin button to see whether it ships a
`bubble.png`.

> **Why two images?** It follows the upstream plugin's convention (a cropped
> character + a full image with an empty bubble). This project **only renders
> the pure character** — the bubble is an SVG drawn in code, so it **adapts to
> any line length** instead of being squeezed into a fixed-size bubble in the
> image.
>
> **Placement rule** (copied from the plugin's `.dshwv-img`): the image is scaled
> to **59.45%** of the window edge and pinned to the **bottom-right**; the bubble
> occupies the top. Keep your character centred or bottom-right.

## 🔊 Sounds

```
assets/sounds/
    example/     press.wav  release.wav
    my-sound/    press.mp3  release.mp3
```

Extensions `mp3 / wav / m4a / ogg / aac` all work; one file is enough (the other
stays silent).

Playback uses **native Windows MCI** (`ctypes` → `winmm.mciSendString`) so
**QtMultimedia is not required**. MP3 supports volume control; WAV does not (MCI
limitation) — failures are ignored silently.

## 💬 Lines

Edit `lines.json`:

```json
{
  "lines":       ["spoken on her own, one per line", "..."],
  "click_lines": ["responses when you poke her", "..."]
}
```

Save, then tray → "Reload lines" — **no restart needed**. Ships with 75 lines +
15 comebacks.

---

## 🔒 Standalone by design

There is **no HTTP / socket / API call anywhere** in the code (the only match
for `http://www.w3.org/2000/svg` is the SVG namespace identifier, not a request).

**Only `assets/` next to the executable is read.** At startup the app at most
`mkdir`s `assets/skins` and `assets/sounds` — it **never scans external folders
or copies files**.

Registry, startup entries, background services, AppData: **untouched**. Delete
the folder and nothing remains.

---

## ⚖️ Asset licensing (important)

This is the easiest thing to get wrong when publishing, so it gets its own
section.

The **visual parameters** are modelled on
[MeteorNOX/DeepSeek-Balance-Whale-Widget](https://github.com/MeteorNOX/DeepSeek-Balance-Whale-Widget)
(MIT). That plugin's `PROVENANCE.md` states explicitly:

> The artwork under `assets/` (images / GIFs / sound effects) is **not covered
> by the MIT license** … provided for running the plugin only, **no sublicense
> is granted**.

Therefore:

| Content | License | Redistributable |
|---|---|---|
| This project's code (`whale_pet.py`, `tools/`) | MIT (c) 2025 wo-atmy | ✅ Yes |
| Synthesised sounds `assets/sounds/default/` | MIT (c) 2025 wo-atmy | ✅ Yes |
| Character art `assets/skins/DSniang/` and `docs/images/hero.png` | ⚠️ **Fan-made derivative, not MIT** | ⚠️ Not original to this project |
| The upstream plugin's **sound effects** | ❌ Not MIT | ❌ **No** |
| PySide6 runtime (inside the portable build) | LGPL v3 | ✅ Follow LGPL |

**In detail:**

- **Code** (`whale_pet.py`, `tools/`, scripts, docs) is MIT — use it freely.
- **Sounds** — the two blips in `assets/sounds/default/` are **synthesised
  originals** produced by
  [`tools/make_placeholder_assets.py`](tools/make_placeholder_assets.py), also
  MIT — replace or redistribute them freely.
- **Character art** (`assets/skins/DSniang/` and the hero image at the top of the
  README) is a **fan-made derivative of the upstream character**, not original to
  this project, and therefore **not covered by MIT**. For a public or commercial
  release, consider swapping in artwork you fully own (see "Skins" above — the
  code is unaffected).
- The upstream plugin's **sound effects** are not included; synthesised
  placeholders are shipped instead.

Full details in [**THIRD-PARTY-NOTICES.md**](THIRD-PARTY-NOTICES.md).

---

## 📁 Repository layout

```
.
├── whale_pet.py                  # the whole app (PySide6, single file, ~1300 lines)
├── lines.json                    # line library (edit this)
├── Whale-Pet-Portable.zip        # portable build (~23 MB, download & run)
├── requirements.txt              # PySide6-Essentials
├── build.bat                     # one-click portable build
├── start-pet.bat / stop-pet.bat  # run / stop from source
├── app.ico                       # exe icon (generated by tools/make_icon.py)
├── README.md / README.en.md      # Chinese / English docs
├── CHANGELOG.md                  # release history
├── LICENSE                       # MIT
├── THIRD-PARTY-NOTICES.md        # attribution + asset licensing boundary
├── .gitignore                    # keeps runtime files and build output out of git
├── .github/workflows/release.yml # tag -> Release with portable zip
├── assets/                       # art & audio
│   ├── skins/                    #   one folder per skin (DSniang is the default)
│   └── sounds/                   #   one folder per sound set
├── docs/
│   ├── portable-readme.txt       # Chinese readme for the portable build
│   └── images/                   # README images (hero + real render)
└── tools/
    ├── make_icon.py               # multi-size .ico from a character image
    ├── make_placeholder_assets.py # regenerates the default sounds (and a fallback skin)
    └── selftest.py                # offscreen render self-check
```

Generated at runtime (git-ignored): `config.json`, `pet.pid`, `build/`, `dist/`,
`tools/_*.png`.

---

## 🧪 Self-check

```bash
python tools/selftest.py     # renders tools/_selftest*.png to verify drawing
```

> **Don't validate this kind of window with `CopyFromScreen`** — the Windows DWM
> composition layer doesn't capture it correctly (bubbles come out dark and
> translucent, text disappears). Use the offscreen `grab()` in `selftest.py`.

---

## ⚠️ Known limitations

- **Only tested on Windows** (MCI audio and `WS_EX_TRANSPARENT` click-through are Win32).
- The character is a static image — no blinking / breathing animation.
- Full-screen games and videos cover her (normal always-on-top behaviour).
- The portable build is unsigned, so SmartScreen may warn the first time.
- If DSH is running, the balance widget in the bottom-right corner overlaps her.

---

## 🤝 Contributing

- Bugs and feature requests: open an [Issue](../../issues)
- PRs welcome. Before touching the code, read the module docstring at the top of
  `whale_pet.py` — it documents the constraints around window rendering, tray
  event handling, DPI handling and the MCI audio implementation.
- **Author**: [wo-atmy](https://github.com/wo-atmy)
- **QQ (project chat)**: `3982885755`

If this whale makes your screen corner a bit livelier, a ⭐ is the best thanks.

---

## 📄 License

Released under the **MIT License** — see [LICENSE](LICENSE).

```
Copyright (c) 2025 wo-atmy
```

Third-party components and assets: [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).

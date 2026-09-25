# Soul of Waifu on Linux

This is an **unofficial Linux port** of [jofizcd/Soul-of-Waifu](https://github.com/jofizcd/Soul-of-Waifu).
The port comes from [SnowwhiteOakheart/Soul-of-Waifu](https://github.com/SnowwhiteOakheart/Soul-of-Waifu)
(`linux` branch). This fork's `master` branch adds a Wayland-native, adaptive and themeable interface on top.
`main` tracks upstream unchanged.

**Based on the official v2.5.1 release.** Upstream's GitHub repository lags behind its releases: the code in
`Soul-of-Waifu-v2.5.1.rar` differs from GitHub `main` in about 60 files and adds new modules
(`hub_utils.py`, `discord_rpc.py`, `profile_backup.py`). The `linux` branch therefore uses the source code from the
release archive, merged with the Linux changes.

The Linux-specific code is kept small so upstream updates can still be merged:

| File | Purpose |
|---|---|
| `installer.sh` / `start.sh` | Linux replacements for `installer.bat` / `start.bat` |
| `app/utils/platform_compat.py` | Linux versions of the Windows-only calls (`os.startfile`, `winreg`, `ctypes.windll`, …) |
| `tools/patch_venv.py` | compatibility patches in the venv (fairseq on Python 3.11, pyworld, qwen_tts) |
| `tools/fetch_llama_backend.py` | downloads the llama.cpp Linux build for a backend |
| `tools/fork_report.sh` | lists the changes against the release source and checks that none got lost |
| `FORK-CHANGES.md` | every change with its purpose, plus the upstream update procedure |
| Small patches in the app code | forward-slash paths, llama.cpp Linux builds, audio devices, companion tools |

## Beyond the Linux port

This branch also adds features that are not Linux-specific:

- **German translation** of the whole app (`app/translations/de.yaml`, Options -> App Language).
- **Reply Language** (Options -> App Interface): tells the AI which language to answer in - narration,
  descriptions and inner thoughts included, not just dialogue. Default follows the app language;
  "Let the model decide" restores the upstream behaviour.
- **German as a chat translation target**, next to Russian.
- **The local LLM starts itself**: opening a chat that uses "Local LLM" starts llama-server in the background
  (model and backend permitting), so it is warm by the time the first message is sent; sending a message waits
  for the server instead of failing with "Could not reach the local server". Nothing happens for cloud
  providers or when no local model is configured.
- **Soul Stage Tabletop RPG Evolution (Phases 1–5):**
  - Live Player Status HUD for HP, Energy, Stress, and condition badges with duration counters and tooltips.
  - Procedural sound effects synthesizer (`app/utils/sfx_manager.py`) for dice, criticals, failures, and camp ambience.
  - Dedicated manual dice roller (`🎲`) supporting d20, d100, 2d6, d6, d12 with player skill modifiers and DC target checks.
  - Visual decision badges (Baldur's Gate 3 / Disco Elysium style) in the choices bar.
  - Interactive consumable inventory with instant 1-click recovery.
  - Campfire rest system (`🏕️`) with short/long rest, companion banter interludes, and bond milestones (+25, +50, +75).
  - Tactical Encounter Mode: a live initiative bar and enemy HP pools for real fights, with one-click Attack/Dodge/Item/Flee quick actions.
- Upstream fixes: the Appearance tab is translated at last, and RP editor cards no longer clip
  longer translations.

None of that is Linux-specific, so it runs on Windows as well: **[v2.5.1-win.1](https://github.com/SnowwhiteOakheart/Soul-of-Waifu/releases/tag/v2.5.1-win.1)** ships those
files as a small patch to unpack over an official v2.5.1 installation (untested on Windows, see the
release notes).

## Requirements

- An x86_64 Linux desktop (tested on CachyOS/KDE Plasma and Arch/Hyprland, Wayland sessions)
- Python is handled by the installer. It uses [`uv`](https://docs.astral.sh/uv/) to set up **Python 3.11**, the version the upstream dependency pins need.
- System packages:

```bash
# Arch / CachyOS / Manjaro
sudo pacman -S --needed uv ffmpeg espeak-ng sox git base-devel portaudio xcb-util-cursor unrar
# Debian / Ubuntu
sudo apt install ffmpeg espeak-ng sox git build-essential portaudio19-dev libxcb-cursor0 unrar
# Fedora
sudo dnf install uv ffmpeg espeak-ng sox git gcc gcc-c++ portaudio-devel xcb-util-cursor unrar
```

On Debian and Ubuntu, install `uv` with `curl -LsSf https://astral.sh/uv/install.sh | sh`.

Optional tools for the Soul Companion desktop features:

| Package | Used for |
|---|---|
| `playerctl` | media control (play/pause/next) |
| `wl-clipboard` (Wayland) or `xclip` (X11) | reading the clipboard |
| `xdotool` (X11) / `kdotool` (KDE Wayland, AUR) | active window title, focusing windows |
| `wtype` or `ydotool` (Wayland) | typing text into other apps |
| `xprintidle` (X11) | idle detection (companion falls asleep) |

## Installation

```bash
git clone https://github.com/SilentAutomaton/Soul-of-Waifu.git
cd Soul-of-Waifu
./installer.sh
```

The git repository has no icons, backgrounds or avatar models. Upstream ships those only inside the release
archive (`Soul-of-Waifu-vX.Y.Z.rar`, about 1.8 GB). The installer can download that archive and copy
just the missing files. It skips the bundled Windows Python and `.exe`/`.dll` files. If you already
have the archive:

```bash
./installer.sh --release-archive ~/Downloads/Soul-of-Waifu-v2.5.1.rar
```

Other options: `--torch cuda|rocm|cpu`, `--skip-assets`, `--no-shortcuts`, `-y` (non-interactive).
Run `./installer.sh --help` for details.

The installer creates an application menu entry **and a desktop shortcut** pointing at `start.sh`, and installs
the app logo as `~/.local/share/icons/hicolor/256x256/apps/soul-of-waifu.png`. The desktop file is made
executable (KDE) and marked as trusted (GNOME). To create them without running the whole installer again:

```bash
./installer.sh --shortcuts-only
```

## Starting

```bash
./start.sh
```

`start.sh` runs the app on **native Wayland** with the system window frame, and file dialogs go through
the XDG desktop portal. The desktop companion uses frameless, always-on-top overlay windows that position
themselves, and Wayland compositors don't allow that. To use it, run the app through XWayland:
`SOW_QPA=xcb ./start.sh`.

## Themes

Options -> Appearance -> Window Theme picks a theme and edits its colors, spacing, corner radius, glass
opacity, text size, interface scale and font. Themes are JSON files: the built-in ones are in
`app/gui/themes/`, your own (saved, imported, or written by hand) in `~/.config/soul-of-waifu/themes/`.
A file edited there is picked up while the app runs. Changing a theme restyles every widget at once, which
takes a few seconds.

## Local LLMs (llama.cpp)

The backend updater in the app downloads the official **Ubuntu x64** builds of llama.cpp. They run on most
distributions:

| Backend setting | Linux build |
|---|---|
| CPU | `llama-*-bin-ubuntu-x64` |
| Vulkan | `llama-*-bin-ubuntu-vulkan-x64` (works on NVIDIA, AMD and Intel) |
| HIP | `llama-*-bin-ubuntu-rocm-*-x64` |
| SYCL | `llama-*-bin-ubuntu-sycl-fp16-x64` |
| CUDA | **no official Linux build.** See below. |

`installer.sh` downloads the Vulkan build (the CPU build for `--torch cpu`). To fetch another backend later, run
`app/data/envs/sow/bin/python tools/fetch_llama_backend.py cpu|vulkan|hip|sycl`, or use the backend updater in the app.

If you have **more than one GPU** (e.g. an NVIDIA card plus an integrated Radeon), llama.cpp splits the model across
all Vulkan devices, and the slower one holds it back. Put `--device Vulkan0` into **Options -> LLM Settings ->
Custom Args** to use only the first GPU. `llama-server --list-devices` shows the numbering.

To use CUDA, pick one of these:
- Choose the **Vulkan** backend. It is fast on NVIDIA cards too, and it is what the installer sets up.
- Build it yourself - `./tools/build_llama_cuda.sh` does the whole job: it fetches the llama.cpp release the
  bundled backend reports, builds `llama-server` with CUDA for your card and copies it (with its libraries)
  into `app/utils/ai_clients/backend/cuda/`, where the app's CUDA option looks for it.

  ```bash
  ./tools/build_llama_cuda.sh              # same tag as the bundled backend, sm_89 (RTX 40xx)
  ./tools/build_llama_cuda.sh b11056 86    # a specific tag, sm_86 (RTX 30xx)
  ```

  Needs `cuda`, `cmake`, `ninja` and a compiler; the build takes a while. The backend updater does not know
  about your build, so run the script again after it replaces the bundled backends.
- Install a system `llama-server` with CUDA. If no bundled binary is found, the app uses the `llama-server`
  from your `PATH`.

## Feature status

| Feature | Linux |
|---|---|
| Chat, cloud providers, character cards, Soul Memory, Soul Stage | ✅ same code as Windows |
| TTS (Edge, ElevenLabs, XTTSv2, Qwen3, Kokoro, Silero) / STT (Faster-Whisper) | ✅ |
| RVC voice conversion | ✅ `tools/patch_venv.py` makes fairseq 0.12.2 importable on Python 3.11; the app also starts without it |
| Local LLMs (llama.cpp) | ✅ the installer fetches the Vulkan build (CPU/ROCm/SYCL available); no official CUDA build for Linux |
| Audio output | ✅ the device list offers the sound-server PCMs (`default`, `pipewire`, `pulse`) |
| Live2D / VRM avatars | ✅ |
| Open files, folders, apps (`.desktop` launchers, localized XDG folders) | ✅ |
| Media keys, clipboard, window title/focus | ✅ with the optional tools above |
| Idle detection (sleep/drowsy) | ⚠️ X11 (`xprintidle`) and GNOME only. Disabled on KDE Wayland. |
| Screenshots / mouse and keyboard automation (`mss`, `pyautogui`) | ⚠️ X11 only. On Wayland they reach XWayland windows only. |
| Code execution tool | ✅ Python and **Bash** (PowerShell on Windows) |
| Program language | ✅ English, Russian and **German** (`app/translations/de.yaml`, added in this fork) |
| Reply language of the AI | ✅ Options -> App Interface -> Reply Language (follows the app language by default) |

## Staying up to date with upstream

New versions usually appear in the **release archive** before they reach GitHub, so that is the main path:
the `release` branch holds the unmodified source of each release archive, and `linux` merges it.
**[FORK-CHANGES.md](FORK-CHANGES.md) documents every change in this fork** and the full update procedure;
`./tools/fork_report.sh` verifies afterwards that no change was lost in the merge.

1. Extract the new `Soul-of-Waifu-vX.Y.Z.rar`, switch to `release`, and copy its source files over the tracked
   files (skip `app/data/`, binaries and models). Commit.
2. Switch to `linux`, run `git merge release`, resolve any conflicts, and bump `SOW_VERSION` in `installer.sh`.

For commits that only exist on upstream's GitHub branch:

```bash
git remote add upstream https://github.com/jofizcd/Soul-of-Waifu.git   # once
git fetch upstream
git switch linux
git merge upstream/main
```

If upstream adds new Windows-only code, look for `os.startfile`, `winreg`, `ctypes.windll` and hard-coded
backslash paths (`"assets\\..."`), and route them through `app/utils/platform_compat.py`.

## License

GPL-3.0, same as upstream.

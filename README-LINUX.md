# Soul of Waifu on Linux

This is an **unofficial Linux port** of [jofizcd/Soul-of-Waifu](https://github.com/jofizcd/Soul-of-Waifu).
The port lives on the `linux` branch (the default branch of this fork). `main` tracks upstream unchanged.

**Based on the official v2.5.1 release.** Upstream's GitHub repository lags behind its releases: the code in
`Soul-of-Waifu-v2.5.1.rar` differs from GitHub `main` in about 60 files and adds new modules
(`hub_utils.py`, `discord_rpc.py`, `profile_backup.py`). The `linux` branch therefore uses the source code from the
release archive, merged with the Linux changes.

The Linux-specific code is kept small so upstream updates can still be merged:

| File | Purpose |
|---|---|
| `installer.sh` / `start.sh` | Linux replacements for `installer.bat` / `start.bat` |
| `app/utils/platform_compat.py` | Linux versions of the Windows-only calls (`os.startfile`, `winreg`, `ctypes.windll`, …) |
| Small patches in the app code | forward-slash paths, llama.cpp Linux builds, companion tools |

## Requirements

- An x86_64 Linux desktop (tested on CachyOS/KDE Plasma, Wayland session)
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
git clone -b linux https://github.com/SnowwhiteOakheart/Soul-of-Waifu.git
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

Other options: `--torch cuda|rocm|cpu`, `--skip-assets`, `--desktop-entry`, `-y` (non-interactive).
Run `./installer.sh --help` for details.

## Starting

```bash
./start.sh
```

`start.sh` runs the app through **XWayland** (`QT_QPA_PLATFORM=xcb`) by default. The desktop companion uses
frameless, always-on-top overlay windows that position themselves, and Wayland compositors don't allow that.
To try native Wayland anyway, run `QT_QPA_PLATFORM=wayland ./start.sh`.

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

To use CUDA, pick one of these:
- Choose the **Vulkan** backend. It is fast on NVIDIA cards too.
- Install a system `llama-server` with CUDA, for example the AUR package `llama.cpp-cuda`. If no bundled binary is
  found, the app uses the `llama-server` from your `PATH`.
- Build llama.cpp yourself and put `llama-server` and its `.so` files into `app/utils/ai_clients/backend/cuda/`.

## Feature status

| Feature | Linux |
|---|---|
| Chat, cloud providers, character cards, Soul Memory, Soul Stage | ✅ same code as Windows |
| TTS (Edge, ElevenLabs, XTTSv2, Qwen3, Kokoro, Silero) / STT (Faster-Whisper) | ✅ |
| RVC voice conversion | ⚠️ needs `fairseq`/`rvc-python` to build. The app still starts without them. |
| Live2D / VRM avatars | ✅ |
| Open files, folders, apps (`.desktop` launchers, localized XDG folders) | ✅ |
| Media keys, clipboard, window title/focus | ✅ with the optional tools above |
| Idle detection (sleep/drowsy) | ⚠️ X11 (`xprintidle`) and GNOME only. Disabled on KDE Wayland. |
| Screenshots / mouse and keyboard automation (`mss`, `pyautogui`) | ⚠️ X11 only. On Wayland they reach XWayland windows only. |
| Code execution tool | ✅ Python and **Bash** (PowerShell on Windows) |

## Staying up to date with upstream

```bash
git remote add upstream https://github.com/jofizcd/Soul-of-Waifu.git   # once
git fetch upstream
git switch linux
git merge upstream/main
```

New versions usually appear in the release archive before they reach GitHub. The `release` branch holds the
unmodified source of each release archive, and `linux` merges it. To update:

1. Extract the new `Soul-of-Waifu-vX.Y.Z.rar`, switch to `release`, and copy its source files over the tracked
   files (skip `app/data/`, binaries and models). Commit.
2. Switch to `linux`, run `git merge release`, resolve any conflicts, and bump `SOW_VERSION` in `installer.sh`.

If upstream adds new Windows-only code, look for `os.startfile`, `winreg`, `ctypes.windll` and hard-coded
backslash paths (`"assets\\..."`), and route them through `app/utils/platform_compat.py`.

## License

GPL-3.0, same as upstream.

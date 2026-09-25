#!/usr/bin/env bash
# Soul of Waifu - Linux installer
#
# Usage: ./installer.sh [options]
#   --torch cuda|rocm|cpu     PyTorch build (default: auto-detect and ask)
#   --release-archive FILE    Use an already downloaded Soul-of-Waifu-vX.Y.Z.rar
#   --skip-assets             Do not fetch icons/assets from the release archive
#   --no-shortcuts            Do not create the menu entry and desktop shortcut
#   --shortcuts-only          Only create the menu entry and desktop shortcut, then exit
#   -y, --yes                 Non-interactive, accept all defaults

set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")"

SOW_VERSION="2.5.1"
PYTHON_VERSION="${SOW_PYTHON_VERSION:-3.11}"
VENV_DIR="app/data/envs/sow-linux"
RELEASE_URL="https://github.com/jofizcd/Soul-of-Waifu/releases/download/v${SOW_VERSION}/Soul-of-Waifu-v${SOW_VERSION}.rar"
TORCH_PKGS=(torch==2.10.0 torchvision==0.25.0 torchaudio==2.10.0)
declare -A TORCH_INDEX=(
    [cuda]="https://download.pytorch.org/whl/cu128"
    [rocm]="https://download.pytorch.org/whl/rocm7.1"
    [cpu]="https://download.pytorch.org/whl/cpu"
)
# Installed separately with --no-deps so they cannot block the rest: packages that need a
# compiler, plus en-core-web-sm whose metadata (spacy<3.8) contradicts the pinned spacy==3.8.14.
FRAGILE_PKGS='^(fairseq|rvc-python|faiss-cpu|pyworld|praat-parselmouth|PyAudio|en-core-web-sm)'

GREEN=$'\e[0;32m'; YELLOW=$'\e[0;33m'; RED=$'\e[0;31m'; BOLD=$'\e[1m'; RESET=$'\e[0m'
info() { echo "${GREEN}==>${RESET} ${BOLD}$*${RESET}"; }
warn() { echo "${YELLOW}WARNING:${RESET} $*"; }
fail() { echo "${RED}ERROR:${RESET} $*" >&2; exit 1; }
have() { command -v "$1" >/dev/null 2>&1; }

TORCH_VARIANT=""; RELEASE_ARCHIVE=""; SKIP_ASSETS=0; SHORTCUTS=1; SHORTCUTS_ONLY=0; ASSUME_YES=0
while [[ $# -gt 0 ]]; do
    case "$1" in
        --torch) TORCH_VARIANT="${2:-}"; shift 2 ;;
        --release-archive) RELEASE_ARCHIVE="$(readlink -f "${2:-}")"; shift 2 ;;
        --skip-assets) SKIP_ASSETS=1; shift ;;
        --desktop-entry) SHORTCUTS=1; shift ;;
        --no-shortcuts) SHORTCUTS=0; shift ;;
        --shortcuts-only) SHORTCUTS_ONLY=1; shift ;;
        -y|--yes) ASSUME_YES=1; shift ;;
        -h|--help) sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) fail "Unknown option: $1 (see --help)" ;;
    esac
done

ask() {  # ask "question" y|n  -> returns 0 for yes
    local answer
    if [[ $ASSUME_YES -eq 1 ]]; then [[ $2 == y ]]; return; fi
    read -r -p "   $1 [$([[ $2 == y ]] && echo Y/n || echo y/N)] " answer
    answer="${answer:-$2}"
    [[ ${answer,,} == y* ]]
}

[[ $EUID -ne 0 ]] || fail "Do not run the installer as root."

echo "${GREEN}${BOLD}Soul of Waifu v${SOW_VERSION} - Linux installer${RESET}"
echo

install_shortcuts() {
    local data_home="${XDG_DATA_HOME:-$HOME/.local/share}"
    local apps_dir="$data_home/applications"
    local icon_dir="$data_home/icons/hicolor/256x256/apps"
    local icon_ref="soul-of-waifu"
    mkdir -p "$apps_dir" "$icon_dir"

    # Pillow lives in the app venv; fall back to the system python.
    local py="${PY:-}"
    [[ -n $py ]] || { [[ -x $VENV_DIR/bin/python ]] && py="$VENV_DIR/bin/python"; } || true
    [[ -n $py ]] || py=python3

    # Put a 256x256 PNG into the icon theme; fall back to the original file.
    if [[ -f app/gui/icons/logotype.png ]]; then
        if ! "$py" - "$PWD/app/gui/icons/logotype.png" "$icon_dir/soul-of-waifu.png" 2>/dev/null <<'PYICON'
import sys
from PIL import Image
src = Image.open(sys.argv[1]).convert("RGBA")
src.thumbnail((256, 256), Image.LANCZOS)
canvas = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
canvas.paste(src, ((256 - src.width) // 2, (256 - src.height) // 2))
canvas.save(sys.argv[2])
PYICON
        then
            cp -f app/gui/icons/logotype.png "$icon_dir/soul-of-waifu.png" 2>/dev/null || icon_ref="$PWD/app/gui/icons/logotype.png"
        fi
    else
        icon_ref="$PWD/app/gui/icons/logotype.ico"
    fi

    local entry
    entry="$(mktemp)"
    cat > "$entry" <<EOF
[Desktop Entry]
Type=Application
Name=Soul of Waifu
Comment=AI roleplay companion with Live2D/VRM avatars
Exec="$PWD/start.sh"
Path=$PWD
Icon=$icon_ref
Terminal=false
Categories=Game;RolePlaying;
StartupWMClass=main.py
EOF

    install -m 644 "$entry" "$apps_dir/soul-of-waifu.desktop"
    echo "   Menu entry:       $apps_dir/soul-of-waifu.desktop"

    local desktop_dir
    desktop_dir="$(xdg-user-dir DESKTOP 2>/dev/null || true)"
    [[ -d ${desktop_dir:-} ]] || desktop_dir="$HOME/Desktop"
    if [[ -d $desktop_dir ]]; then
        # KDE only launches .desktop files that are executable, GNOME wants them "trusted".
        install -m 755 "$entry" "$desktop_dir/soul-of-waifu.desktop"
        gio set "$desktop_dir/soul-of-waifu.desktop" metadata::trusted true >/dev/null 2>&1 || true
        echo "   Desktop shortcut: $desktop_dir/soul-of-waifu.desktop"
    else
        warn "No desktop folder found - only the menu entry was created."
    fi
    rm -f "$entry"

    command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$apps_dir" >/dev/null 2>&1 || true
    command -v gtk-update-icon-cache >/dev/null 2>&1 && gtk-update-icon-cache -q -t "$data_home/icons/hicolor" >/dev/null 2>&1 || true
}

if [[ $SHORTCUTS_ONLY -eq 1 ]]; then
    info "Creating shortcuts..."
    install_shortcuts
    exit 0
fi

# --------------------------------------------------------------------------- 1
info "[1/6] Checking system dependencies..."
libs="$(ldconfig -p 2>/dev/null || true)"
missing=()
have ffmpeg    || missing+=("ffmpeg")
have espeak-ng || missing+=("espeak-ng")
have sox       || missing+=("sox")
have git       || missing+=("git")
have gcc       || missing+=("gcc")
[[ $libs == *libportaudio.so* ]]  || missing+=("portaudio")
[[ $libs == *libxcb-cursor.so* ]] || missing+=("xcb-util-cursor")
if [[ ${#missing[@]} -gt 0 ]]; then
    warn "Missing system packages: ${missing[*]}"
    echo "   Arch/CachyOS:  sudo pacman -S --needed ffmpeg espeak-ng sox git base-devel portaudio xcb-util-cursor"
    echo "   Debian/Ubuntu: sudo apt install ffmpeg espeak-ng sox git build-essential portaudio19-dev libxcb-cursor0"
    echo "   Fedora:        sudo dnf install ffmpeg espeak-ng sox git gcc gcc-c++ portaudio-devel xcb-util-cursor"
    ask "Continue anyway? (the related features will not work)" y || exit 1
else
    echo "   All required system packages found."
fi
optional=()
have playerctl || optional+=("playerctl")
have wl-paste  || have xclip || optional+=("wl-clipboard")
have xdotool   || have kdotool || optional+=("xdotool/kdotool")
if [[ ${#optional[@]} -gt 0 ]]; then
    echo "   Optional for Soul Companion tools: ${optional[*]} (see README-LINUX.md)"
fi

# --------------------------------------------------------------------------- 2
info "[2/6] Checking program assets (icons, backgrounds, avatars)..."
if [[ -f app/gui/icons/resources.py ]]; then
    echo "   Assets already present."
elif [[ $SKIP_ASSETS -eq 1 ]]; then
    warn "Skipping assets - the app cannot start without app/gui/icons."
else
    downloaded=0
    if [[ -z $RELEASE_ARCHIVE ]]; then
        RELEASE_ARCHIVE="$PWD/app/data/_download/Soul-of-Waifu-v${SOW_VERSION}.rar"
        mkdir -p "$(dirname "$RELEASE_ARCHIVE")"
        echo "   Icons and assets are only shipped in the official release archive (~1.8 GB)."
        ask "Download ${RELEASE_URL##*/} from GitHub now?" y \
            || fail "Assets are required. Re-run with --release-archive FILE."
        curl -L --fail -C - -o "$RELEASE_ARCHIVE" "$RELEASE_URL"
        downloaded=1
    fi
    [[ -f $RELEASE_ARCHIVE ]] || fail "Archive not found: $RELEASE_ARCHIVE"

    # Pick a tool that actually understands this archive's format - a generic
    # "whichever tool is installed first" pick silently extracts nothing if e.g.
    # unrar is asked to open a .7z (unrar exits 0 having unpacked zero files).
    case "${RELEASE_ARCHIVE,,}" in
        *.7z)  candidates=(7z 7zz bsdtar) ;;
        *.zip) candidates=(bsdtar 7z 7zz) ;;
        *.rar) candidates=(unrar 7z 7zz bsdtar) ;;
        *)     candidates=(unrar 7z 7zz bsdtar) ;;
    esac
    extractor=""
    for tool in "${candidates[@]}"; do
        if have "$tool"; then extractor="$tool"; break; fi
    done
    [[ -n $extractor ]] || fail "Need $(IFS=/; echo "${candidates[*]}") to unpack ${RELEASE_ARCHIVE##*/}."

    # Extract next to the checkout: /tmp is often a small RAM-backed tmpfs.
    mkdir -p app/data
    tmp="$(mktemp -d "$PWD/app/data/_extract.XXXXXX")"
    trap 'rm -rf "$tmp"' EXIT
    echo "   Extracting with $extractor (needs a few GB of temporary space)..."
    case "$extractor" in
        unrar)  unrar x -idq -o+ "$RELEASE_ARCHIVE" "$tmp/" ;;
        7z|7zz) "$extractor" x -bso0 -bsp0 -y "$RELEASE_ARCHIVE" -o"$tmp" ;;
        bsdtar) bsdtar -xf "$RELEASE_ARCHIVE" -C "$tmp" --exclude '*/app/data/*' ;;
    esac

    found="$(find "$tmp" -maxdepth 6 -path '*/app/gui/icons/resources.py' -print -quit)"
    [[ -n $found ]] || fail "Unexpected archive layout (app/gui/icons/resources.py not found)."
    src="${found%/app/gui/icons/resources.py}"

    echo "   Copying icons and assets (files from this repository are never overwritten)..."
    # Keep the copied files out of `git status` in this checkout without touching .gitignore.
    exclude_file=""
    if [[ -d .git/info ]]; then
        exclude_file=".git/info/exclude"
        echo "# files copied from the release archive by installer.sh" >> "$exclude_file"
    fi
    copied=0
    while IFS= read -r -d '' f; do
        [[ -e $f ]] && continue
        mkdir -p "$(dirname "$f")"
        cp -p "$src/$f" "$f"
        if [[ -n $exclude_file ]]; then printf '/%s\n' "${f#./}" >> "$exclude_file"; fi
        copied=$((copied + 1))
    done < <(cd "$src" && find . -type f \
                ! -path './app/data/*' ! -path './app/utils/ai_clients/backend/*' \
                ! -iname '*.bat' ! -iname '*.exe' ! -iname '*.dll' -print0)
    rm -rf "$tmp"; trap - EXIT
    echo "   Installed $copied files."

    if [[ $downloaded -eq 1 ]] && ask "Delete the downloaded archive to free ~1.8 GB?" y; then
        rm -f "$RELEASE_ARCHIVE"
    fi
fi

# --------------------------------------------------------------------------- 3
info "[3/6] Preparing Python ${PYTHON_VERSION} environment in ${VENV_DIR}..."
if [[ -x $VENV_DIR/bin/python ]] && ! "$VENV_DIR/bin/python" -c \
        "import sys; sys.exit(sys.version.startswith('${PYTHON_VERSION}.') is False)"; then
    warn "Existing environment uses $("$VENV_DIR/bin/python" --version 2>&1) - recreating it."
    rm -rf "$VENV_DIR"
fi

if have uv; then
    [[ -x $VENV_DIR/bin/python ]] || uv venv --seed --python "$PYTHON_VERSION" "$VENV_DIR"
    pip_install() { uv pip install --python "$VENV_DIR/bin/python" "$@"; }
elif have "python${PYTHON_VERSION}"; then
    [[ -x $VENV_DIR/bin/python ]] || "python${PYTHON_VERSION}" -m venv "$VENV_DIR"
    "$VENV_DIR/bin/python" -m pip install --upgrade pip setuptools wheel
    pip_install() { "$VENV_DIR/bin/python" -m pip install "$@"; }
else
    fail "Python ${PYTHON_VERSION} is required. Install 'uv' (e.g. 'sudo pacman -S uv', see https://docs.astral.sh/uv/) - it downloads Python ${PYTHON_VERSION} automatically."
fi
PY="$VENV_DIR/bin/python"

# --------------------------------------------------------------------------- 4
if [[ -z $TORCH_VARIANT ]]; then
    gpus="$(lspci 2>/dev/null || true)"
    if have nvidia-smi && nvidia-smi -L >/dev/null 2>&1; then
        detected=cuda
    elif [[ -e /dev/kfd && $gpus =~ (VGA|Display|3D).*(AMD|ATI) ]]; then
        detected=rocm
    else
        detected=cpu
    fi

    if [[ $ASSUME_YES -eq 1 ]]; then
        TORCH_VARIANT=$detected
    else
        case $detected in cuda) default_choice=1 ;; rocm) default_choice=2 ;; *) default_choice=3 ;; esac
        echo "   PyTorch build:  [1] CUDA (NVIDIA)   [2] ROCm (AMD)   [3] CPU only"
        read -r -p "   Choice [${default_choice}]: " choice
        case "${choice:-$default_choice}" in
            1) TORCH_VARIANT=cuda ;; 2) TORCH_VARIANT=rocm ;; 3) TORCH_VARIANT=cpu ;;
            *) fail "Invalid choice." ;;
        esac
    fi
fi
[[ -n ${TORCH_INDEX[$TORCH_VARIANT]:-} ]] || fail "Unknown --torch value '$TORCH_VARIANT' (use cuda, rocm or cpu)."

info "[4/6] Installing PyTorch (${TORCH_VARIANT})..."
pip_install --index-url "${TORCH_INDEX[$TORCH_VARIANT]}" "${TORCH_PKGS[@]}"

# --------------------------------------------------------------------------- 5
info "[5/6] Installing dependencies from requirements.txt (this takes a while)..."
req_main="$(mktemp)"; req_fragile="$(mktemp)"
# torch is already installed from the matching index above.
grep -vE '^(torch|torchvision|torchaudio)==' requirements.txt | grep -vE "$FRAGILE_PKGS" > "$req_main" || true
grep -E "$FRAGILE_PKGS" requirements.txt > "$req_fragile" || true
echo "pyautogui" >> "$req_main"
# pyworld (RVC) still imports pkg_resources, which setuptools>=81 no longer ships.
echo "setuptools<81" >> "$req_main"

failed=()
if ! pip_install -r "$req_main"; then
    warn "Bulk install failed - retrying package by package..."
    while IFS= read -r line; do
        [[ -z $line || $line == \#* ]] && continue
        pip_install "$line" >/dev/null 2>&1 || failed+=("${line%%[=; @]*}")
    done < "$req_main"
fi
# --no-deps: their dependencies are already pinned above, and rvc-python would
# otherwise downgrade numpy (it asks for numpy<=1.23.5).
while IFS= read -r line; do
    [[ -z $line ]] && continue
    echo "   Building ${line%%[=; @]*}..."
    pip_install --no-deps "$line" >/dev/null 2>&1 || failed+=("${line%%[=; @]*}")
done < "$req_fragile"
rm -f "$req_main" "$req_fragile"
# Compatibility patches: fairseq on Python 3.11 (RVC), pyworld's pkg_resources
# warning, and qwen_tts' flash-attn banner (see tools/patch_venv.py).
"$PY" tools/patch_venv.py >/dev/null || warn "Could not patch venv packages - RVC may be unavailable."

"$PY" -m playwright install chromium >/dev/null 2>&1 \
    || warn "Playwright browser download failed (only needed for web automation tools)."

# Local LLMs: the Windows release ships llama.cpp .exe files; fetch the official Linux build.
# Vulkan runs on NVIDIA, AMD and Intel GPUs; CPU-only installs get the CPU build.
llama_backend=vulkan
[[ $TORCH_VARIANT == cpu ]] && llama_backend=cpu
if [[ -x app/utils/ai_clients/backend/$llama_backend/llama-server ]]; then
    echo "   llama.cpp ($llama_backend) already installed."
else
    echo "   Downloading llama.cpp ($llama_backend) for local models..."
    "$PY" tools/fetch_llama_backend.py "$llama_backend" \
        || warn "Could not download llama.cpp - use Options -> LLM settings -> backend updater later."
fi

# --------------------------------------------------------------------------- 6
info "[6/6] Smoke test..."
"$PY" -c "import torch, numpy, transformers, PyQt6; print('   Core imports OK - torch', torch.__version__, '| GPU available:', torch.cuda.is_available())"
if "$PY" -c "from TTS.api import TTS" >/dev/null 2>&1; then echo "   Coqui TTS OK"; else warn "Coqui TTS import failed."; fi
if "$PY" -c "import kokoro" >/dev/null 2>&1; then echo "   Kokoro TTS OK"; else warn "Kokoro TTS unavailable."; fi
if "$PY" -c "import rvc_python" >/dev/null 2>&1; then echo "   RVC OK"; else warn "RVC voice conversion unavailable."; fi
if [[ ${#failed[@]} -gt 0 ]]; then
    warn "Could not install: ${failed[*]} - the related features will be disabled."
fi

if [[ $SHORTCUTS -eq 1 ]]; then
    install_shortcuts
fi

echo
echo "${GREEN}${BOLD}Installation complete.${RESET} Start the program with ./start.sh"

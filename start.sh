#!/usr/bin/env bash
# Soul of Waifu - Linux launcher
cd "$(dirname "$(readlink -f "$0")")" || exit 1

VENV_DIR="$PWD/app/data/envs/sow-linux"
pause() { if [[ -t 0 ]]; then read -r -p "Press Enter to exit..."; fi; }

if [[ ! -x $VENV_DIR/bin/python ]]; then
    echo "ERROR: Python environment not found in $VENV_DIR - run ./installer.sh first."
    pause; exit 1
fi
if [[ ! -f app/gui/icons/resources.py ]]; then
    echo "ERROR: Program assets are missing (app/gui/icons) - run ./installer.sh first."
    pause; exit 1
fi
if ! command -v ffmpeg >/dev/null 2>&1; then
    echo "ERROR: ffmpeg not found. Install it with your package manager (e.g. 'sudo pacman -S ffmpeg')."
    pause; exit 1
fi

export VIRTUAL_ENV="$VENV_DIR"
export PATH="$VENV_DIR/bin:$PATH"
export PYTHONUNBUFFERED=1
# The desktop companion uses frameless always-on-top overlays that position themselves.
# Wayland compositors don't allow that, so run through XWayland unless overridden
# (e.g. QT_QPA_PLATFORM=wayland ./start.sh).
export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-xcb}"

python main.py "$@"
code=$?
if [[ $code -ne 0 ]]; then
    echo
    echo "Soul of Waifu exited with code $code - see the logs/ folder for details."
    pause
fi
exit $code

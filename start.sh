#!/usr/bin/env bash
# Soul of Waifu - Linux launcher
cd "$(dirname "$(readlink -f "$0")")" || exit 1

VENV_DIR="$PWD/app/data/envs/sow"
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
# Native Wayland by default. The desktop companion positions its own overlay windows,
# which Wayland does not allow: use SOW_QPA=xcb ./start.sh for it.
export QT_QPA_PLATFORM="${SOW_QPA:-wayland}"
# The pip Qt build has no KDE/GTK platform theme; the portal one gives native file dialogs.
export QT_QPA_PLATFORMTHEME=xdgdesktopportal

python main.py "$@"
code=$?
if [[ $code -ne 0 ]]; then
    echo
    echo "Soul of Waifu exited with code $code - see the logs/ folder for details."
    pause
fi
exit $code

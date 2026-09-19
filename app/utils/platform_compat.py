"""
Cross-platform helpers for the Linux port of Soul of Waifu.

Everything Windows-specific in the upstream code (os.startfile, winreg,
ctypes.windll, ...) that has a reasonable Linux equivalent is routed through
this module, so the rest of the code base stays close to upstream.
All Linux helpers are best-effort: they rely on common desktop tools
(xdg-open, playerctl, wl-paste/xclip, xdotool/kdotool, ...) and degrade
gracefully when those are missing.
"""

import os
import re
import sys
import time
import shlex
import shutil
import logging
import platform
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger("Platform Compat")

IS_WINDOWS = sys.platform == "win32"
IS_MACOS = sys.platform == "darwin"
IS_LINUX = sys.platform.startswith("linux")


def _session_type() -> str:
    return (os.environ.get("XDG_SESSION_TYPE") or "").lower()


def is_wayland() -> bool:
    return _session_type() == "wayland" or bool(os.environ.get("WAYLAND_DISPLAY"))


def is_x11() -> bool:
    return _session_type() == "x11" or (bool(os.environ.get("DISPLAY")) and not is_wayland())


def _run(cmd: list, timeout: float = 2.0) -> Optional[str]:
    """Run a command and return stdout, or None if it failed / is missing."""
    if not shutil.which(cmd[0]):
        return None
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except Exception:
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout


def _spawn(cmd: list, cwd: Optional[str] = None) -> None:
    """Start a detached GUI process that outlives Soul of Waifu."""
    subprocess.Popen(
        cmd,
        cwd=cwd,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


# ---------------------------------------------------------------------------
# Files, folders, URIs
# ---------------------------------------------------------------------------

def open_path(path) -> None:
    """Open a file, folder or URI with the system default handler (like os.startfile)."""
    path = str(path)
    if IS_WINDOWS:
        os.startfile(path)
    elif IS_MACOS:
        _spawn(["open", path])
    else:
        if not shutil.which("xdg-open"):
            raise RuntimeError("xdg-open is not installed (package 'xdg-utils').")
        _spawn(["xdg-open", path])


def reveal_path(path) -> None:
    """
    Show a file in the file manager with the file itself selected - the Linux answer to
    `explorer /select,`. Falls back to opening the containing folder.
    """
    path = os.path.abspath(str(path))
    if IS_WINDOWS:
        _spawn(["explorer", f"/select,{path}"])
        return
    if IS_MACOS:
        _spawn(["open", "-R", path])
        return

    # org.freedesktop.FileManager1 is what Dolphin, Nautilus, Nemo and Thunar implement.
    # _run returns None when the call fails, and then the folder fallback below applies.
    if os.path.exists(path):
        shown = _run(["gdbus", "call", "--session",
                      "--dest", "org.freedesktop.FileManager1",
                      "--object-path", "/org/freedesktop/FileManager1",
                      "--method", "org.freedesktop.FileManager1.ShowItems",
                      f"['file://{path}']", ""], timeout=5.0)
        if shown is not None:
            return

    folder = path if os.path.isdir(path) else os.path.dirname(path) or "."
    open_path(folder)


_XDG_USER_DIR_KEYS = {
    "Desktop": "XDG_DESKTOP_DIR",
    "Downloads": "XDG_DOWNLOAD_DIR",
    "Documents": "XDG_DOCUMENTS_DIR",
    "Pictures": "XDG_PICTURES_DIR",
    "Music": "XDG_MUSIC_DIR",
    "Videos": "XDG_VIDEOS_DIR",
}


def user_dir(name: str) -> Path:
    """
    Resolve a well-known user folder ("Desktop", "Downloads", ...).
    On Linux this honours ~/.config/user-dirs.dirs, so localized folders
    such as ~/Schreibtisch or ~/Bilder are found correctly.
    """
    home = Path.home()
    key = _XDG_USER_DIR_KEYS.get(name)
    if IS_LINUX and key:
        value = os.environ.get(key)
        if not value:
            config_home = Path(os.environ.get("XDG_CONFIG_HOME") or home / ".config")
            try:
                for line in (config_home / "user-dirs.dirs").read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if line.startswith(key + "="):
                        value = line.split("=", 1)[1].strip().strip('"')
                        break
            except OSError:
                pass
        if value:
            value = value.replace("$HOME", str(home))
            return Path(os.path.expanduser(value))
    return home / name


TRASH_URI = "shell:RecycleBinFolder" if IS_WINDOWS else "trash:///"


# ---------------------------------------------------------------------------
# System idle time
# ---------------------------------------------------------------------------

_idle_backend = None  # name of the first backend that worked, or "none"


def _idle_xprintidle() -> Optional[int]:
    if not is_x11():
        # Under Wayland xprintidle only sees XWayland input and would report
        # the user as idle while they type into native Wayland apps.
        return None
    out = _run(["xprintidle"], timeout=1)
    return int(out.strip()) if out and out.strip().isdigit() else None


def _idle_gnome() -> Optional[int]:
    out = _run([
        "gdbus", "call", "--session",
        "--dest", "org.gnome.Mutter.IdleMonitor",
        "--object-path", "/org/gnome/Mutter/IdleMonitor/Core",
        "--method", "org.gnome.Mutter.IdleMonitor.GetIdletime",
    ], timeout=1)
    m = re.search(r"uint64\s+(\d+)", out or "")
    return int(m.group(1)) if m else None


def _idle_freedesktop() -> Optional[int]:
    out = _run([
        "gdbus", "call", "--session",
        "--dest", "org.freedesktop.ScreenSaver",
        "--object-path", "/org/freedesktop/ScreenSaver",
        "--method", "org.freedesktop.ScreenSaver.GetSessionIdleTime",
    ], timeout=1)
    m = re.search(r"uint32\s+(\d+)", out or "")
    return int(m.group(1)) if m else None


_IDLE_BACKENDS = {
    "xprintidle": _idle_xprintidle,
    "gnome": _idle_gnome,
    "freedesktop": _idle_freedesktop,
}


def get_idle_time_ms() -> int:
    """Milliseconds since the last user input; 0 if it cannot be determined."""
    global _idle_backend
    if not IS_LINUX or _idle_backend == "none":
        return 0

    if _idle_backend:
        value = _IDLE_BACKENDS[_idle_backend]()
        return value if value is not None else 0

    for name, func in _IDLE_BACKENDS.items():
        value = func()
        if value is not None:
            _idle_backend = name
            logger.info(f"Using '{name}' to detect system idle time.")
            return value

    _idle_backend = "none"
    logger.info("No idle-time source available (install 'xprintidle' on X11); companion sleep mode is disabled.")
    return 0


# ---------------------------------------------------------------------------
# Clipboard, keyboard, media keys
# ---------------------------------------------------------------------------

def read_clipboard_text() -> str:
    """Read plain text from the system clipboard (safe to call from worker threads)."""
    commands = []
    if is_wayland():
        commands.append(["wl-paste", "--no-newline", "--type", "text/plain"])
    commands += [
        ["xclip", "-selection", "clipboard", "-o"],
        ["xsel", "--clipboard", "--output"],
    ]
    for cmd in commands:
        out = _run(cmd, timeout=2)
        if out is not None:
            return out
    return ""


def type_text(text: str) -> bool:
    """Type text into the focused window. Returns False if no tool could do it."""
    if is_wayland():
        if shutil.which("wtype"):
            return subprocess.run(["wtype", "--", text], timeout=30).returncode == 0
        if shutil.which("ydotool"):
            return subprocess.run(["ydotool", "type", "--", text], timeout=30).returncode == 0
    if is_x11() and shutil.which("xdotool"):
        return subprocess.run(["xdotool", "type", "--delay", "5", "--", text], timeout=30).returncode == 0
    return False


_PLAYERCTL_ACTIONS = {"play": "play-pause", "pause": "play-pause", "next": "next", "prev": "previous"}


def send_media_key(action: str) -> None:
    """Send a media action (play/pause/next/prev) to the active MPRIS player."""
    if not shutil.which("playerctl"):
        raise RuntimeError("playerctl is not installed; media control is unavailable.")
    subprocess.run(["playerctl", _PLAYERCTL_ACTIONS.get(action, "play-pause")], timeout=3)


# ---------------------------------------------------------------------------
# Windows / applications
# ---------------------------------------------------------------------------

_window_title_cache = ("", 0.0)


def get_active_window_title() -> str:
    """Title of the focused window (X11 via xdotool, KDE Wayland via kdotool)."""
    global _window_title_cache
    title, ts = _window_title_cache
    if time.monotonic() - ts < 2.0:
        return title

    title = ""
    tools = []
    if is_x11():
        tools.append("xdotool")
    if is_wayland():
        tools.append("kdotool")
    for tool in tools:
        out = _run([tool, "getactivewindow", "getwindowname"], timeout=1)
        if out:
            title = out.strip()
            break

    _window_title_cache = (title, time.monotonic())
    return title


def focus_window(pids: set, names: set) -> bool:
    """Bring a window of one of the given processes to the front."""
    if is_x11():
        if shutil.which("xdotool"):
            for pid in pids:
                if _run(["xdotool", "search", "--onlyvisible", "--pid", str(pid), "windowactivate"]) is not None:
                    return True
        if shutil.which("wmctrl"):
            for name in names:
                if _run(["wmctrl", "-x", "-a", name]) is not None:
                    return True
    if is_wayland() and shutil.which("kdotool"):
        for name in names:
            if _run(["kdotool", "search", "--class", name, "windowactivate"]) is not None:
                return True
    return False


# Linux equivalents for the app aliases the companion knows on Windows.
LINUX_APP_ALIASES = {
    "calc.exe": ["kcalc", "gnome-calculator", "qalculate-qt", "qalculate-gtk", "galculator"],
    "notepad.exe": ["kate", "kwrite", "gnome-text-editor", "gedit", "mousepad", "xed"],
    "chrome.exe": ["google-chrome-stable", "google-chrome", "chromium", "chromium-browser"],
    "Telegram.exe": ["telegram-desktop", "Telegram"],
    "Discord.exe": ["discord", "vesktop", "Discord"],
    "spotify.exe": ["spotify", "spotify-launcher"],
    "steam.exe": ["steam"],
    "Code.exe": ["code", "codium", "code-oss"],
    "taskmgr.exe": ["plasma-systemmonitor", "gnome-system-monitor", "ksysguard", "xfce4-taskmanager"],
    "explorer.exe": ["dolphin", "nautilus", "thunar", "nemo", "pcmanfm"],
    "ms-settings:": ["systemsettings", "gnome-control-center", "xfce4-settings-manager"],
    "mspaint.exe": ["kolourpaint", "pinta", "gimp"],
    "msedge.exe": ["microsoft-edge-stable", "firefox", "chromium"],
}


def _desktop_entry_dirs() -> list:
    data_home = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
    data_dirs = (os.environ.get("XDG_DATA_DIRS") or "/usr/local/share:/usr/share").split(":")
    dirs = [data_home / "applications"]
    dirs += [Path(d) / "applications" for d in data_dirs if d]
    dirs += [
        data_home / "flatpak" / "exports" / "share" / "applications",
        Path("/var/lib/flatpak/exports/share/applications"),
        user_dir("Desktop"),
    ]
    seen, result = set(), []
    for d in dirs:
        if d not in seen and d.is_dir():
            seen.add(d)
            result.append(d)
    return result


def _parse_desktop_entry(path: Path) -> dict:
    entry, in_main = {}, False
    try:
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if line.startswith("["):
                in_main = line == "[Desktop Entry]"
                continue
            if in_main and "=" in line:
                k, v = line.split("=", 1)
                entry.setdefault(k.strip(), v.strip())
    except OSError:
        pass
    return entry


def find_desktop_entry(target: str, exact_only: bool = False) -> Optional[Path]:
    """Find a .desktop launcher whose file name or Name= matches target."""
    needle = target.lower().removesuffix(".desktop").strip()
    if not needle:
        return None
    partial = None
    for d in _desktop_entry_dirs():
        for f in d.glob("*.desktop"):
            stem = f.stem.lower()
            entry = _parse_desktop_entry(f)
            if entry.get("NoDisplay", "").lower() == "true" or entry.get("Type", "Application") != "Application":
                continue
            names = {stem, stem.rsplit(".", 1)[-1], entry.get("Name", "").lower()}
            if needle in names:
                return f
            if not exact_only and partial is None and len(needle) >= 3 and any(needle in n for n in names):
                partial = f
    return partial


def launch_desktop_entry(path: Path) -> None:
    if shutil.which("gio"):
        _spawn(["gio", "launch", str(path)])
        return
    entry = _parse_desktop_entry(path)
    exec_line = entry.get("Exec")
    if not exec_line:
        raise RuntimeError(f"No Exec line in {path}")
    args = [a for a in shlex.split(exec_line) if not re.fullmatch(r"%[fFuUdDnNickvm]", a)]
    _spawn(args)


def launch_application(target: str) -> Optional[str]:
    """
    Launch an application by alias, executable name or .desktop entry.
    Returns a human readable description of what was launched, or None.
    """
    candidates = list(LINUX_APP_ALIASES.get(target, []))
    plain = target.removesuffix(".exe")
    candidates += [target, plain, plain.lower()]

    for cand in candidates:
        exe = shutil.which(cand)
        if exe:
            _spawn([exe])
            return f"executable '{cand}'"

    # Exact launcher matches for every candidate first, so "calc" finds a
    # calculator alias before fuzzily matching e.g. "libreoffice-calc".
    for exact_only in (True, False):
        for cand in candidates:
            entry = find_desktop_entry(cand, exact_only=exact_only)
            if entry:
                launch_desktop_entry(entry)
                return f"launcher '{entry.stem}'"
    return None


# ---------------------------------------------------------------------------
# System information
# ---------------------------------------------------------------------------

def get_os_description() -> str:
    arch = platform.architecture()[0]
    if IS_LINUX:
        try:
            pretty = platform.freedesktop_os_release().get("PRETTY_NAME")
        except OSError:
            pretty = None
        if pretty:
            return f"{pretty} (Linux {platform.release()}, {arch})"
    return f"{platform.system()} {platform.release()} ({arch}, Build {platform.version()})"


def get_cpu_name() -> Optional[str]:
    if IS_LINUX:
        try:
            for line in Path("/proc/cpuinfo").read_text().splitlines():
                if line.lower().startswith("model name"):
                    return line.split(":", 1)[1].strip()
        except OSError:
            pass
    return None


def get_gpu_names() -> list:
    """GPU names via lspci (used when nvidia-smi is not available)."""
    out = _run(["lspci"], timeout=3)
    if not out:
        return []
    gpus = []
    for line in out.splitlines():
        if re.search(r"VGA compatible controller|3D controller|Display controller", line):
            gpus.append(line.split(": ", 1)[-1].strip())
    return gpus


# Folders an agent must never touch on Linux.
LINUX_PROTECTED_ROOTS = [
    Path(p) for p in ("/bin", "/boot", "/dev", "/etc", "/lib", "/lib64", "/opt",
                      "/proc", "/root", "/sbin", "/sys", "/usr", "/var")
]

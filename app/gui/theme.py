"""
Semantic color tokens for the whole GUI.

The widgets set their style sheets with literal colors of the default dark palette.
install() wraps QWidget.setStyleSheet so every sheet passes through resolve(), which
moves each literal onto the active theme:

- grays follow the surface/text ramp by brightness (the original tint is kept),
- translucent white is the "overlay" color (the glass effect),
- the blue accent family follows the accent color,
- near-black shadows and all other hues stay as they are.

A theme is a JSON file with the keys of DEFAULT_TOKENS. Built-in themes live in
app/gui/themes/, user themes in ~/.config/soul-of-waifu/themes/.
"""

import os
import re
import json
import colorsys
import weakref
from functools import lru_cache
from pathlib import Path

from PyQt6 import sip
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QFileSystemWatcher, QTimer
from PyQt6.QtGui import QColor, QFont, QFontDatabase, QGuiApplication, QPalette
from PyQt6.QtWidgets import QWidget, QApplication

BUILTIN_DIR = Path(__file__).resolve().parent / "themes"
USER_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "soul-of-waifu" / "themes"

COLOR_TOKENS = [
    "surface0", "surface1", "surface2", "surface3", "surface4",
    "text_muted", "text_secondary", "text_primary", "overlay", "accent",
]

DEFAULT_TOKENS = {
    "name": "Default",
    "surface0": "#0B0B0F",
    "surface1": "#161616",
    "surface2": "#1B1B1B",
    "surface3": "#2B2B2B",
    "surface4": "#3C3C3C",
    "text_muted": "#6F6B63",
    "text_secondary": "#B3B3B3",
    "text_primary": "#E3E3E3",
    "overlay": "#FFFFFF",
    "accent": "#4BB8FF",
}

DEFAULT_SETTINGS = {
    "theme": "default",
    "overrides": {},
    "follow_system": False,
    "font_family": "",
    "font_scale": 1.0,
    "ui_scale": 1.0,
    "density": 1.0,
    "radius": 1.0,
    "glass": 1.0,
}

# Brightness of each ramp stop in the default palette; black stays fixed for shadows.
RAMP = ["surface0", "surface1", "surface2", "surface3", "surface4",
        "text_muted", "text_secondary", "text_primary", "overlay"]

# Families the widgets ask for by name; a custom font replaces all of them.
APP_FONT_FAMILIES = [
    "Inter Tight", "Inter Tight Medium", "Inter Tight SemiBold", "Inter Tight Bold",
    "Inter Tight Light", "Inter", "Comfortaa", "Segoe UI", "Segoe UI Variable",
]

GRAY_SPREAD = 24
SHADOW_MAX = 8
ACCENT_HUES = (185, 235)

COLOR_RE = re.compile(
    r"#(?P<hex>[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b"
    r"|(?P<fn>rgba?)\(\s*(?P<r>\d+)\s*,\s*(?P<g>\d+)\s*,\s*(?P<b>\d+)\s*(?:,\s*(?P<a>[\d.]+%?)\s*)?\)"
)
FONT_SIZE_RE = re.compile(r"(font-size\s*:\s*)(\d+(?:\.\d+)?)px")
SPACING_RE = re.compile(r"((?:padding|margin)(?:-[a-z]+)?\s*:)([^;}]*)")
RADIUS_RE = re.compile(r"((?:border-[a-z-]*radius)\s*:)([^;}]*)")
PX_RE = re.compile(r"(\d+(?:\.\d+)?)px")
RAW_MARKER = "/* raw */"


def _rgb(hex_color):
    c = QColor(hex_color)
    return c.red(), c.green(), c.blue()


def _brightness(r, g, b):
    return (r + g + b) / 3


def _clamp(v, lo=0, hi=255):
    return max(lo, min(hi, v))


class Theme:
    """A resolved set of tokens plus the scale factors, ready to map colors."""

    def __init__(self, tokens, settings):
        self.tokens = {**DEFAULT_TOKENS, **tokens}
        self.font_scale = float(settings.get("font_scale", 1.0))
        self.density = float(settings.get("density", 1.0))
        self.radius = float(settings.get("radius", 1.0))
        self.glass = float(settings.get("glass", 1.0))
        default = [(_brightness(*_rgb(DEFAULT_TOKENS[k])), _rgb(DEFAULT_TOKENS[k])) for k in RAMP]
        active = [_rgb(self.tokens[k]) for k in RAMP]
        self._ramp = [(0, (0, 0, 0), (0, 0, 0))] + [
            (level, d, a) for (level, d), a in zip(default, active)
        ]
        self._accent_default = colorsys.rgb_to_hls(*[c / 255 for c in _rgb(DEFAULT_TOKENS["accent"])])
        self._accent = colorsys.rgb_to_hls(*[c / 255 for c in _rgb(self.tokens["accent"])])
        self.key = json.dumps([self.tokens, self.font_scale, self.density, self.radius, self.glass], sort_keys=True)

    def map_rgb(self, r, g, b):
        if max(r, g, b) - min(r, g, b) <= GRAY_SPREAD:
            level = _brightness(r, g, b)
            if level <= SHADOW_MAX:
                return r, g, b
            for (l0, d0, a0), (l1, d1, a1) in zip(self._ramp, self._ramp[1:]):
                if level <= l1:
                    t = (level - l0) / (l1 - l0) if l1 > l0 else 0
                    shift = [(a0[i] + (a1[i] - a0[i]) * t) - (d0[i] + (d1[i] - d0[i]) * t) for i in range(3)]
                    return tuple(int(round(_clamp(c + s))) for c, s in zip((r, g, b), shift))
            return r, g, b
        h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
        if ACCENT_HUES[0] <= h * 360 <= ACCENT_HUES[1] and s >= 0.35:
            dh, dl, ds = self._accent_default
            ah, al, as_ = self._accent
            h = (h + ah - dh) % 1.0
            l = min(1.0, max(0.0, l + al - dl))
            s = min(1.0, s * (as_ / ds if ds else 1))
            return tuple(int(round(c * 255)) for c in colorsys.hls_to_rgb(h, l, s))
        return r, g, b

    def map_alpha(self, alpha_text):
        if self.glass == 1.0:
            return alpha_text
        if alpha_text.endswith("%"):
            return f"{_clamp(float(alpha_text[:-1]) * self.glass, 0, 100):g}%"
        value = float(alpha_text)
        if "." in alpha_text or value <= 1:
            return f"{min(1.0, value * self.glass):.3f}"
        return str(int(_clamp(value * self.glass)))


_theme = Theme({}, {})
_IDENTITY_KEY = _theme.key
_raw_sheets = weakref.WeakKeyDictionary()
_original_set = QWidget.setStyleSheet
_original_get = QWidget.styleSheet
_original_app_set = QApplication.setStyleSheet


@lru_cache(maxsize=8192)
def _resolve(qss, key):
    theme = _theme

    def color(m):
        if m.group("hex"):
            h = m.group("hex")
            if len(h) == 3:
                h = "".join(c * 2 for c in h)
            r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
            return "#{:02X}{:02X}{:02X}".format(*theme.map_rgb(r, g, b))
        r, g, b = theme.map_rgb(int(m.group("r")), int(m.group("g")), int(m.group("b")))
        if m.group("a") is None:
            return f"{m.group('fn')}({r}, {g}, {b})"
        return f"{m.group('fn')}({r}, {g}, {b}, {theme.map_alpha(m.group('a'))})"

    def scale_px(factor):
        def repl(m):
            return m.group(1) + PX_RE.sub(lambda p: f"{round(float(p.group(1)) * factor)}px", m.group(2))
        return repl

    out = COLOR_RE.sub(color, qss)
    if theme.font_scale != 1.0:
        out = FONT_SIZE_RE.sub(lambda m: f"{m.group(1)}{round(float(m.group(2)) * theme.font_scale)}px", out)
    if theme.density != 1.0:
        out = SPACING_RE.sub(scale_px(theme.density), out)
    if theme.radius != 1.0:
        out = RADIUS_RE.sub(scale_px(theme.radius), out)
    return out


def resolve(qss):
    if not qss or RAW_MARKER in qss or _theme.key == _IDENTITY_KEY:
        return qss
    return _resolve(qss, _theme.key)


def qcolor(r, g=None, b=None, a=255):
    """QColor for paint code: qcolor(r, g, b[, a]) or qcolor("#RRGGBB")."""
    if isinstance(r, str):
        c = QColor(r)
        r, g, b, a = c.red(), c.green(), c.blue(), c.alpha()
    mr, mg, mb = _theme.map_rgb(r, g, b)
    if a < 255:
        a = int(_clamp(a * _theme.glass))
    return QColor(mr, mg, mb, a)


def token(name):
    return QColor(_theme.tokens[name])


def _set_style_sheet(widget, qss):
    _raw_sheets[widget] = qss
    _original_set(widget, resolve(qss))


def _style_sheet(widget):
    return _raw_sheets.get(widget, _original_get(widget))


def _app_set_style_sheet(app, qss):
    _raw_sheets[app] = qss
    _original_app_set(app, resolve(qss))


def _reapply():
    # Qt repolishes every styled widget here; with ~800 sheets this takes seconds.
    QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
    try:
        _restyle_all()
    finally:
        QApplication.restoreOverrideCursor()


def _restyle_all():
    for owner, qss in list(_raw_sheets.items()):
        if sip.isdeleted(owner):
            continue
        if isinstance(owner, QApplication):
            _original_app_set(owner, resolve(qss))
        else:
            _original_set(owner, resolve(qss))
            owner.update()


def _load_json(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    tokens = {k: data[k] for k in COLOR_TOKENS if isinstance(data.get(k), str) and QColor(data[k]).isValid()}
    tokens["name"] = str(data.get("name") or Path(path).stem)
    return tokens


def theme_id(name):
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_") or "theme"


class ThemeManager(QObject):
    """Owns the settings, the theme files and live switching."""

    changed = pyqtSignal()

    def __init__(self, configuration):
        super().__init__()
        self.configuration = configuration
        stored = configuration.get_main_setting("theme")
        self.settings = {**DEFAULT_SETTINGS, **(stored if isinstance(stored, dict) else {})}
        USER_DIR.mkdir(parents=True, exist_ok=True)
        self._watcher = QFileSystemWatcher([str(USER_DIR)])
        self._watcher.directoryChanged.connect(lambda _: self._schedule_apply())
        self._watcher.fileChanged.connect(lambda _: self._schedule_apply())
        self._debounce = QTimer(self, singleShot=True, interval=300)
        self._debounce.timeout.connect(self.apply)

    def themes(self):
        """{id: tokens} of built-in and user themes; a user theme overrides a built-in one."""
        found = {}
        for folder in (BUILTIN_DIR, USER_DIR):
            for path in sorted(folder.glob("*.json")):
                tokens = _load_json(path)
                if tokens:
                    found[path.stem] = tokens
        found.setdefault("default", dict(DEFAULT_TOKENS))
        return found

    def is_user_theme(self, theme):
        return (USER_DIR / f"{theme}.json").exists()

    def current_tokens(self):
        base = self.themes().get(self.settings["theme"]) or DEFAULT_TOKENS
        tokens = {**DEFAULT_TOKENS, **base, **self.settings["overrides"]}
        if self.settings["follow_system"]:
            tokens.update(self._system_tokens())
        return tokens

    def _system_tokens(self):
        app = QGuiApplication.instance()
        if app is None:
            return {}
        accent = app.palette().color(QPalette.ColorRole.Accent)
        return {"accent": accent.name()} if accent.isValid() else {}

    def apply(self):
        global _theme
        self.configuration.update_main_setting("theme", dict(self.settings))
        _theme = Theme(self.current_tokens(), self.settings)
        _reapply()
        self._watch_user_files()
        self.changed.emit()

    def _schedule_apply(self):
        self._debounce.start()

    def _watch_user_files(self):
        files = [str(p) for p in USER_DIR.glob("*.json")]
        watched = set(self._watcher.files())
        new = [f for f in files if f not in watched]
        if new:
            self._watcher.addPaths(new)

    def update(self, **changes):
        """Change settings, save them and restyle the app (debounced for sliders)."""
        self.settings.update(changes)
        self._schedule_apply()

    def save(self, **changes):
        """Store settings that only take effect after a restart, without restyling."""
        self.settings.update(changes)
        self.configuration.update_main_setting("theme", dict(self.settings))

    def set_token(self, name, value):
        self.update(overrides={**self.settings["overrides"], name: value})

    def select(self, theme):
        self.update(theme=theme, overrides={})

    def save_as(self, name):
        tokens = self.current_tokens()
        tokens["name"] = name
        ident = theme_id(name)
        self.write_theme(USER_DIR / f"{ident}.json", tokens)
        self.select(ident)
        return ident

    def delete(self, theme):
        path = USER_DIR / f"{theme}.json"
        if path.exists():
            path.unlink()
        if self.settings["theme"] == theme:
            self.select("default")

    def import_file(self, path):
        tokens = _load_json(path)
        if not tokens:
            return None
        ident = theme_id(tokens["name"])
        self.write_theme(USER_DIR / f"{ident}.json", tokens)
        self.select(ident)
        return ident

    def export_file(self, path):
        self.write_theme(Path(path), self.current_tokens())

    @staticmethod
    def write_theme(path, tokens):
        data = {"name": tokens.get("name", path.stem), **{k: tokens[k] for k in COLOR_TOKENS}}
        Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def migrate_legacy(configuration):
    """Move the old window theme preset onto a token theme, once. The old theme code then
    keeps drawing the default palette, which the active theme remaps."""
    if configuration.get_main_setting("theme") is not None:
        return
    legacy = (configuration.get_main_setting("window_theme") or {}).get("theme_name", "default")
    settings = dict(DEFAULT_SETTINGS)
    if (BUILTIN_DIR / f"{legacy}.json").exists():
        settings["theme"] = legacy
    configuration.update_main_setting("theme", settings)
    configuration.update_main_setting("window_theme", {})
    configuration.update_main_setting("gui_theme", "default")


def read_settings(configuration):
    stored = configuration.get_main_setting("theme")
    return {**DEFAULT_SETTINGS, **(stored if isinstance(stored, dict) else {})}


def prepare_environment(configuration):
    """Scale settings that Qt reads once, before QApplication exists."""
    settings = read_settings(configuration)
    if settings["ui_scale"] != 1.0:
        os.environ["QT_SCALE_FACTOR"] = f"{settings['ui_scale']:g}"
    if settings["font_scale"] != 1.0:
        os.environ["QT_FONT_DPI"] = str(round(96 * settings["font_scale"]))
    return settings


# Windows families the widgets name, mapped onto what the app ships or Linux has.
WINDOWS_FAMILIES = {
    "Segoe UI": "Inter Tight",
    "Segoe UI Variable": "Inter Tight",
    "Inter": "Inter Tight",
    "Segoe UI Emoji": "Noto Color Emoji",
    "Consolas": "monospace",
    "Cascadia Code": "monospace",
}


def use_app_fonts(folder):
    """Load the bundled fonts and make Inter Tight the default, as Segoe UI is on Windows.
    Widgets without an explicit font (list items, dialogs, rich text) used the system font."""
    for path in sorted(Path(folder).iterdir()):
        if path.suffix.lower() in (".ttf", ".otf"):
            QFontDatabase.addApplicationFont(str(path))
    for name, family in WINDOWS_FAMILIES.items():
        QFont.insertSubstitution(name, family)
    app = QApplication.instance()
    font = app.font()
    font.setFamily("Inter Tight")
    app.setFont(font)


def use_system_hinting():
    """The widgets ask for no hinting, which Windows ignores for its own rendering but
    FreeType obeys: text comes out softer than in every other window. Keep fontconfig's choice."""
    QFont.setHintingPreference = lambda font, preference: None


def use_font_family(family):
    """Point every family the widgets name at the chosen one."""
    for name in APP_FONT_FAMILIES:
        QFont.insertSubstitution(name, family)
    app = QApplication.instance()
    font = app.font()
    font.setFamily(family)
    app.setFont(font)


manager = None


def install(configuration):
    """Wrap setStyleSheet and load the saved theme. Call before the widgets exist."""
    QWidget.setStyleSheet = _set_style_sheet
    QWidget.styleSheet = _style_sheet
    QApplication.setStyleSheet = _app_set_style_sheet
    global _theme, manager
    manager = ThemeManager(configuration)
    _theme = Theme(manager.current_tokens(), manager.settings)
    app = QGuiApplication.instance()
    if app is not None:
        follow = lambda *_: manager.settings["follow_system"] and manager._schedule_apply()
        app.styleHints().colorSchemeChanged.connect(follow)
        app.paletteChanged.connect(follow)
    return manager

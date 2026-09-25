from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt

from app.gui import theme
from app.gui.custom_widgets import FlowLayout, SowInputDialog, SLIDER_STYLE_DARK

LABEL_STYLE = "color: #B3B3B3; background: transparent; border: none; font-size: 12px;"
HINT_STYLE = "color: #6F6B63; background: transparent; border: none; font-size: 11px;"
BUTTON_STYLE = """
    QPushButton {
        background-color: rgba(255, 255, 255, 0.05); color: #E3E3E3;
        border: 1px solid rgba(255, 255, 255, 0.10); border-radius: 8px; padding: 6px 12px;
    }
    QPushButton:hover { background-color: rgba(255, 255, 255, 0.10); }
    QPushButton:focus { border: 1px solid #4BB8FF; }
    QPushButton:disabled { color: #6F6B63; }
"""
INPUT_STYLE = """
    QComboBox, QFontComboBox {
        background-color: rgba(255, 255, 255, 0.05); color: #E3E3E3;
        border: 1px solid rgba(255, 255, 255, 0.10); border-radius: 8px; padding: 4px 10px; min-height: 26px;
    }
    QComboBox:focus, QFontComboBox:focus { border: 1px solid #4BB8FF; }
    QComboBox QAbstractItemView { background-color: #161616; color: #E3E3E3; selection-background-color: #2B2B2B; }
    QCheckBox { color: #B3B3B3; background: transparent; border: none; spacing: 8px; }
    QCheckBox::indicator {
        width: 16px; height: 16px; border-radius: 4px;
        border: 1px solid rgba(255, 255, 255, 0.35); background: rgba(255, 255, 255, 0.05);
    }
    QCheckBox::indicator:checked { background: #4BB8FF; border-color: #4BB8FF; }
    QCheckBox::indicator:focus { border: 2px solid #4BB8FF; }
"""
TOKEN_LABELS = {
    "surface0": "Deep background",
    "surface1": "Background",
    "surface2": "Window",
    "surface3": "Card",
    "surface4": "Raised",
    "text_muted": "Muted text",
    "text_secondary": "Secondary text",
    "text_primary": "Text",
    "overlay": "Glass tint",
    "accent": "Accent",
}
SLIDERS = [
    # key, label key, default label, min %, max %, needs restart
    ("density", "theme_density", "Spacing", 60, 140, False),
    ("radius", "theme_radius", "Corner radius", 0, 200, False),
    ("glass", "theme_glass", "Glass opacity", 30, 250, False),
    ("font_scale", "theme_font_scale", "Text size", 80, 150, False),
    ("ui_scale", "theme_ui_scale", "Interface scale (after restart)", 75, 200, True),
]
RESTART_KEYS = {key for key, *_rest, restart in SLIDERS if restart}


class ThemeEditor(QtWidgets.QFrame):
    """Theme picker and token editor for Options -> Appearance."""

    def __init__(self, manager, translations, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.translations = translations
        self.setStyleSheet("QFrame { background: transparent; border: none; }" + INPUT_STYLE)

        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(16)

        picker = FlowLayout(spacing=8)
        self.combo = QtWidgets.QComboBox()
        self.combo.setAccessibleName(self.tr("theme_select", "Theme"))
        self.combo.setMinimumWidth(180)
        self.combo.activated.connect(lambda i: self.manager.select(self.combo.itemData(i)))
        picker.addWidget(self.combo)
        self.btn_save = self._button("theme_save_as", "Save as…", self.save_as)
        self.btn_import = self._button("theme_import", "Import…", self.import_theme)
        self.btn_export = self._button("theme_export", "Export…", self.export_theme)
        self.btn_delete = self._button("theme_delete", "Delete", self.delete_theme)
        for b in (self.btn_save, self.btn_import, self.btn_export, self.btn_delete):
            picker.addWidget(b)
        root.addLayout(picker)

        root.addWidget(self._label("theme_colors", "Colors", HINT_STYLE))
        swatches = FlowLayout(spacing=10)
        self.swatches = {}
        for name in theme.COLOR_TOKENS:
            cell = QtWidgets.QWidget()
            cell_layout = QtWidgets.QVBoxLayout(cell)
            cell_layout.setContentsMargins(0, 0, 0, 0)
            cell_layout.setSpacing(4)
            btn = QtWidgets.QPushButton()
            btn.setFixedSize(64, 32)
            btn.setCursor(QtGui.QCursor(Qt.CursorShape.PointingHandCursor))
            text = self.tr(f"theme_token_{name}", TOKEN_LABELS[name])
            btn.setAccessibleName(text)
            btn.setToolTip(text)
            btn.clicked.connect(lambda _, n=name: self.pick_color(n))
            cell_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignHCenter)
            lbl = self._label(None, text, HINT_STYLE)
            lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            cell_layout.addWidget(lbl)
            swatches.addWidget(cell)
            self.swatches[name] = btn
        root.addLayout(swatches)

        self.follow = QtWidgets.QCheckBox(self.tr("theme_follow_system", "Take the accent color from the system"))
        self.follow.toggled.connect(lambda on: self.manager.update(follow_system=on))
        root.addWidget(self.follow)

        # A plain list: QFontComboBox draws every family in its own font, which takes
        # seconds with a thousand installed fonts.
        font_row = FlowLayout(spacing=10)
        font_row.addWidget(self._label("theme_custom_font", "Font (after restart)", LABEL_STYLE))
        self.font_combo = QtWidgets.QComboBox()
        self.font_combo.setEditable(True)
        self.font_combo.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.NoInsert)
        self.font_combo.setMinimumWidth(240)
        self.font_combo.setMaxVisibleItems(20)
        self.font_combo.setAccessibleName(self.tr("theme_font", "Font"))
        self.font_combo.addItem(self.tr("theme_font_default", "App default (Inter Tight)"), "")
        for family in QtGui.QFontDatabase.families():
            self.font_combo.addItem(family, family)
        completer = self.font_combo.completer()
        completer.setCompletionMode(QtWidgets.QCompleter.CompletionMode.PopupCompletion)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.font_combo.activated.connect(self._font_changed)
        self.font_combo.lineEdit().editingFinished.connect(self._font_changed)
        font_row.addWidget(self.font_combo)
        root.addLayout(font_row)

        self.sliders = {}
        for key, tr_key, default, lo, hi, _restart in SLIDERS:
            row = QtWidgets.QHBoxLayout()
            row.setSpacing(12)
            lbl = self._label(tr_key, default, LABEL_STYLE)
            lbl.setMinimumWidth(190)
            slider = QtWidgets.QSlider(Qt.Orientation.Horizontal)
            slider.setRange(lo, hi)
            slider.setSingleStep(5)
            slider.setPageStep(10)
            slider.setStyleSheet(SLIDER_STYLE_DARK)
            slider.setAccessibleName(lbl.text())
            value = self._label(None, "", LABEL_STYLE)
            value.setMinimumWidth(44)
            slider.valueChanged.connect(lambda v, s=slider, k=key, vl=value: self._slider_changed(s, k, v, vl))
            slider.sliderReleased.connect(lambda s=slider, k=key: self._commit(k, s.value() / 100))
            row.addWidget(lbl)
            row.addWidget(slider, 1)
            row.addWidget(value)
            root.addLayout(row)
            self.sliders[key] = (slider, value)

        self.manager.changed.connect(self.refresh)
        self.refresh()

    def tr(self, key, default):
        return self.translations.get(key, default) if key else default

    def _label(self, key, default, style):
        lbl = QtWidgets.QLabel(self.tr(key, default))
        lbl.setStyleSheet(style)
        return lbl

    def _button(self, key, default, slot):
        b = QtWidgets.QPushButton(self.tr(key, default))
        b.setStyleSheet(BUTTON_STYLE)
        b.setCursor(QtGui.QCursor(Qt.CursorShape.PointingHandCursor))
        b.clicked.connect(slot)
        return b

    def refresh(self):
        s = self.manager.settings
        themes = self.manager.themes()
        self.combo.blockSignals(True)
        self.combo.clear()
        for ident, tokens in sorted(themes.items(), key=lambda kv: (kv[0] != "default", kv[1]["name"].lower())):
            self.combo.addItem(tokens["name"], ident)
        self.combo.setCurrentIndex(max(0, self.combo.findData(s["theme"])))
        self.combo.blockSignals(False)
        self.btn_delete.setEnabled(self.manager.is_user_theme(s["theme"]))

        tokens = self.manager.current_tokens()
        for name, btn in self.swatches.items():
            # The swatch shows the exact token, so its sheet must bypass the remapping.
            btn.setStyleSheet(
                f"{theme.RAW_MARKER} QPushButton {{ background-color: {tokens[name]};"
                f" border: 1px solid rgba(128, 128, 128, 0.5); border-radius: 6px; }}"
                f" QPushButton:focus {{ border: 2px solid {tokens['accent']}; }}"
            )

        self.follow.blockSignals(True)
        self.follow.setChecked(s["follow_system"])
        self.follow.blockSignals(False)
        self.font_combo.blockSignals(True)
        self.font_combo.setCurrentIndex(max(0, self.font_combo.findData(s["font_family"])))
        self.font_combo.blockSignals(False)

        for key, (slider, value) in self.sliders.items():
            slider.blockSignals(True)
            slider.setValue(round(float(s[key]) * 100))
            slider.blockSignals(False)
            value.setText(f"{slider.value()}%")

    def _slider_changed(self, slider, key, percent, value_label):
        value_label.setText(f"{percent}%")
        if not slider.isSliderDown():
            self._commit(key, percent / 100)

    def _commit(self, key, value):
        if key in RESTART_KEYS:
            self.manager.save(**{key: value})
        else:
            self.manager.update(**{key: value})

    def _font_changed(self, *_):
        index = self.font_combo.findText(self.font_combo.currentText(), Qt.MatchFlag.MatchFixedString)
        if index < 0:
            index = max(0, self.font_combo.findData(self.manager.settings["font_family"]))
        self.font_combo.setCurrentIndex(index)
        family = self.font_combo.itemData(index)
        if family != self.manager.settings["font_family"]:
            self.manager.save(font_family=family)

    def pick_color(self, name):
        current = QtGui.QColor(self.manager.current_tokens()[name])
        color = QtWidgets.QColorDialog.getColor(current, self.window(), self.swatches[name].toolTip())
        if color.isValid():
            self.manager.set_token(name, color.name().upper())

    def save_as(self):
        dialog = SowInputDialog(
            parent=self.window(),
            title=self.tr("theme_save_title", "Save Theme"),
            label=self.tr("theme_save_label", "Theme name:"),
            placeholder=self.tr("theme_save_placeholder", "My Theme"),
        )
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted and dialog.get_text().strip():
            self.manager.save_as(dialog.get_text().strip())

    def import_theme(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.window(), self.tr("theme_import_title", "Import Theme"), "", "Theme (*.json)")
        if path and self.manager.import_file(path) is None:
            QtWidgets.QMessageBox.warning(
                self.window(), self.tr("theme_import_title", "Import Theme"),
                self.tr("theme_import_invalid", "This file is not a valid theme."))

    def export_theme(self):
        name = self.manager.current_tokens()["name"]
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self.window(), self.tr("theme_export_title", "Export Theme"), f"{theme.theme_id(name)}.json", "Theme (*.json)")
        if path:
            self.manager.export_file(path if path.endswith(".json") else path + ".json")

    def delete_theme(self):
        self.manager.delete(self.manager.settings["theme"])

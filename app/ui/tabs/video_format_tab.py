from PySide6.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QSpinBox, QLabel, 
    QRadioButton, QHBoxLayout, QButtonGroup, QCheckBox
)
from PySide6.QtCore import Signal


class VideoFormatTab(QWidget):
    """Tab for video format-based renaming."""
    
    options_changed = Signal()

    def __init__(self, i18n):
        super().__init__()
        self.i18n = i18n
        self._create_layout()
        # Default state
        self._on_source_change(None)
        self._on_prefix_enabled_changed()

    def _create_layout(self):
        layout = QFormLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Prefix controls
        self.use_prefix_checkbox = QCheckBox("Use prefix")
        self.use_prefix_checkbox.toggled.connect(self._on_prefix_enabled_changed)
        layout.addRow("", self.use_prefix_checkbox)

        self.prefix_label = QLabel("Prefix:")
        self.prefix_input = QLineEdit()
        self.prefix_input.setPlaceholderText("Enter prefix...")
        self.prefix_input.textChanged.connect(self._sync_pattern_from_prefix)
        layout.addRow(self.prefix_label, self.prefix_input)

        # Start number
        self.start_label = QLabel("Start number:")
        self.start_input = QSpinBox()
        self.start_input.setRange(0, 999999)
        self.start_input.setValue(1)
        self.start_input.valueChanged.connect(lambda: self.options_changed.emit())
        layout.addRow(self.start_label, self.start_input)

        # Resolution source
        self.res_source_label = QLabel("Resolution source:")
        res_source_layout = QHBoxLayout()
        self.manual_radio = QRadioButton("Manual")
        self.detect_radio = QRadioButton("Detect")
        self.detect_radio.setChecked(True)
        
        self.res_group = QButtonGroup(self)
        self.res_group.addButton(self.manual_radio)
        self.res_group.addButton(self.detect_radio)
        self.res_group.buttonClicked.connect(self._on_source_change)
        
        res_source_layout.addWidget(self.manual_radio)
        res_source_layout.addWidget(self.detect_radio)
        res_source_layout.addStretch()
        layout.addRow(self.res_source_label, res_source_layout)

        # Resolution input
        self.res_label = QLabel("Resolution (WxH):")
        self.res_input = QLineEdit("1920x1080")
        self.res_input.textChanged.connect(lambda: self.options_changed.emit())
        layout.addRow(self.res_label, self.res_input)

        # Pattern
        self.pattern_label = QLabel("Pattern:")
        self.pattern_input = QLineEdit("{n} - {res}")
        self.pattern_input.textChanged.connect(lambda: self.options_changed.emit())
        layout.addRow(self.pattern_label, self.pattern_input)

        # Help
        self.help_label = QLabel("Variables: {n}, {res}, {name}")
        self.help_label.setStyleSheet("color: gray; font-size: 11px;")
        layout.addRow("", self.help_label)

    def _on_source_change(self, button):
        is_manual = self.manual_radio.isChecked()
        self.res_input.setEnabled(is_manual)
        self.options_changed.emit()

    def _on_prefix_enabled_changed(self):
        enabled = self.use_prefix_checkbox.isChecked()
        self.prefix_input.setEnabled(enabled)
        self._sync_pattern_from_prefix()

    def _sync_pattern_from_prefix(self):
        use_prefix = self.use_prefix_checkbox.isChecked()
        prefix = self.prefix_input.text().strip()
        
        self.pattern_input.blockSignals(True)
        if use_prefix and prefix:
            self.pattern_input.setText(f"{prefix}_{{n}} - {{res}}")
        else:
            self.pattern_input.setText("{n} - {res}")
        self.pattern_input.blockSignals(False)
        
        self.options_changed.emit()

    def get_options(self) -> dict:
        return {
            "prefix": "", # Prefix is now baked into the pattern
            "start": self.start_input.value(),
            "auto_detect": self.detect_radio.isChecked(),
            "manual_res": self.res_input.text(),
            "pattern": self.pattern_input.text()
        }

    def update_translations(self):
        self.use_prefix_checkbox.setText(self.i18n.tr("use_prefix"))
        self.prefix_label.setText(self.i18n.tr("prefix"))
        self.prefix_input.setPlaceholderText(self.i18n.tr("prefix_placeholder"))
        self.start_label.setText(self.i18n.tr("start_number"))
        self.res_source_label.setText(self.i18n.tr("res_source"))
        self.manual_radio.setText(self.i18n.tr("manual"))
        self.detect_radio.setText(self.i18n.tr("detect"))
        self.res_label.setText(self.i18n.tr("res_label"))
        self.pattern_label.setText(self.i18n.tr("pattern"))

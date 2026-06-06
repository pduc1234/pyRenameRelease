"""Sequential rename tab."""
from PySide6.QtWidgets import QWidget, QFormLayout, QLineEdit, QSpinBox, QLabel
from PySide6.QtCore import Signal


class SequentialTab(QWidget):
    """Tab for sequential numbering rename."""
    
    options_changed = Signal()

    def __init__(self, i18n):
        super().__init__()
        self.i18n = i18n
        self._create_layout()

    def _create_layout(self):
        layout = QFormLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Prefix
        self.prefix_label = QLabel("Prefix:")
        self.prefix_input = QLineEdit()
        self.prefix_input.textChanged.connect(lambda: self.options_changed.emit())
        layout.addRow(self.prefix_label, self.prefix_input)

        # Start number
        self.start_label = QLabel("Start number:")
        self.start_input = QSpinBox()
        self.start_input.setRange(0, 999999)
        self.start_input.setValue(1)
        self.start_input.valueChanged.connect(lambda: self.options_changed.emit())
        layout.addRow(self.start_label, self.start_input)

        # Padding
        self.pad_label = QLabel("Zero-pad digits:")
        self.pad_input = QSpinBox()
        self.pad_input.setRange(1, 10)
        self.pad_input.setValue(1)
        self.pad_input.valueChanged.connect(lambda: self.options_changed.emit())
        layout.addRow(self.pad_label, self.pad_input)

        # Note about variables (optional in task, but sequential supports it in preview_engine)
        # The preview_engine.preview_sequential doesn't actually use a pattern, just prefix/start/pad.
        # Wait, the task says:
        # "Fields: Start number, Pattern, Optional variables help"
        # "Supported variables: {n} = number, {name} = original filename, {res} = video resolution"
        # "Example: Pattern: {n} - {res}"
        
        # My preview_engine.preview_sequential is simple. I should update it to support pattern.
        # Let me re-read sequential_tab requirement.
        
        # Okay, I'll add Pattern input for Sequential tab too as per requirement.
        self.pattern_label = QLabel("Pattern:")
        self.pattern_input = QLineEdit("{n}")
        self.pattern_input.textChanged.connect(lambda: self.options_changed.emit())
        layout.addRow(self.pattern_label, self.pattern_input)
        
        self.help_label = QLabel("Variables: {n} = number, {name} = original filename, {res} = resolution")
        self.help_label.setStyleSheet("color: gray; font-size: 11px;")
        layout.addRow("", self.help_label)

    def get_options(self) -> dict:
        return {
            "prefix": self.prefix_input.text(),
            "start": self.start_input.value(),
            "pad": self.pad_input.value(),
            "pattern": self.pattern_input.text()
        }

    def update_translations(self):
        self.prefix_label.setText(self.i18n.tr("prefix"))
        self.start_label.setText(self.i18n.tr("start_number"))
        self.pad_label.setText(self.i18n.tr("zero_pad"))
        self.pattern_label.setText(self.i18n.tr("pattern"))
        # self.help_label text could also be localized if needed

"""Add Suffix rename tab."""
from PySide6.QtWidgets import QWidget, QFormLayout, QLineEdit, QLabel
from PySide6.QtCore import Signal


class AddSuffixTab(QWidget):
    """Tab for adding suffix to filenames."""
    
    options_changed = Signal()

    def __init__(self, i18n):
        super().__init__()
        self.i18n = i18n
        self._create_layout()

    def _create_layout(self):
        layout = QFormLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Suffix
        self.suffix_label = QLabel("Suffix:")
        self.suffix_input = QLineEdit()
        self.suffix_input.textChanged.connect(lambda: self.options_changed.emit())
        layout.addRow(self.suffix_label, self.suffix_input)

        # Separator
        self.sep_label = QLabel("Separator:")
        self.sep_input = QLineEdit(" - ")
        self.sep_input.textChanged.connect(lambda: self.options_changed.emit())
        layout.addRow(self.sep_label, self.sep_input)

        # Example
        self.example_label = QLabel("Example: filename{sep}{suffix}.ext")
        self.example_label.setStyleSheet("color: gray; font-size: 11px;")
        layout.addRow("", self.example_label)

    def get_options(self) -> dict:
        return {
            "suffix": self.suffix_input.text(),
            "separator": self.sep_input.text()
        }

    def update_translations(self):
        self.suffix_label.setText(self.i18n.tr("suffix_label"))
        self.sep_label.setText(self.i18n.tr("separator"))

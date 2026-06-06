"""Footer widget for status and actions."""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Signal


class StatusFooter(QWidget):
    """Widget for status text, Rename, and Undo buttons."""
    
    rename_requested = Signal()
    undo_requested = Signal()

    def __init__(self, i18n):
        super().__init__()
        self.i18n = i18n
        self._create_layout()

    def _create_layout(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Status text
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label, 1)

        # Undo button
        self.undo_btn = QPushButton("Undo")
        self.undo_btn.clicked.connect(self.undo_requested.emit)
        self.undo_btn.setEnabled(False)
        layout.addWidget(self.undo_btn)

        # Rename button
        self.rename_btn = QPushButton("Rename")
        self.rename_btn.clicked.connect(self.rename_requested.emit)
        self.rename_btn.setEnabled(False)
        # Style it to look primary if possible without CSS, but QPushButton is simple.
        layout.addWidget(self.rename_btn)

    def set_status(self, text: str):
        self.status_label.setText(text)

    def set_rename_enabled(self, enabled: bool):
        self.rename_btn.setEnabled(enabled)

    def set_undo_enabled(self, enabled: bool):
        self.undo_btn.setEnabled(enabled)

    def update_translations(self):
        """Refresh labels based on current language."""
        self.undo_btn.setText(self.i18n.tr("undo"))
        self.rename_btn.setText(self.i18n.tr("rename"))
        # status text is usually set dynamically

"""Top bar widget for folder selection and language switching."""
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QFileDialog
)
from PySide6.QtCore import Signal


class TopBar(QWidget):
    """Widget for selecting folder and language."""
    
    folder_changed = Signal(str)
    refresh_requested = Signal()
    language_changed = Signal(str)
    update_requested = Signal()

    def __init__(self, i18n):
        super().__init__()
        self.i18n = i18n
        self._create_layout()

    def _create_layout(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Folder icon
        self.folder_icon = QLabel("📁")
        layout.addWidget(self.folder_icon)

        # Folder path input
        self.folder_input = QLineEdit()
        self.folder_input.setReadOnly(True)
        self.folder_input.setPlaceholderText("Select a folder...")
        layout.addWidget(self.folder_input, 1)

        # Browse button
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self._on_browse)
        layout.addWidget(self.browse_btn)

        # Refresh button
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_requested.emit)
        layout.addWidget(self.refresh_btn)

        # Update button (hidden by default)
        self.update_btn = QPushButton("🚀 Update")
        self.update_btn.setVisible(False)
        self.update_btn.setStyleSheet("background-color: #1D9E75; color: white; font-weight: bold;")
        self.update_btn.clicked.connect(self.update_requested.emit)
        layout.addWidget(self.update_btn)

        # Language selector
        self.lang_selector = QComboBox()
        self.lang_selector.addItems(["EN", "VI"])
        self.lang_selector.currentTextChanged.connect(self._on_lang_change)
        layout.addWidget(self.lang_selector)

    def set_folder(self, folder: str):
        self.folder_input.setText(folder)

    def set_language(self, lang: str):
        self.lang_selector.setCurrentText(lang.upper())

    def show_update_button(self, visible: bool = True):
        self.update_btn.setVisible(visible)

    def _on_browse(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folder_input.setText(folder)
            self.folder_changed.emit(folder)

    def _on_lang_change(self, text):
        self.language_changed.emit(text.lower())

    def update_translations(self):
        """Refresh labels based on current language."""
        self.folder_input.setPlaceholderText(self.i18n.tr("select_folder_placeholder"))
        self.browse_btn.setText(self.i18n.tr("browse"))
        self.refresh_btn.setText(self.i18n.tr("refresh"))
        self.update_btn.setText(f"🚀 {self.i18n.tr('update_available')}")
        # Note: lang_selector items are static codes EN/VI

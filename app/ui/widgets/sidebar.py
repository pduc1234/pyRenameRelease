"""Sidebar widget for extension filtering, sorting, and file selection."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, 
    QPushButton, QScrollArea, QFrame, QSizePolicy, QApplication
)
from PySide6.QtCore import Qt, Signal


class Sidebar(QWidget):
    """Sidebar for filtering, sorting, and selecting files."""
    
    filter_changed = Signal()
    sort_changed = Signal(str)
    selection_changed = Signal()

    def __init__(self, i18n):
        super().__init__()
        self.i18n = i18n
        self.selected_file_paths = set()
        self._last_clicked_row = -1
        self._create_layout()

    def _create_layout(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        # Title
        self.title_label = QLabel("Files")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.title_label)

        # Extensions section
        self.ext_label = QLabel("Extensions")
        self.ext_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.ext_label)

        self.ext_list = QListWidget()
        self.ext_list.setMinimumHeight(70)
        self.ext_list.setMaximumHeight(130)
        self.ext_list.itemChanged.connect(self._on_filter_changed)
        layout.addWidget(self.ext_list)

        # Sort section
        self.sort_label = QLabel("Sort by")
        self.sort_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.sort_label)

        sort_btn_layout = QHBoxLayout()
        self.sort_name_btn = QPushButton("Name")
        self.sort_name_btn.clicked.connect(lambda: self.sort_changed.emit("name"))
        self.sort_date_btn = QPushButton("Date")
        self.sort_date_btn.clicked.connect(lambda: self.sort_changed.emit("mtime"))
        self.sort_size_btn = QPushButton("Size")
        self.sort_size_btn.clicked.connect(lambda: self.sort_changed.emit("size"))
        
        sort_btn_layout.addWidget(self.sort_name_btn)
        sort_btn_layout.addWidget(self.sort_date_btn)
        sort_btn_layout.addWidget(self.sort_size_btn)
        layout.addLayout(sort_btn_layout)

        # Selection actions
        sel_btn_layout = QHBoxLayout()
        self.sel_all_btn = QPushButton("All")
        self.sel_all_btn.clicked.connect(self._on_select_all)
        self.sel_none_btn = QPushButton("None")
        self.sel_none_btn.clicked.connect(self._on_select_none)
        self.sel_invert_btn = QPushButton("Invert")
        self.sel_invert_btn.clicked.connect(self._on_select_invert)

        sel_btn_layout.addWidget(self.sel_all_btn)
        sel_btn_layout.addWidget(self.sel_none_btn)
        sel_btn_layout.addWidget(self.sel_invert_btn)
        layout.addLayout(sel_btn_layout)

        # Items list
        self.items_label = QLabel("Items")
        self.items_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.items_label)

        self.items_list = QListWidget()
        self.items_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.items_list.itemClicked.connect(self._on_item_clicked)
        self.items_list.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self.items_list)

    def _on_filter_changed(self):
        self.filter_changed.emit()

    def _on_item_clicked(self, item):
        row = self.items_list.row(item)
        modifiers = QApplication.keyboardModifiers()
        
        if (modifiers & Qt.ShiftModifier) and self._last_clicked_row != -1:
            # Multi-select range from anchor
            start = min(self._last_clicked_row, row)
            end = max(self._last_clicked_row, row)
            
            # Use the new state of the clicked item
            new_state = item.checkState()
            
            self.items_list.blockSignals(True)
            for i in range(start, end + 1):
                it = self.items_list.item(i)
                it.setCheckState(new_state)
                path = it.data(Qt.UserRole)
                if new_state == Qt.Checked:
                    self.selected_file_paths.add(path)
                else:
                    self.selected_file_paths.discard(path)
            self.items_list.blockSignals(False)
            self.selection_changed.emit()
        else:
            # Update anchor
            self._last_clicked_row = row

    def _on_item_changed(self, item):
        path = item.data(Qt.UserRole)
        if item.checkState() == Qt.Checked:
            self.selected_file_paths.add(path)
        else:
            self.selected_file_paths.discard(path)
        self.selection_changed.emit()

    def _on_select_all(self):
        self.items_list.blockSignals(True)
        for i in range(self.items_list.count()):
            item = self.items_list.item(i)
            item.setCheckState(Qt.Checked)
            path = item.data(Qt.UserRole)
            self.selected_file_paths.add(path)
        self.items_list.blockSignals(False)
        self.selection_changed.emit()

    def _on_select_none(self):
        self.items_list.blockSignals(True)
        for i in range(self.items_list.count()):
            item = self.items_list.item(i)
            item.setCheckState(Qt.Unchecked)
            path = item.data(Qt.UserRole)
            self.selected_file_paths.discard(path)
        self.items_list.blockSignals(False)
        self.selection_changed.emit()

    def _on_select_invert(self):
        self.items_list.blockSignals(True)
        for i in range(self.items_list.count()):
            item = self.items_list.item(i)
            new_state = Qt.Unchecked if item.checkState() == Qt.Checked else Qt.Checked
            item.setCheckState(new_state)
            path = item.data(Qt.UserRole)
            if new_state == Qt.Checked:
                self.selected_file_paths.add(path)
            else:
                self.selected_file_paths.discard(path)
        self.items_list.blockSignals(False)
        self.selection_changed.emit()

    def update_extensions(self, extensions: set[str]):
        self.ext_list.blockSignals(True)
        self.ext_list.clear()
        for ext in sorted(extensions):
            item = QListWidgetItem(f".{ext}" if ext else "no extension")
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)
            self.ext_list.addItem(item)
        self.ext_list.blockSignals(False)

    def get_active_extensions(self) -> list[str]:
        active = []
        for i in range(self.ext_list.count()):
            item = self.ext_list.item(i)
            if item.checkState() == Qt.Checked:
                text = item.text()
                active.append(text.lstrip("."))
        return active

    def update_items(self, files: list, preserve_selection: bool = True):
        self.items_list.blockSignals(True)
        self.items_list.clear()
        
        new_paths = {f.path for f in files}
        if not preserve_selection:
            self.selected_file_paths = set()
        else:
            # Keep only existing valid selections that still exist
            self.selected_file_paths &= new_paths

        for f in files:
            item = QListWidgetItem(f.full)
            item.setData(Qt.UserRole, f.path)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            
            state = Qt.Checked if f.path in self.selected_file_paths else Qt.Unchecked
            item.setCheckState(state)
            self.items_list.addItem(item)
            
        self.items_list.blockSignals(False)
        self.selection_changed.emit()

    def update_translations(self):
        self.title_label.setText(self.i18n.tr("files"))
        self.ext_label.setText(self.i18n.tr("extensions"))
        self.sort_label.setText(self.i18n.tr("sort_by"))
        self.items_label.setText(self.i18n.tr("items"))
        self.sel_all_btn.setText(self.i18n.tr("all"))
        self.sel_none_btn.setText(self.i18n.tr("none"))
        self.sel_invert_btn.setText(self.i18n.tr("invert"))

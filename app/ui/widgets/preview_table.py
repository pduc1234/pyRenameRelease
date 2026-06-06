"""Preview table widget for showing rename results."""
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


class PreviewTable(QTableWidget):
    """Table to display old name -> new name mapping with status."""

    def __init__(self, i18n):
        super().__init__()
        self.i18n = i18n
        self._setup_table()

    def _create_layout(self):
        # QTableWidget doesn't need a layout call like this usually
        pass

    def _setup_table(self):
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["Old Name", "", "New Name", "Status"])
        
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.NoSelection)
        self.verticalHeader().setVisible(False)

    def update_pairs(self, pairs: list):
        self.setRowCount(len(pairs))
        for i, p in enumerate(pairs):
            # Old Name
            self.setItem(i, 0, QTableWidgetItem(p.old_name))
            
            # Arrow
            arrow_item = QTableWidgetItem("→")
            arrow_item.setTextAlignment(Qt.AlignCenter)
            self.setItem(i, 1, arrow_item)
            
            # New Name
            new_item = QTableWidgetItem(p.new_name)
            if p.status == "error":
                new_item.setForeground(QColor("red"))
            elif p.status == "warning":
                new_item.setForeground(QColor("orange"))
            elif p.status == "renamed":
                new_item.setForeground(QColor("#1D9E75"))
            else:
                new_item.setForeground(QColor("#1D9E75")) # Custom green from before
            self.setItem(i, 2, new_item)
            
            # Status
            status_text = ""
            if p.message:
                status_text = self.i18n.tr(p.message)
            else:
                status_text = self.i18n.tr(f"status_{p.status}")
                
            status_item = QTableWidgetItem(status_text)
            if p.status == "error":
                status_item.setForeground(QColor("red"))
            elif p.status == "renamed":
                status_item.setForeground(QColor("#1D9E75"))
            self.setItem(i, 3, status_item)

    def update_translations(self):
        self.setHorizontalHeaderLabels([
            self.i18n.tr("old_name"),
            "",
            self.i18n.tr("new_name"),
            self.i18n.tr("status")
        ])

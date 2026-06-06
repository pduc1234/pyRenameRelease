"""Style constants and helpers for PySide6."""
from PySide6.QtGui import QFont


def get_base_font(size: int = 10) -> QFont:
    """Get standard app font."""
    font = QFont("Segoe UI", size)
    return font


def apply_app_font(app):
    """Apply standard font to the whole application."""
    font = get_base_font(10.5)
    app.setFont(font)

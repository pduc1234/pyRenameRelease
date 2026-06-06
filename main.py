"""Main entry point for File Renamer."""
import sys
import ctypes
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from app.ui.main_window import MainWindow
from app.ui.styles import apply_app_font
from app.ui.i18n import resource_path


def main():
    # Set AppUserModelID for Windows taskbar grouping
    if sys.platform == "win32":
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("FileRenamer.FileRenamer")
        except Exception:
            pass

    app = QApplication(sys.argv)
    apply_app_font(app)
    
    # Load and set application icon
    icon_path = resource_path("assets/app.ico")
    if icon_path.exists():
        icon = QIcon(str(icon_path))
        app.setWindowIcon(icon)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

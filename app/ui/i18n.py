"""Translation manager for PySide6."""
import json
from pathlib import Path
import sys
from typing import Dict, Any


def resource_path(relative_path: str) -> Path:
    """Get absolute path to resource, works for dev and for PyInstaller."""
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path
    
    # Path to project root (one level above app/)
    base_path = Path(__file__).resolve().parent.parent.parent
    
    # Try project root
    p = base_path / relative_path
    if p.exists():
        return p
        
    # Try inside app/ folder (common for i18n in dev)
    p = base_path / "app" / relative_path
    return p


class I18nManager:
    """Manages translations and current language."""

    def __init__(self, language: str = "en"):
        self.language = language
        self.strings: Dict[str, str] = {}
        self.load_language(language)

    def load_language(self, language: str):
        """Load translation JSON file."""
        self.language = language
        file_path = resource_path(f"i18n/{language}.json")
        try:
            if file_path.exists():
                self.strings = json.loads(file_path.read_text(encoding="utf-8"))
            else:
                self.strings = {}
        except Exception:
            self.strings = {}

    def tr(self, key: str, **kwargs) -> str:
        """Translate a key with optional formatting."""
        text = self.strings.get(key, key)
        if kwargs:
            try:
                return text.format(**kwargs)
            except (KeyError, ValueError):
                return text
        return text

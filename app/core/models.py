"""Core data models."""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class FileEntry:
    """Represents a file in a folder."""
    name: str  # stem
    ext: str   # suffix (includes dot)
    full: str  # name
    path: str  # absolute path
    size: int
    mtime: float

    @property
    def extension_no_dot(self) -> str:
        return self.ext.lstrip(".").lower()


@dataclass
class RenamePair:
    """Represents a rename operation."""
    old_name: str
    new_name: str
    status: str = "valid"  # valid, warning, error
    message: Optional[str] = None

"""File scanning, filtering, and sorting."""
from pathlib import Path
from typing import Optional, List
from .models import FileEntry


class FileScanner:
    """Manages file scanning, filtering, and sorting."""

    def __init__(self, folder: str):
        """Initialize with a folder path."""
        self.folder = Path(folder) if folder else None
        self.files: List[FileEntry] = []
        self.extensions: set[str] = set()

    def scan(self) -> List[FileEntry]:
        """
        Scan folder and return list of FileEntry objects.
        """
        if not self.folder or not self.folder.is_dir():
            self.files = []
            self.extensions = set()
            return []

        self.files = []
        self.extensions = set()

        try:
            for entry in self.folder.iterdir():
                if not entry.is_file():
                    continue

                stat = entry.stat()
                file_entry = FileEntry(
                    name=entry.stem,
                    ext=entry.suffix,
                    full=entry.name,
                    path=str(entry.absolute()),
                    size=stat.st_size,
                    mtime=stat.st_mtime,
                )
                self.extensions.add(file_entry.extension_no_dot)
                self.files.append(file_entry)
        except (PermissionError, OSError):
            pass

        return self.files

    def filter(self, exts: Optional[List[str]] = None) -> List[FileEntry]:
        """
        Filter files by extensions (without dot).
        """
        if not exts:
            return self.files[:]

        exts_lower = [e.lower() for e in exts]
        return [f for f in self.files if f.extension_no_dot in exts_lower]

    def sort(self, files: List[FileEntry], by: str = "name", reverse: bool = False) -> List[FileEntry]:
        """
        Sort files by specified field.
        """
        if by == "name":
            return sorted(files, key=lambda f: f.name.lower(), reverse=reverse)
        elif by == "mtime":
            return sorted(files, key=lambda f: f.mtime, reverse=reverse)
        elif by == "size":
            return sorted(files, key=lambda f: f.size, reverse=reverse)
        else:
            return files[:]

"""Undo management and history tracking."""
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional


class UndoManager:
    """Manages rename history for undo functionality."""

    def __init__(self, history_path: Optional[Path] = None):
        self.history_path = history_path or Path.home() / ".file_renamer_history.json"
        self.max_entries = 10

    def _normalize(self, folder: str) -> str:
        return str(Path(folder).resolve())

    def _load_raw(self) -> List[dict]:
        if not self.history_path.exists():
            return []
        try:
            data = json.loads(self.history_path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            return []

    def _write_raw(self, data: List[dict]) -> bool:
        try:
            self.history_path.parent.mkdir(parents=True, exist_ok=True)
            self.history_path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            return True
        except OSError:
            return False

    def save(self, folder: str, pairs: List[Tuple[str, str]]) -> bool:
        """Save a rename operation to history."""
        data = self._load_raw()
        data.append({
            "ts": datetime.now().isoformat(timespec="seconds"),
            "folder": self._normalize(folder),
            "pairs": [[o, n] for o, n in pairs],
        })
        data = data[-self.max_entries:]
        return self._write_raw(data)

    def load_last(self, folder: str) -> Optional[List[Tuple[str, str]]]:
        """Load the most recent rename operation for the folder."""
        folder_norm = self._normalize(folder)
        data = self._load_raw()

        for entry in reversed(data):
            if self._normalize(entry.get("folder", "")) == folder_norm:
                return [tuple(p) for p in entry.get("pairs", [])]
        return None

    def undo(self, folder: str) -> Tuple[bool, Optional[str]]:
        """Undo the most recent rename operation for the folder."""
        folder_norm = self._normalize(folder)
        data = self._load_raw()

        target_idx = None
        for i in range(len(data) - 1, -1, -1):
            if self._normalize(data[i].get("folder", "")) == folder_norm:
                target_idx = i
                break

        if target_idx is None:
            return False, "No rename history for this folder"

        pairs = data[target_idx].get("pairs", [])
        folder_path = Path(folder_norm)
        errors = []

        for old, new in pairs:
            src = folder_path / new
            dst = folder_path / old

            if not src.exists():
                errors.append(f"File not found: {new}")
                continue

            try:
                src.rename(dst)
            except OSError as e:
                errors.append(str(e))

        if errors:
            return False, "; ".join(errors)

        data.pop(target_idx)
        self._write_raw(data)
        return True, None

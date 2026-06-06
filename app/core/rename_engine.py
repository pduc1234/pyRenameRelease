"""Rename execution engine."""
import uuid
from pathlib import Path
from typing import List, Tuple, Optional
from .models import RenamePair
from .undo_manager import UndoManager


class RenameEngine:
    """Executes rename operations with atomic rollback."""

    def __init__(self, undo_manager: UndoManager):
        self.undo_manager = undo_manager

    def execute(self, folder: str, pairs: List[RenamePair]) -> Tuple[bool, Optional[str]]:
        """
        Execute rename operations with automatic rollback on failure.
        """
        folder_path = Path(folder).resolve()

        # 1. Filter valid pairs and ignore no-ops
        active_pairs = [p for p in pairs if p.status != "error" and p.old_name.lower() != p.new_name.lower()]
        if not active_pairs:
            return True, "No changes to apply"

        # 2. Convert to tuple list for atomic engine
        tuple_pairs = [(p.old_name, p.new_name) for p in active_pairs]

        # 3. Perform atomic rename
        ok, msg = self._do_rename_atomic(folder_path, tuple_pairs)
        if not ok:
            return False, msg

        # 4. Save to history
        if not self.undo_manager.save(str(folder_path), tuple_pairs):
            return True, "Rename succeeded, but failed to save history (Undo will not be available)."
        
        return True, None

    def _do_rename_atomic(
        self, folder: Path, pairs: List[Tuple[str, str]]
    ) -> Tuple[bool, Optional[str]]:
        """
        Two-phase atomic rename: old → tmp (phase 1), tmp → new (phase 2).
        """
        temp_map: List[Tuple[Path, Path, Path]] = []

        for old, new in pairs:
            tmp = folder / f"__frtmp_{uuid.uuid4().hex}__{old}"
            temp_map.append((folder / old, tmp, folder / new))

        renamed_phase1: List[Tuple[Path, Path]] = []
        try:
            for old_path, tmp_path, _ in temp_map:
                old_path.rename(tmp_path)
                renamed_phase1.append((old_path, tmp_path))
        except OSError as e:
            for orig, tmp in reversed(renamed_phase1):
                try:
                    tmp.rename(orig)
                except Exception:
                    pass
            return False, f"Phase 1 error: {e}"

        renamed_phase2: List[Tuple[Path, Path]] = []
        try:
            for _, tmp_path, new_path in temp_map:
                new_path.parent.mkdir(parents=True, exist_ok=True) # Ensure dir exists
                tmp_path.rename(new_path)
                renamed_phase2.append((tmp_path, new_path))
        except OSError as e:
            for tmp, new in reversed(renamed_phase2):
                try:
                    new.rename(tmp)
                except Exception:
                    pass
            for orig, tmp in reversed(renamed_phase1):
                try:
                    tmp.rename(orig)
                except Exception:
                    pass
            return False, f"Phase 2 error: {e}"

        return True, None

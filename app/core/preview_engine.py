"""Preview generation logic."""
from pathlib import Path
from typing import List, Optional, Dict
from .models import FileEntry, RenamePair
from .video_metadata import get_resolution
import re


# Windows forbidden characters in filenames
FORBIDDEN_CHARS = set('\\/:*?"<>|')

# Windows reserved device names
_WIN_RESERVED = frozenset({
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
})


class PreviewEngine:
    """Generates preview of rename operations."""

    def sanitize_filename(self, filename: str) -> str:
        """Remove/replace forbidden Windows characters from filename."""
        result = "".join("_" if c in FORBIDDEN_CHARS else c for c in filename)
        result = result.rstrip(". ")
        if not result:
            result = "_"
        return result

    def validate_new_name(self, new_name: str) -> Optional[str]:
        """Validate filename against Windows rules."""
        if not new_name or new_name in (".", ".."):
            return "Filename cannot be empty or . / .."
        
        stem = Path(new_name).stem.upper()
        if stem in _WIN_RESERVED:
            return f"Reserved Windows device name ({stem})"
        
        if new_name.endswith((".", " ")):
            return "Cannot end with a dot or space"

        return None

    def validate_pattern(self, pattern: str) -> Optional[str]:
        """Validate rename pattern placeholders."""
        valid_vars = {"n", "res", "name"}
        try:
            placeholders = re.findall(r"\{(.*?)\}", pattern)
            for p in placeholders:
                if ":" in p:
                    return f"Format specifiers like '{{n:02d}}' not supported. Use {{n}}, {{res}}, {{name}}."
                if p not in valid_vars:
                    return f"Invalid variable '{{{p}}}'. Only {{n}}, {{res}}, {{name}} allowed."
        except Exception as e:
            return str(e)
        return None

    def preview_sequential(
        self, 
        files: List[FileEntry], 
        start: int = 1, 
        pad: int = 1, 
        prefix: str = "",
        pattern: str = "{n}"
    ) -> List[RenamePair]:
        """Generate sequential naming preview."""
        pattern_err = self.validate_pattern(pattern)
        
        pairs = []
        for i, file in enumerate(files):
            n_str = str(start + i).zfill(pad)
            
            try:
                new_name_base = pattern.format_map({"n": n_str, "res": "?x?", "name": file.name})
                new_name = f"{prefix}{new_name_base}{file.ext}"
                new_name = self.sanitize_filename(new_name)
                
                pair = RenamePair(old_name=file.full, new_name=new_name)
                
                if pattern_err:
                    pair.status = "error"
                    pair.message = pattern_err
                else:
                    err = self.validate_new_name(new_name)
                    if err:
                        pair.status = "error"
                        pair.message = err
                
                pairs.append(pair)
            except Exception as e:
                pairs.append(RenamePair(old_name=file.full, new_name=file.full, status="error", message=str(e)))
        
        return self._check_batch_conflicts(pairs)

    def preview_suffix(
        self, files: List[FileEntry], suffix: str = "", separator: str = " - "
    ) -> List[RenamePair]:
        """Generate suffix naming preview."""
        pairs = []
        for file in files:
            new_name = f"{file.name}{separator}{suffix}{file.ext}"
            new_name = self.sanitize_filename(new_name)
            
            pair = RenamePair(old_name=file.full, new_name=new_name)
            err = self.validate_new_name(new_name)
            if err:
                pair.status = "error"
                pair.message = err
            pairs.append(pair)
            
        return self._check_batch_conflicts(pairs)

    def preview_video(
        self, 
        files: List[FileEntry], 
        pattern: str = "{n} - {res}", 
        start: int = 1, 
        auto_detect: bool = False, 
        manual_res: str = "1920x1080",
        prefix: str = ""
    ) -> List[RenamePair]:
        """Generate video metadata naming preview."""
        pattern_err = self.validate_pattern(pattern)
        
        # Determine effective pattern
        effective_pattern = pattern
        if prefix.strip() and not pattern.startswith(f"{prefix.strip()}_"):
            effective_pattern = f"{prefix.strip()}_{pattern}"

        pairs = []
        for i, file in enumerate(files):
            res = manual_res
            if auto_detect:
                detected = get_resolution(file.path)
                if detected:
                    res = detected
                else:
                    res = "?x?"  # Or handle as warning
            
            try:
                new_name_base = effective_pattern.format_map({"n": start + i, "res": res, "name": file.name})
                new_name = f"{new_name_base}{file.ext}"
                new_name = self.sanitize_filename(new_name)
                
                pair = RenamePair(old_name=file.full, new_name=new_name)
                
                if pattern_err:
                    pair.status = "error"
                    pair.message = pattern_err
                else:
                    err = self.validate_new_name(new_name)
                    if err:
                        pair.status = "error"
                        pair.message = err
                    elif res == "?x?":
                        pair.status = "warning"
                        pair.message = "resolution_detection_failed"
                
                pairs.append(pair)
            except Exception as e:
                pairs.append(RenamePair(old_name=file.full, new_name=file.full, status="error", message=str(e)))

        return self._check_batch_conflicts(pairs)

    def _check_batch_conflicts(self, pairs: List[RenamePair]) -> List[RenamePair]:
        """Check for duplicate new names within the same batch."""
        new_names_count = {}
        for p in pairs:
            if p.status != "error":
                name_lower = p.new_name.lower()
                new_names_count[name_lower] = new_names_count.get(name_lower, 0) + 1
        
        for p in pairs:
            if p.status != "error":
                if new_names_count.get(p.new_name.lower(), 0) > 1:
                    p.status = "error"
                    p.message = "duplicate_name_in_batch"
                elif p.new_name.lower() == p.old_name.lower():
                    p.status = "warning"
                    p.message = "same_as_old_name"
        
        return pairs

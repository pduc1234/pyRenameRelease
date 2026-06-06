"""GitHub Release update checker logic."""
import json
import urllib.request
from typing import Optional, Dict, Any
from ..app_info import APP_VERSION, GITHUB_OWNER, GITHUB_REPO


class UpdateChecker:
    """Checks for new versions on GitHub Releases."""

    API_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"

    def __init__(self):
        self.latest_release: Optional[Dict[str, Any]] = None

    def check_for_update(self) -> Optional[Dict[str, Any]]:
        """
        Fetch latest release info from GitHub.
        
        Returns:
            Dict with 'version', 'url', 'body' if a newer version exists, else None.
        """
        try:
            # Set a user-agent to avoid GitHub API block
            headers = {"User-Agent": "FileRenamer-App"}
            req = urllib.request.Request(self.API_URL, headers=headers)
            
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                
                tag_name = data.get("tag_name", "").lstrip("v")
                if self._is_newer(tag_name, APP_VERSION):
                    self.latest_release = {
                        "version": tag_name,
                        "url": data.get("html_url"),
                        "body": data.get("body", ""),
                    }
                    return self.latest_release
        except Exception:
            # Silent fail for background check
            pass
        return None

    def _is_newer(self, latest: str, current: str) -> bool:
        """Simple semver comparison (x.y.z)."""
        try:
            l_parts = [int(p) for p in latest.split(".")]
            c_parts = [int(p) for p in current.split(".")]
            # Pad with zeros if needed
            max_len = max(len(l_parts), len(c_parts))
            l_parts += [0] * (max_len - len(l_parts))
            c_parts += [0] * (max_len - len(c_parts))
            return l_parts > c_parts
        except (ValueError, AttributeError):
            return latest != current

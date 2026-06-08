"""GitHub Release update checker logic using signed manifest."""
import urllib.request
import urllib.error
from typing import Optional
from ..app_info import APP_VERSION, GITHUB_OWNER, GITHUB_REPO
from .update_manifest import UpdateManifest
from .update_security import verify_manifest_signature


class UpdateChecker:
    """Checks for new versions on GitHub Releases using a signed manifest."""

    BASE_URL = f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest/download"
    MANIFEST_URL = f"{BASE_URL}/latest.json"
    SIGNATURE_URL = f"{BASE_URL}/latest.json.sig"

    def __init__(self):
        self.latest_manifest: Optional[UpdateManifest] = None

    def check_for_update(self) -> Optional[UpdateManifest]:
        """
        Fetch and verify latest manifest from GitHub.
        
        Returns:
            UpdateManifest if a verified newer version exists, else None.
        """
        try:
            # 1. Fetch manifest and signature
            manifest_bytes = self._fetch_url(self.MANIFEST_URL)
            signature_bytes = self._fetch_url(self.SIGNATURE_URL)
            
            if not manifest_bytes or not signature_bytes:
                return None

            # 2. Verify signature
            if not verify_manifest_signature(manifest_bytes, signature_bytes):
                print("Update manifest signature verification failed!")
                return None

            # 3. Parse manifest
            manifest = UpdateManifest.from_json(manifest_bytes)
            
            # 4. Compare versions
            if self._is_newer(manifest.version, APP_VERSION):
                self.latest_manifest = manifest
                return manifest
                
        except Exception as e:
            # Silent fail for background check, but log for debugging if needed
            print(f"Update check failed: {e}")
            pass
        return None

    def _fetch_url(self, url: str) -> Optional[bytes]:
        """Fetch raw bytes from URL."""
        headers = {"User-Agent": "FileRenamer-App"}
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.read()
        except urllib.error.URLError:
            return None

    def _is_newer(self, latest: str, current: str) -> bool:
        """Simple semver comparison (x.y.z)."""
        try:
            l_parts = [int(p) for p in latest.split(".")]
            c_parts = [int(p) for p in current.split(".")]
            max_len = max(len(l_parts), len(c_parts))
            l_parts += [0] * (max_len - len(l_parts))
            c_parts += [0] * (max_len - len(c_parts))
            return l_parts > c_parts
        except (ValueError, AttributeError):
            return latest != current

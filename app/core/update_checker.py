"""GitHub Release update checker logic using signed manifest."""
import json
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
    API_LATEST_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"

    def __init__(self):
        self.latest_manifest: Optional[UpdateManifest] = None

    def check_for_update(self) -> Optional[UpdateManifest]:
        """
        Fetch and verify latest manifest from GitHub.
        
        Returns:
            UpdateManifest if a verified newer version exists, else None.
        """
        try:
            update = self._check_signed_manifest()
            if update:
                return update

            update = self._check_github_latest_release()
            if update:
                return update

        except Exception as e:
            # Silent fail for background check, but log for debugging if needed
            print(f"Update check failed: {e}")
        return None

    def _check_signed_manifest(self) -> Optional[UpdateManifest]:
        """Check signed latest.json assets from the latest GitHub Release."""
        try:
            manifest_bytes = self._fetch_url(self.MANIFEST_URL)
            signature_bytes = self._fetch_url(self.SIGNATURE_URL)

            if not manifest_bytes or not signature_bytes:
                return None

            if not verify_manifest_signature(manifest_bytes, signature_bytes):
                print("Update manifest signature verification failed!")
                return None

            manifest = UpdateManifest.from_json(manifest_bytes)

            if self._is_newer(manifest.version, APP_VERSION):
                self.latest_manifest = manifest
                return manifest

        except Exception as e:
            print(f"Signed update manifest check failed: {e}")
        return None

    def _check_github_latest_release(self) -> Optional[UpdateManifest]:
        """Fallback to GitHub Releases API when signed manifest assets are missing."""
        release_bytes = self._fetch_url(self.API_LATEST_URL)
        if not release_bytes:
            return None

        data = json.loads(release_bytes.decode("utf-8"))
        version = str(data.get("tag_name", "")).lstrip("v")
        if not version or not self._is_newer(version, APP_VERSION):
            return None

        asset = self._find_setup_asset(data.get("assets", []))
        package_url = ""
        sha256 = ""
        if asset:
            package_url = asset.get("browser_download_url", "")
            digest = asset.get("digest", "")
            if isinstance(digest, str) and digest.startswith("sha256:"):
                sha256 = digest.split(":", 1)[1]

        manifest = UpdateManifest(
            version=version,
            package_url=package_url,
            sha256=sha256,
            published_at=data.get("published_at", ""),
            notes_url=data.get("html_url"),
        )
        self.latest_manifest = manifest
        return manifest

    def _find_setup_asset(self, assets: list) -> Optional[dict]:
        """Find the Windows setup asset in a GitHub release payload."""
        for asset in assets:
            if asset.get("name") == "FileRenamer-Setup.exe":
                return asset
        for asset in assets:
            name = str(asset.get("name", "")).lower()
            if name.endswith(".exe") and "setup" in name:
                return asset
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

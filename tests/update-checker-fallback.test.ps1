$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")

$python = @'
import json
import sys

sys.path.insert(0, r"__REPO_ROOT__")

from app.core.update_checker import UpdateChecker

checker = UpdateChecker()

latest_payload = {
    "tag_name": "v9.9.9",
    "html_url": "https://github.com/pduc1234/pyRenameRelease/releases/tag/v9.9.9",
    "published_at": "2026-06-08T00:00:00Z",
    "assets": [
        {
            "name": "FileRenamer-Setup.exe",
            "browser_download_url": "https://github.com/pduc1234/pyRenameRelease/releases/download/v9.9.9/FileRenamer-Setup.exe",
        }
    ],
}

def fake_fetch(url):
    if url.endswith("/latest.json") or url.endswith("/latest.json.sig"):
        return None
    if url == checker.API_LATEST_URL:
        return json.dumps(latest_payload).encode("utf-8")
    raise AssertionError(f"Unexpected URL: {url}")

checker._fetch_url = fake_fetch
manifest = checker.check_for_update()

if manifest is None:
    raise AssertionError("GitHub Releases API fallback should detect newer releases when signed manifest assets are missing.")
if manifest.version != "9.9.9":
    raise AssertionError(f"Unexpected fallback version: {manifest.version}")
if manifest.package_url != latest_payload["assets"][0]["browser_download_url"]:
    raise AssertionError("Fallback update should use FileRenamer-Setup.exe asset URL.")
if manifest.notes_url != latest_payload["html_url"]:
    raise AssertionError("Fallback update should keep release page URL.")
if manifest.sha256:
    raise AssertionError("Fallback manifest should not invent a hash when GitHub does not provide one.")

print("Update checker fallback checks passed.")
'@

$python = $python.Replace("__REPO_ROOT__", $repoRoot.Path.Replace("\", "\\"))
$python | & (Join-Path $repoRoot ".venv\Scripts\python.exe") -
if ($LASTEXITCODE -ne 0) {
    throw "Update checker fallback checks failed."
}

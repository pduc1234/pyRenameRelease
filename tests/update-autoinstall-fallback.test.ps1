$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")

$python = @'
import inspect
import sys

sys.path.insert(0, r"__REPO_ROOT__")

from app.ui.main_window import MainWindow

source = inspect.getsource(MainWindow._on_update_requested)

if "or not self.latest_release.sha256" in source:
    raise AssertionError("Update action must not open GitHub just because a fallback release has no SHA-256.")
if "if self.latest_release.sha256" not in source:
    raise AssertionError("Update action should verify SHA-256 when the release provides one.")
if "verify_sha256" not in source:
    raise AssertionError("Update action must keep hash verification for signed/hashed releases.")

print("Update auto-install fallback checks passed.")
'@

$python = $python.Replace("__REPO_ROOT__", $repoRoot.Path.Replace("\", "\\"))
$python | & (Join-Path $repoRoot ".venv\Scripts\python.exe") -
if ($LASTEXITCODE -ne 0) {
    throw "Update auto-install fallback checks failed."
}

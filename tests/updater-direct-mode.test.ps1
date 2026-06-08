$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")

$python = @'
import inspect
import sys

sys.path.insert(0, r"__REPO_ROOT__")

from app.updater import updater_main

source = inspect.getsource(updater_main)

if 'parser.add_argument("--package", required=True' in source:
    raise AssertionError("Updater direct mode should not require --package.")
if "download_latest_package" not in source:
    raise AssertionError("Updater should download the latest package when run directly.")
if "get_default_install_dir" not in source:
    raise AssertionError("Updater direct mode should resolve the installed app directory by itself.")

print("Updater direct mode checks passed.")
'@

$python = $python.Replace("__REPO_ROOT__", $repoRoot.Path.Replace("\", "\\"))
$python | & (Join-Path $repoRoot ".venv\Scripts\python.exe") -
if ($LASTEXITCODE -ne 0) {
    throw "Updater direct mode checks failed."
}

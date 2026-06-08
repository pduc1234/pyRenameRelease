$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")

$python = @'
import sys

sys.path.insert(0, r"__REPO_ROOT__")

from app.updater import updater_main

class FakeProcess:
    def is_running(self):
        return True

def fake_process(pid):
    return FakeProcess()

updater_main.psutil.Process = fake_process
updater_main.time.sleep = lambda seconds: None

result = updater_main.wait_for_process_exit(12345, timeout=2)
if result is not False:
    raise AssertionError("Updater should return False after timeout when parent process is still running.")

print("Updater wait checks passed.")
'@

$python = $python.Replace("__REPO_ROOT__", $repoRoot.Path.Replace("\", "\\"))
$python | & (Join-Path $repoRoot ".venv\Scripts\python.exe") -
if ($LASTEXITCODE -ne 0) {
    throw "Updater wait checks failed."
}

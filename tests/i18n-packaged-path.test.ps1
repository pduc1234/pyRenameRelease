$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")

$python = @'
import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, r"__REPO_ROOT__")

from app.ui.i18n import I18nManager

temp_root = Path(tempfile.mkdtemp(prefix="FileRenamer_i18n_test_"))
try:
    packaged_i18n = temp_root / "app" / "i18n"
    packaged_i18n.mkdir(parents=True)
    (packaged_i18n / "en.json").write_text(
        json.dumps({"old_name": "Old Name", "quick_guide": "Quick Guide"}),
        encoding="utf-8",
    )

    sys._MEIPASS = str(temp_root)
    manager = I18nManager("en")

    if manager.tr("old_name") != "Old Name":
        raise AssertionError("Packaged i18n path app/i18n/en.json was not loaded.")
    if manager.tr("quick_guide") != "Quick Guide":
        raise AssertionError("Guide translations were not loaded from packaged i18n.")
finally:
    if hasattr(sys, "_MEIPASS"):
        delattr(sys, "_MEIPASS")
    shutil.rmtree(temp_root, ignore_errors=True)

print("Packaged i18n path checks passed.")
'@

$python = $python.Replace("__REPO_ROOT__", $repoRoot.Path.Replace("\", "\\"))
$python | & (Join-Path $repoRoot ".venv\Scripts\python.exe") -
if ($LASTEXITCODE -ne 0) {
    throw "Packaged i18n path checks failed."
}

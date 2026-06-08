$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")

$python = @'
import sys

sys.path.insert(0, r"__REPO_ROOT__")

from app.ui.tabs.guide_tab import GuideTab

sample = "\u2022 First line\n\u2022 Second line\n  - Nested detail"
html = GuideTab.format_step_text(sample)

if "<ul>" not in html or "</ul>" not in html:
    raise AssertionError("Guide step text should render as a real HTML list.")
if html.count("<li>") != 3:
    raise AssertionError(f"Expected 3 list items, got: {html}")
if "\u2022" in html:
    raise AssertionError("Guide HTML should not keep inline bullet separators.")
if "<br>" in html:
    raise AssertionError("Guide HTML should use block/list markup instead of raw <br> line breaks.")

print("Guide formatting checks passed.")
'@

$python = $python.Replace("__REPO_ROOT__", $repoRoot.Path.Replace("\", "\\"))
$python | & (Join-Path $repoRoot ".venv\Scripts\python.exe") -
if ($LASTEXITCODE -ne 0) {
    throw "Guide formatting checks failed."
}

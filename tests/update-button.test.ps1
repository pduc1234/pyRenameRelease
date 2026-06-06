$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$topBarSource = Get-Content -LiteralPath (Join-Path $repoRoot "app\ui\widgets\top_bar.py") -Raw
$mainWindowSource = Get-Content -LiteralPath (Join-Path $repoRoot "app\ui\main_window.py") -Raw

function Assert-Contains {
    param(
        [string] $Haystack,
        [string] $Needle,
        [string] $Message
    )

    if (-not $Haystack.Contains($Needle)) {
        throw $Message
    }
}

Assert-Contains $mainWindowSource "self.top_bar.update_requested.connect(self._on_update_requested)" "Update button signal must open the update dialog."
Assert-Contains $topBarSource "Qt.PointingHandCursor" "Update button must use a pointing hand cursor on hover."

Write-Host "Update button wiring checks passed."

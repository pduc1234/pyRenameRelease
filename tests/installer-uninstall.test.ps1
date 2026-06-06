$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$stubPath = Join-Path $repoRoot "installer\InstallerStub.cs"
$source = Get-Content -LiteralPath $stubPath -Raw

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

Assert-Contains $source "IsUninstallMode" "Installer stub must support uninstall mode."
Assert-Contains $source "Uninstall FileRenamer.exe" "Installer must create an uninstall executable after install."
Assert-Contains $source "CurrentVersion\Uninstall\FileRenamer" "Installer must register FileRenamer in HKCU uninstall entries."
Assert-Contains $source "DeleteUninstallRegistryEntry" "Uninstaller must remove the HKCU uninstall registry entry."

Write-Host "Installer uninstall metadata checks passed."

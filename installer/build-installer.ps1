$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$appDir = Join-Path $repoRoot "dist\FileRenamer"
$outputPath = Join-Path $repoRoot "dist\FileRenamer-Setup.exe"
$packageDir = Join-Path $repoRoot "build\installer"
$payloadZip = Join-Path $packageDir "FileRenamer.zip"
$stubPath = Join-Path $packageDir "FileRenamerInstallerStub.exe"
$cscPath = Join-Path $env:SystemRoot "Microsoft.NET\Framework64\v4.0.30319\csc.exe"
$marker = [Text.Encoding]::ASCII.GetBytes("`n--FILERENAMER-PAYLOAD-V1--`n")

if (-not (Test-Path -LiteralPath (Join-Path $appDir "FileRenamer.exe"))) {
    throw "Build output not found. Run PyInstaller before building the installer."
}

if (Test-Path -LiteralPath $packageDir) {
    Remove-Item -LiteralPath $packageDir -Recurse -Force
}

New-Item -ItemType Directory -Path $packageDir -Force | Out-Null

if (Test-Path -LiteralPath $payloadZip) {
    Remove-Item -LiteralPath $payloadZip -Force
}

Compress-Archive -LiteralPath $appDir -DestinationPath $payloadZip -Force

if (-not (Test-Path -LiteralPath $cscPath)) {
    throw "C# compiler not found: $cscPath"
}

& $cscPath `
    /nologo `
    /target:winexe `
    /platform:x64 `
    /optimize+ `
    "/win32icon:$(Join-Path $repoRoot "assets\app.ico")" `
    "/reference:System.IO.Compression.dll" `
    "/reference:System.IO.Compression.FileSystem.dll" `
    "/reference:System.Windows.Forms.dll" `
    "/out:$stubPath" `
    (Join-Path $PSScriptRoot "InstallerStub.cs")

if (Test-Path -LiteralPath $outputPath) {
    Remove-Item -LiteralPath $outputPath -Force
}

$outputStream = [IO.File]::Create($outputPath)
try {
    $stubStream = [IO.File]::OpenRead($stubPath)
    try {
        $stubStream.CopyTo($outputStream)
    }
    finally {
        $stubStream.Dispose()
    }

    $outputStream.Write($marker, 0, $marker.Length)

    $payloadStream = [IO.File]::OpenRead($payloadZip)
    try {
        $payloadStream.CopyTo($outputStream)
    }
    finally {
        $payloadStream.Dispose()
    }
}
finally {
    $outputStream.Dispose()
}

if (-not (Test-Path -LiteralPath $outputPath)) {
    throw "Installer was not created: $outputPath"
}

Write-Host "Installer created: $outputPath"

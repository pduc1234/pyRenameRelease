# File Renamer / Trinh Doi Ten File

Version: `0.2.4`

File Renamer is a Windows desktop app for safely renaming many files at once. It supports live preview, undo, video-resolution naming, bilingual UI, a Windows installer, and GitHub Releases based update checks.

File Renamer la ung dung desktop Windows de doi ten file hang loat an toan. App co xem truoc, hoan tac, doi ten theo do phan giai video, giao dien Anh/Viet, installer Windows va co che kiem tra cap nhat qua GitHub Releases.

---

## Highlights

- Batch rename files with validation before applying changes.
- Sequential numbering with prefix, zero padding, and custom pattern.
- Add suffix mode with configurable separator.
- Video format mode with `{n}`, `{res}`, and `{name}` variables.
- Optional video prefix helper for names such as `FFF_1 - 1920x1080.mp4`.
- Live preview table with old name, new name, and status.
- Undo for the latest successful rename operation.
- Folder selection by Browse, drag and drop, or pasted path.
- Resizable rename controls and preview area.
- Separate full-size Guide tab for onboarding/new users.
- English and Vietnamese UI.
- GitHub Releases update check with signed manifest support and safe fallback.
- Windows user-level installer with Desktop/Start Menu shortcuts and uninstaller.

---

## Run From Source

Requirements:

- Windows
- Python 3.10+

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

---

## Build

Build the packaged app:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\pyinstaller.exe build.spec --clean -y
```

Output:

```text
dist/FileRenamer/FileRenamer.exe
dist/FileRenamer/FileRenamerUpdater.exe
```

Build the Windows installer:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\installer\build-installer.ps1
```

Output:

```text
dist/FileRenamer-Setup.exe
```

---

## Install And Uninstall

`FileRenamer-Setup.exe` installs the app for the current Windows user.

Install location:

```text
%LOCALAPPDATA%\Programs\FileRenamer
```

The installer creates:

- `FileRenamer.exe`
- `FileRenamerUpdater.exe`
- `Uninstall FileRenamer.exe`
- Desktop shortcut
- Start Menu shortcut
- Windows Installed Apps uninstall entry under HKCU

Uninstall options:

- Run `%LOCALAPPDATA%\Programs\FileRenamer\Uninstall FileRenamer.exe`
- Or uninstall from Windows Settings > Installed apps

---

## Updates

The app checks:

```text
https://github.com/pduc1234/pyRenameRelease
```

Update behavior:

1. App starts.
2. Current `APP_VERSION` is compared with the latest GitHub Release.
3. If a newer version exists, the top bar shows `Update available`.
4. If the release includes a signed `latest.json` manifest and package hash, the app can download and verify the package.
5. If signed update assets are missing, the app still shows the update button and opens the GitHub Release page safely.

Preferred release assets:

```text
FileRenamer-Setup.exe
latest.json
latest.json.sig
```

Example `latest.json`:

```json
{
  "version": "0.2.4",
  "published_at": "2026-06-08T00:00:00Z",
  "package_url": "https://github.com/pduc1234/pyRenameRelease/releases/download/v0.2.4/FileRenamer-Setup.exe",
  "sha256": "<sha256 of FileRenamer-Setup.exe>",
  "signature_algorithm": "ed25519",
  "notes_url": "https://github.com/pduc1234/pyRenameRelease/releases/tag/v0.2.4"
}
```

---

## Release Checklist

1. Update `APP_VERSION` in `app/app_info.py`.
2. Update this README version and release examples.
3. Run tests:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tests\update-button.test.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tests\update-checker-fallback.test.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tests\i18n-packaged-path.test.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tests\installer-uninstall.test.ps1
.\.venv\Scripts\python.exe -m compileall app
```

4. Build app and installer:

```powershell
.\.venv\Scripts\pyinstaller.exe build.spec --clean -y
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\installer\build-installer.ps1
```

5. Commit and tag:

```powershell
git add README.md app/app_info.py app tests installer build.spec requirements.txt
git add -f dist/FileRenamer dist/FileRenamer-Setup.exe
git commit -m "v0.2.4: release build"
git tag v0.2.4
git push origin main
git push origin v0.2.4
```

6. Create a GitHub Release from tag `v0.2.4`.
7. Attach `dist/FileRenamer-Setup.exe`.
8. Optional but recommended: attach signed `latest.json` and `latest.json.sig`.

---

## Project Structure

```text
app/
  app_info.py              App version and GitHub release repository
  core/                    File scanning, preview, rename, undo, update logic
  i18n/                    English and Vietnamese translations
  ui/                      PySide6 UI windows, widgets, and tabs
  updater/                 Standalone updater entry point
assets/                    App icon and visual assets
dist/FileRenamer/          Packaged Windows app
dist/FileRenamer-Setup.exe Windows installer artifact
installer/                 Installer build script and C# installer stub
tests/                     PowerShell regression checks
main.py                    App entry point
build.spec                 PyInstaller configuration
requirements.txt           Runtime/build dependencies
```

---

## Tech Stack

- UI: PySide6
- Packaging: PyInstaller
- Installer: C#/.NET Framework self-extracting installer
- Updates: GitHub Releases API, SHA-256, Ed25519 manifest verification
- Video metadata: pymediainfo
- Updater helper: psutil

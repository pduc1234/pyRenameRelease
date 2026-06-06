# File Renamer / Trình Đổi Tên File

Version: `0.1.9`

A Windows desktop app for batch renaming files with live preview, undo support, video resolution naming, and update checks through GitHub Releases.

Ứng dụng desktop Windows để đổi tên file hàng loạt, có xem trước, hoàn tác, đổi tên theo độ phân giải video và kiểm tra cập nhật qua GitHub Releases.

---

## English

### Features

- **Sequential rename**: rename selected files with numbering, prefix, padding, and a custom pattern.
- **Add suffix**: append text to existing filenames with a configurable separator.
- **Video format rename**: rename videos using `{n}`, `{res}`, and `{name}` variables.
- **Optional video prefix**: enable `Use prefix` to generate names like `FFF_1 - 1920x1080.mp4`.
- **Resolution source**: auto-detect video resolution by default, with manual override available.
- **Precise file selection**: no auto-select on folder load, plus All/None/Invert and Shift + click range selection.
- **Live preview**: see old name, new name, and validation status before renaming.
- **Safe rename flow**: confirmation for large batches, validation for Windows filenames, and rollback on failure.
- **Undo**: revert the latest successful rename operation for the current folder.
- **Drag and drop**: drop a folder into the app to load it.
- **Multilingual UI**: English and Vietnamese.
- **Update check**: checks public GitHub Releases for newer versions.
- **Windows installer**: `FileRenamer-Setup.exe` installs the app for the current user, creates Desktop/Start Menu shortcuts, and adds `Uninstall FileRenamer.exe`.

### Run From Source

Requirements:

- Windows
- Python 3.10+

```powershell
pip install -r requirements.txt
python main.py
```

### Build Executable and Installer

```powershell
pip install -r requirements.txt
pyinstaller build.spec --clean -y
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\installer\build-installer.ps1
```

The packaged app is created at:

```text
dist/FileRenamer/FileRenamer.exe
```

The installer is created at:

```text
dist/FileRenamer-Setup.exe
```

When installed, FileRenamer is copied to:

```text
%LOCALAPPDATA%\Programs\FileRenamer
```

The installer creates Desktop and Start Menu shortcuts, writes a per-user uninstall entry to Windows Installed Apps, and places the uninstaller at:

```text
%LOCALAPPDATA%\Programs\FileRenamer\Uninstall FileRenamer.exe
```

### Update Releases

The app checks releases from:

```text
https://github.com/pduc1234/pyRenameRelease
```

Before publishing a new release:

1. Update `APP_VERSION` in `app/app_info.py`.
2. Rebuild with PyInstaller.
3. Rebuild the installer with `installer/build-installer.ps1`.
4. Push the updated app files and installer to the public release repository.
5. Create a GitHub Release with a tag newer than the app version users already have, for example `v0.1.9`.
6. Attach `dist/FileRenamer-Setup.exe` to the GitHub Release so users can install the latest version.

### Project Structure

```text
app/
  app_info.py              App version and public release repository
  core/                    File scanning, preview generation, rename, undo, update check
  i18n/                    English and Vietnamese translations
  ui/                      PySide6 windows, widgets, and tabs
assets/                    App icons and images
dist/FileRenamer/          Packaged Windows app
dist/FileRenamer-Setup.exe Windows installer artifact
installer/                 Installer build script and C# installer stub
main.py                    App entry point
build.spec                 PyInstaller configuration
requirements.txt           Runtime/build dependencies
```

### Tech Stack

- UI: PySide6
- Video metadata: pymediainfo
- Packaging: PyInstaller
- Installer: C#/.NET Framework self-extracting installer
- Updates: GitHub Releases API

---

## Tiếng Việt

### Tính năng

- **Đánh số file**: đổi tên các file đã chọn theo số thứ tự, tiền tố, số chữ số và mẫu tên tùy chỉnh.
- **Thêm hậu tố**: thêm chuỗi vào cuối tên file hiện tại với dấu ngăn cách tùy chọn.
- **Định dạng video**: đổi tên video bằng các biến `{n}`, `{res}`, `{name}`.
- **Tiền tố video tùy chọn**: bật `Sử dụng tiền tố` để tạo tên như `FFF_1 - 1920x1080.mp4`.
- **Nguồn độ phân giải**: mặc định tự động đọc độ phân giải video, vẫn có thể nhập thủ công.
- **Chọn file chính xác**: không tự chọn tất cả khi mở thư mục; hỗ trợ Tất cả/Bỏ chọn/Đảo chọn và Shift + click để chọn theo vùng.
- **Xem trước trực tiếp**: xem tên cũ, tên mới và trạng thái kiểm tra trước khi đổi tên.
- **Đổi tên an toàn**: xác nhận khi đổi tên nhiều file, kiểm tra tên hợp lệ trên Windows và rollback nếu lỗi.
- **Hoàn tác**: khôi phục lần đổi tên thành công gần nhất trong thư mục hiện tại.
- **Kéo thả thư mục**: kéo một thư mục vào app để tải danh sách file.
- **Giao diện song ngữ**: tiếng Anh và tiếng Việt.
- **Kiểm tra cập nhật**: kiểm tra bản mới qua GitHub Releases public.
- **Installer Windows**: `FileRenamer-Setup.exe` cài app cho user hiện tại, tạo shortcut Desktop/Start Menu và thêm `Uninstall FileRenamer.exe`.

### Chạy từ source

Yêu cầu:

- Windows
- Python 3.10+

```powershell
pip install -r requirements.txt
python main.py
```

### Build file chạy và installer

```powershell
pip install -r requirements.txt
pyinstaller build.spec --clean -y
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\installer\build-installer.ps1
```

Ứng dụng đã đóng gói nằm tại:

```text
dist/FileRenamer/FileRenamer.exe
```

Installer được tạo tại:

```text
dist/FileRenamer-Setup.exe
```

Sau khi cài đặt, FileRenamer được copy vào:

```text
%LOCALAPPDATA%\Programs\FileRenamer
```

Installer tạo shortcut ở Desktop và Start Menu, đăng ký mục gỡ cài đặt theo user trong Windows Installed Apps, và đặt file uninstall tại:

```text
%LOCALAPPDATA%\Programs\FileRenamer\Uninstall FileRenamer.exe
```

### Cập nhật phiên bản

App kiểm tra release tại:

```text
https://github.com/pduc1234/pyRenameRelease
```

Trước khi phát hành bản mới:

1. Cập nhật `APP_VERSION` trong `app/app_info.py`.
2. Build lại bằng PyInstaller.
3. Build lại installer bằng `installer/build-installer.ps1`.
4. Push các file app và installer đã cập nhật lên repo release public.
5. Tạo GitHub Release với tag mới hơn bản người dùng đang có, ví dụ `v0.1.9`.
6. Đính kèm `dist/FileRenamer-Setup.exe` vào GitHub Release để người dùng cài bản mới nhất.

### Cấu trúc project

```text
app/
  app_info.py              Version app và repo release public
  core/                    Quét file, tạo preview, đổi tên, hoàn tác, kiểm tra cập nhật
  i18n/                    Bản dịch tiếng Anh và tiếng Việt
  ui/                      Cửa sổ, widget và tab PySide6
assets/                    Icon và hình ảnh của app
dist/FileRenamer/          Bản app Windows đã đóng gói
dist/FileRenamer-Setup.exe File installer Windows
installer/                 Script build installer và C# installer stub
main.py                    Entry point của app
build.spec                 Cấu hình PyInstaller
requirements.txt           Dependency chạy/build app
```

### Công nghệ

- UI: PySide6
- Metadata video: pymediainfo
- Đóng gói: PyInstaller
- Installer: C#/.NET Framework self-extracting installer
- Cập nhật: GitHub Releases API

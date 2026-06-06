# File Renamer

A lightweight Windows desktop application for batch renaming files with multiple strategies: sequential numbering, suffix addition, and video format metadata extraction.

## Features

- **Sequential Rename**: Rename files with a prefix, starting number, and zero-padding
- **Add Suffix**: Append a suffix to filenames with customizable separator
- **Video Format**: Rename based on video resolution (manual or auto-detected from metadata)
- **File Selection**: Choose exactly which files to rename using checkboxes and bulk actions (All/None)
- **Multi-language**: Support for English and Vietnamese
- **Drag & Drop**: Drop folders onto the window (Best-effort; may be disabled on some systems)
- **Live Preview**: See the rename results before executing
- **Undo**: Revert the last rename operation with full history tracking
- **Filter & Sort**: Filter by extension (case-insensitive), sort by name/date/size
- **Batch Confirmation**: Confirmation dialog for batches >20 files
- **Atomic Operations**: Two-phase rename with automatic rollback on failure, supports swaps and cycles
- **Path Safety**: Prevents directory traversal attacks and Windows filename restrictions
- **Pattern Validation**: Video tab validates pattern variables ({n}, {res}, {name})
- **Modern UI**: Built with CustomTkinter for a sleek dark-themed responsive experience

## Installation

1. Install Python 3.10+
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## Building Executable

```bash
pip install -r requirements.txt
pyinstaller build.spec --clean
```

The output `.exe` will be in `dist/FileRenamer.exe` (one-file, no console)

## Architecture

- `app/core/`: Business logic (file scanning, renaming with atomic ops, history, sanitization)
- `app/ui/`: UI components (main window, file panel, tabs)
- `app/utils/`: Utility functions (history management)

## Tech Stack

- **UI**: customtkinter 5.2+
- **Drag & Drop**: tkinterdnd2
- **Video Metadata**: pymediainfo
- **Build**: pyinstaller

---

Made with ❤️ for batch file operations

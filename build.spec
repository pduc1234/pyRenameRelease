# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller build configuration for File Renamer (PySide6) with separate Updater."""

import sys
from pathlib import Path

block_cipher = None

# Include i18n and assets for main app
datas = [
    ('app/i18n', 'i18n'),
    ('assets', 'assets'),
]

# 1. Analysis for Main App
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['PySide6.QtCore', 'PySide6.QtWidgets', 'PySide6.QtGui', 'pymediainfo', 'cryptography', 'psutil'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=['tkinter', 'customtkinter', 'tkinterdnd2'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 2. Analysis for Updater
a_updater = Analysis(
    ['app/updater/updater_main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['psutil', 'cryptography', 'app.core.update_checker', 'app.core.update_downloader', 'app.core.update_security'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
pyz_updater = PYZ(a_updater.pure, a_updater.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='FileRenamer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/app.ico',
)

exe_updater = EXE(
    pyz_updater,
    a_updater.scripts,
    [],
    exclude_binaries=True,
    name='FileRenamerUpdater',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True, # Updater can have console for logging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    exe_updater,
    a_updater.binaries,
    a_updater.zipfiles,
    a_updater.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FileRenamer',
)

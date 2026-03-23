# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['auto_screenshot.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'pyautogui',
        'pygetwindow',
        'PIL',
        'PIL.Image',
        'keyboard',
        'pywintypes',
        'win32api',
        'win32con',
        'win32gui',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt5', 'pygame', 'cv2', 'matplotlib', 'scipy', 'pandas'],
    noarchive=True,
    optimize=1,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='终末地截图工具',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

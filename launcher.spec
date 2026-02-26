# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

added_files = [
    ('locales/', 'locales/'),
    ('config/', 'config/'),
    ('web_app/templates/', 'web_app/templates/'),
    ('web_app/static/', 'web_app/static/'),
    ('assets/fonts/', 'assets/fonts/'),
    ('webtoon_editor_test/', 'webtoon_editor_test/'),
]

a = Analysis(
    ['launcher/main.py'],
    pathex=['.'],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'customtkinter', 
        'PIL.ImageTk', 
        'PIL.Image', 
        'requests',
        'webview',
        'uvicorn',
        'fastapi',
        'jinja2',
        'starlette',
        'pydantic',
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'PyQt5.QtWebEngineWidgets',
        'PyQt5.QtWebChannel',
        'PyQt5.QtPrintSupport',
        'qtpy',
        'engineio',
        'socketio',
        'cv2',
        'numpy',
        'flask',
        'easyocr',
        'pytesseract',
        'PIL',
        'webtoon_editor_test.app'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['cv2.qt.plugins', 'cv2.qt'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ToonixLauncher',
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
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ToonixEditor'
)

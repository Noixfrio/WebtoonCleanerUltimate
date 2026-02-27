# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_data_files, collect_all

block_cipher = None

# Helper to add files only if they exist
def get_added_files():
    files = [
        ('locales/', 'locales/'),
        ('config/', 'config/'),
        ('web_app/templates/', 'web_app/templates/'),
        ('web_app/static/', 'web_app/static/'),
        ('webtoon_editor_test/', 'webtoon_editor_test/'),
    ]
    # Fontes são opcionais se não existirem no repo (podem ser baixadas depois)
    if os.path.exists('assets/fonts'):
        files.append(('assets/fonts/', 'assets/fonts/'))
    
    # CustomTkinter assets
    files += collect_data_files('customtkinter')
    
    # Robust collection for OCR engines
    for pkg in ['paddleocr', 'paddle', 'easyocr', 'pyocr']:
        try:
            tmp_datas, tmp_binaries, tmp_hidden = collect_all(pkg)
            files += tmp_datas
            # Note: binaries and hiddenimports will be handled in Analysis
        except:
            pass
            
    return files

added_files = get_added_files()

a = Analysis(
    ['launcher/main.py'],
    pathex=['.'],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'tkinter',
        '_tkinter',
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
    excludes=[
        'cv2.qt.plugins', 'cv2.qt',
        'matplotlib', 'notebook', 'ipython', 'ipykernel', 'jedi',
        'tornado', 'jsonschema', 'nbformat', 'nbconvert', 'testpath',
        'unittest', 'pydoc',
        'paddle.fluid.proto', 'paddle.dataset', 'paddle.reader',
        'setuptools', 'pip', 'distutils', 'numpy.f2py', 'PIL.SpiderImagePlugin'
    ],
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

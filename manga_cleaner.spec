# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

# Coleta dados automáticos de bibliotecas problemáticas
datas = collect_data_files('easyocr')
datas += collect_data_files('skimage')
datas += collect_data_files('fastapi')

# Adicionando pastas de dados do projeto de forma segura
added_files = []
for src_path in ['web_app/templates', 'web_app/static', 'assets', 'models']:
    if os.path.exists(src_path):
        added_files.append((src_path, src_path))
datas += added_files

# Importações que o PyInstaller às vezes não detecta automaticamente
hidden_imports = collect_submodules('uvicorn')
hidden_imports += [
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'fastapi',
    'jinja2',
    'anyio._backends._asyncio',
    'easyocr',
    'onnxruntime',
    'cv2',
    'numpy',
    'torch',
    'torchvision',
    'PIL',
]

a = Analysis(
    ['launcher.py'],
    pathex=[os.getcwd()],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='MangaCleaner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False, # Desativamos UPX para evitar falsos positivos de antivirus e lentidão
    console=True, 
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' 
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='MangaCleaner',
)

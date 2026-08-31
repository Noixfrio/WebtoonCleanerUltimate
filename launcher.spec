# -*- mode: python ; coding: utf-8 -*-
# Empacota o Toonix Editor em pasta Windows (onedir).
# Uso: python -m PyInstaller launcher.spec --clean --noconfirm

import os
from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None
ROOT = os.path.abspath(SPECPATH)


def collect_dir(src, dest):
    items = []
    if not os.path.isdir(src):
        return items
    for dirpath, dirnames, filenames in os.walk(src):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for filename in filenames:
            if filename.endswith((".pyc", ".pyo")):
                continue
            full = os.path.join(dirpath, filename)
            rel = os.path.relpath(dirpath, src)
            target = dest if rel == "." else os.path.join(dest, rel)
            items.append((full, target))
    return items


def _collect(package_name):
    try:
        d, b, h = collect_all(package_name)
        return list(d), list(b), list(h)
    except Exception:
        return [], [], []


datas = []
binaries = []
hiddenimports = [
    "uvicorn",
    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.loops.auto",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.websockets",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.lifespan",
    "uvicorn.lifespan.on",
    "fastapi",
    "starlette",
    "starlette.routing",
    "starlette.staticfiles",
    "starlette.templating",
    "pydantic",
    "pydantic_settings",
    "multipart",
    "jinja2",
    "customtkinter",
    "webview",
    "webview.platforms.winforms",
    "webview.platforms.edgechromium",
    "webview.platforms.mshtml",
    "easyocr",
    "onnxruntime",
    "cv2",
    "PIL",
    "PIL._tkinter_finder",
    "flask",
    "werkzeug",
    "huggingface_hub",
    "requests",
    "psutil",
    "websockets",
    "core",
    "core.pipeline",
    "core.detector",
    "core.mask_builder",
    "core.inpaint_engine",
    "core.advanced_inpaint",
    "core.font_manager",
    "core.model_manager",
    "core.logger",
    "config",
    "config.settings",
    "web_app",
    "web_app.main",
    "web_app.routes",
    "webtoon_editor_test",
    "webtoon_editor_test.app",
    "launcher",
    "launcher.main",
    "launcher.ui",
    "launcher.backend_server",
    "launcher.desktop_window",
    "tools.ultra_cleaner",
    "experimental_hybrid_cleaner",
]

for pkg in (
    "customtkinter",
    "webview",
    "easyocr",
    "onnxruntime",
    "huggingface_hub",
    "cv2",
    "flask",
    "jinja2",
):
    d, b, h = _collect(pkg)
    datas += d
    binaries += b
    hiddenimports += h

try:
    hiddenimports += collect_submodules("uvicorn")
except Exception:
    pass

# Paddle é enorme e não é usado no detector atual (EasyOCR).
# Se o PyInstaller puxar sozinho, o build infla e costuma quebrar.
excludes = [
    "paddle",
    "paddlepaddle",
    "paddleocr",
    "matplotlib",
    "tkinter.test",
    "pytest",
    "IPython",
    "notebook",
]

for src, dest in (
    ("config", "config"),
    ("locales", "locales"),
    ("web_app", "web_app"),
    ("webtoon_editor_test", "webtoon_editor_test"),
    ("tools", "tools"),
    ("experimental_hybrid_cleaner", "experimental_hybrid_cleaner"),
):
    datas += collect_dir(os.path.join(ROOT, src), dest)

if os.path.isfile(os.path.join(ROOT, "version.json")):
    datas.append((os.path.join(ROOT, "version.json"), "."))

runtime_hook = os.path.join(ROOT, "runtime_hooks", "pyi_rth_toonix.py")

a = Analysis(
    [os.path.join(ROOT, "launcher.py")],
    pathex=[ROOT],
    binaries=binaries,
    datas=datas,
    hiddenimports=sorted(set(hiddenimports)),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[runtime_hook] if os.path.isfile(runtime_hook) else [],
    excludes=excludes,
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
    name="ToonixLauncher",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
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
    strip=False,
    upx=False,
    upx_exclude=[],
    name="ToonixEditor",
)

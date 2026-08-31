import sys
from pathlib import Path

BINARY_VERSION = "v0.9.9-beta.32-win"


def get_app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


def get_live_modules_dir() -> Path:
    return get_app_dir() / "live_modules"


def get_installed_version_path() -> Path:
    return get_live_modules_dir() / "installed_version.txt"


def get_app_version(default: str = BINARY_VERSION) -> str:
    path = get_installed_version_path()
    try:
        if path.is_file():
            value = path.read_text(encoding="utf-8").strip()
            if value:
                return value
    except OSError:
        pass
    return default


def get_resource_path(relative_path):
    """Resolve caminhos para recursos: patch ao vivo, pasta do app, depois _MEIPASS."""
    relative = Path(relative_path)
    live = get_live_modules_dir() / relative
    if live.exists():
        return live

    if getattr(sys, "frozen", False):
        base_path = Path(sys.executable).parent
        candidate = base_path / relative
        if candidate.exists():
            return candidate

        if hasattr(sys, "_MEIPASS"):
            candidate = Path(sys._MEIPASS) / relative
            if candidate.exists():
                return candidate

    return Path(__file__).parent.parent / relative

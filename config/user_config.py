import json
import os
import shutil
import string
import sys
from pathlib import Path

DEFAULT_CONFIG = {
    "language": "pt-br",
    "analytics": True,
    "last_check": "",
    "models_dir": "",
}


def get_app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


def get_config_path() -> Path:
    return get_app_dir() / "config" / "config.json"


def load_user_config() -> dict:
    path = get_config_path()
    data = dict(DEFAULT_CONFIG)
    try:
        with open(path, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        if isinstance(loaded, dict):
            data.update(loaded)
    except (OSError, json.JSONDecodeError):
        pass
    return data


def save_user_config(updates: dict) -> dict:
    data = load_user_config()
    data.update(updates)
    path = get_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    return data


def get_default_models_dir() -> Path:
    return get_app_dir()


def get_models_dir() -> Path:
    configured = str(load_user_config().get("models_dir") or "").strip()
    if configured:
        return Path(configured)
    return get_default_models_dir()


def set_models_dir(path) -> Path:
    resolved = Path(path).expanduser().resolve()
    resolved.mkdir(parents=True, exist_ok=True)
    save_user_config({"models_dir": str(resolved)})
    apply_huggingface_cache(resolved)
    return resolved


def get_hf_cache_dir(models_dir=None) -> Path:
    base = Path(models_dir) if models_dir is not None else get_models_dir()
    return base / "huggingface"


def apply_huggingface_cache(models_dir=None) -> Path:
    """Redirect Hugging Face downloads off the system drive when possible."""
    cache_dir = get_hf_cache_dir(models_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    os.environ["HF_HOME"] = str(cache_dir)
    os.environ["HUGGINGFACE_HUB_CACHE"] = str(cache_dir / "hub")
    os.environ["HF_HUB_CACHE"] = str(cache_dir / "hub")
    return cache_dir


def get_free_space(path) -> int:
    candidate = Path(path)
    while not candidate.exists() and candidate.parent != candidate:
        candidate = candidate.parent
    if not candidate.exists():
        return 0
    return shutil.disk_usage(candidate).free


def list_available_drives():
    drives = []
    if os.name == "nt":
        for letter in string.ascii_uppercase:
            root = Path(f"{letter}:\\")
            if not root.exists():
                continue
            try:
                usage = shutil.disk_usage(root)
            except OSError:
                continue
            drives.append({
                "path": str(root),
                "label": f"{letter}:",
                "free": usage.free,
                "total": usage.total,
            })
        return drives

    root = Path("/")
    try:
        usage = shutil.disk_usage(root)
        drives.append({
            "path": str(root),
            "label": str(root),
            "free": usage.free,
            "total": usage.total,
        })
    except OSError:
        pass
    return drives


def format_bytes(num_bytes: int) -> str:
    value = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            if unit in ("B", "KB"):
                return f"{int(value)} {unit}"
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{num_bytes} B"

import os
import sys


LIVE_PACKAGES = (
    "core",
    "web_app",
    "launcher",
    "config",
    "webtoon_editor_test",
    "tools",
    "experimental_hybrid_cleaner",
)


def _live_modules_dir():
    if getattr(sys, "frozen", False):
        return os.path.join(os.path.dirname(sys.executable), "live_modules")
    return ""


def _install_live_modules_finder(live_root):
    """Faz .py extraídos de um patch ganharem do código congelado no PYZ."""
    if not os.path.isdir(live_root):
        return

    if live_root not in sys.path:
        sys.path.insert(0, live_root)

    try:
        import importlib.machinery
    except Exception:
        return

    class LivePathFinder:
        def find_spec(self, fullname, path, target=None):
            parts = fullname.split(".")
            if parts[0] not in LIVE_PACKAGES:
                return None
            rel = os.path.join(*parts)
            as_mod = os.path.join(live_root, rel + ".py")
            as_pkg = os.path.join(live_root, rel, "__init__.py")
            if not (os.path.isfile(as_mod) or os.path.isfile(as_pkg)):
                return None
            search = [live_root] if len(parts) == 1 else [os.path.join(live_root, *parts[:-1])]
            return importlib.machinery.PathFinder.find_spec(fullname, search, target)

    sys.meta_path.insert(0, LivePathFinder())


def _prepare_runtime():
    os.environ.setdefault("KMP_AFFINITY", "disabled")
    os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")

    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
        os.chdir(exe_dir)
        os.environ["TOONIX_FROZEN"] = "1"
        _install_live_modules_finder(_live_modules_dir())


_prepare_runtime()

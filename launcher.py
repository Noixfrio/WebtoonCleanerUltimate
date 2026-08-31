import multiprocessing
import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

if getattr(sys, "frozen", False):
    live = os.path.join(os.path.dirname(sys.executable), "live_modules")
    if os.path.isdir(live) and live not in sys.path:
        sys.path.insert(0, live)
        try:
            import importlib.machinery

            _PREFIXES = (
                "core",
                "web_app",
                "launcher",
                "config",
                "webtoon_editor_test",
                "tools",
                "experimental_hybrid_cleaner",
            )

            class _LivePathFinder:
                def find_spec(self, fullname, path, target=None):
                    parts = fullname.split(".")
                    if parts[0] not in _PREFIXES:
                        return None
                    rel = os.path.join(*parts)
                    as_mod = os.path.join(live, rel + ".py")
                    as_pkg = os.path.join(live, rel, "__init__.py")
                    if not (os.path.isfile(as_mod) or os.path.isfile(as_pkg)):
                        return None
                    search = [live] if len(parts) == 1 else [os.path.join(live, *parts[:-1])]
                    return importlib.machinery.PathFinder.find_spec(fullname, search, target)

            sys.meta_path.insert(0, _LivePathFinder())
        except Exception:
            pass

from launcher.main import main

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()

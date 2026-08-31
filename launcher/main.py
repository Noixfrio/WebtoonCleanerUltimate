import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from launcher.logger import logger
from launcher.i18n import i18n
from launcher.ui import start_ui
from launcher.utils import BINARY_VERSION, get_app_version

os.environ["KMP_AFFINITY"] = "disabled"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from launcher.utils import get_resource_path


def load_config():
    config_path = get_resource_path("config/config.json")
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"language": "pt-br", "analytics": True}


def cleanup_update_residue():
    """Remove arquivos temporários de atualizações anteriores."""
    try:
        from launcher.utils import get_app_dir

        base_dir = get_app_dir()
        residue_patterns = ["*.bak", "*.new", "update_toonix.bat", "toonix_update_download.zip"]
        for pattern in residue_patterns:
            for file_path in base_dir.glob(pattern):
                try:
                    logger.info(f"Removendo resíduo de update: {file_path.name}")
                    file_path.unlink()
                except Exception as e:
                    logger.warning(f"Não foi possível remover {file_path}: {e}")
    except Exception as e:
        logger.error(f"Erro no cleanup de resíduos: {e}")


def check_and_apply_updates():
    """Executa verificação e aplicação de atualizações antes de abrir a UI."""
    try:
        from launcher.utils import get_app_dir
        from core.auto_updater import AutoUpdater

        app_dir = get_app_dir()
        updater = AutoUpdater(app_dir)

        # Mostrar splash simples
        print("🔍 Procurando atualizações...")
        logger.info("Verificando atualizações automáticas...")

        updated, commit = updater.run_update_check_and_apply()

        if updated:
            print(f"✓ Atualizado para commit {commit}")
            logger.info(f"Aplicada atualização para {commit}")
        elif commit:
            print(f"✓ Já atualizado ({commit})")
            logger.info(f"Sistema já está atualizado ({commit})")
        else:
            logger.info("Verificação de atualização concluída (sem commit info)")

        return commit

    except Exception as e:
        logger.error(f"Erro no auto-update: {e}")
        import traceback
        traceback.print_exc()
        # Falha no update não deve impedir a abertura
        return None


def main():
    if "--test-boot" in sys.argv:
        print("BOOT_OK")
        sys.exit(0)

    version = get_app_version(BINARY_VERSION)
    logger.info(f"Iniciando Toonix Launcher {version} (binário {BINARY_VERSION})")

    cleanup_update_residue()

    # Auto-update antes de abrir a UI
    current_commit = None
    if "--skip-update" not in sys.argv and os.environ.get("TOONIX_SKIP_UPDATE") != "1":
        current_commit = check_and_apply_updates()
    else:
        logger.info("Auto-update ignorado via flag ou variável de ambiente.")

    config = load_config()
    i18n.load_language(config.get("language", "pt-br"))

    # Passar o commit para a UI exibir
    start_ui(version, binary_version=BINARY_VERSION, current_commit=current_commit)


if __name__ == "__main__":
    main()

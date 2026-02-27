import sys
import os
import json
from pathlib import Path

# Adicionar pasta raiz ao path caso executado via script
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from launcher.logger import logger
from launcher.i18n import i18n
from launcher.ui import start_ui
from launcher.updater import ToonixUpdater

VERSION = "0.9.9"

from launcher.utils import get_resource_path

def load_config():
    config_path = get_resource_path("config/config.json")
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except:
            pass
    return {"language": "pt-br", "analytics": True}

def cleanup_update_residue():
    """Remove arquivos temporários de atualizações anteriores (.bak, .new, .bat)."""
    try:
        current_exe = Path(sys.executable)
        base_dir = current_exe.parent
        
        # Padrões de arquivos para limpar
        residue_patterns = ["*.bak", "*.new", "update_toonix.bat"]
        
        for pattern in residue_patterns:
            for file_path in base_dir.glob(pattern):
                try:
                    logger.info(f"Removendo resíduo de update: {file_path.name}")
                    file_path.unlink()
                except Exception as e:
                    logger.warning(f"Não foi possível remover {file_path}: {e}")
    except Exception as e:
        logger.error(f"Erro no cleanup de resíduos: {e}")

def main():
    # Flag para validação de boot via Updater
    if "--test-boot" in sys.argv:
        print("BOOT_OK")
        sys.exit(0)
        
    logger.info(f"Iniciando Toonix Launcher v{VERSION}")
    
    # 0. Limpar resíduos de updates anteriores
    cleanup_update_residue()
    
    # Carregar Config e Idioma
    config = load_config()
    i18n.load_language(config.get("language", "pt-br"))
    
    # Flag para pular update (caso o wine trave na rede)
    if "--skip-update" in sys.argv:
        logger.info("Update ignorado via flag.")
        start_ui(VERSION, skip_update=True)
    else:
        start_ui(VERSION)

if __name__ == "__main__":
    main()

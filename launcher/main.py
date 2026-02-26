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

VERSION = "0.9.0-beta"

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

def main():
    logger.info(f"Iniciando Toonix Launcher v{VERSION}")
    
    # Carregar Config e Idioma
    config = load_config()
    i18n.load_language(config.get("language", "pt-br"))
    
    # Iniciar UI (O boot real aconteceria via threads no splash screen)
    start_ui(VERSION)

if __name__ == "__main__":
    main()

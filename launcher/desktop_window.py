import webview
import threading
import os
import sys
import time
import requests
from pathlib import Path
from launcher.logger import logger

# Qt só no Linux. No Windows o pywebview usa Edge WebView2 (sem PyQt).
if getattr(sys, 'frozen', False) and sys.platform.startswith('linux'):
    base_dir = Path(sys.executable).parent
    plugin_path = str(base_dir / "_internal" / "PyQt5" / "Qt5" / "plugins")
    if os.path.exists(plugin_path):
        os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path
        os.environ['QT_QPA_PLATFORM'] = 'xcb'

class DesktopApp:
    def __init__(self, url="http://127.0.0.1:5000"):
        self.url = url
        self.window = None

    def _wait_for_server(self):
        """Aguarda o backend ficar pronto antes de mostrar a janela."""
        logger.info(f"Aguardando servidor em {self.url}...")
        retries = 30
        while retries > 0:
            try:
                response = requests.get(self.url, timeout=1)
                if response.status_code == 200:
                    logger.info("Servidor detectado e pronto!")
                    return True
            except:
                pass
            time.sleep(1)
            retries -= 1
        return False

    def start(self):
        """Inicia a janela do PyWebView."""
        if not self._wait_for_server():
            logger.error("Falha ao conectar ao servidor backend.")
            return

        self.window = webview.create_window(
            'Toonix Editor',
            self.url,
            width=1280,
            height=800,
            min_size=(800, 600),
            background_color='#0f1117'
        )
        
        gui = None
        if sys.platform.startswith("linux"):
            gui = "qt"
        elif sys.platform == "win32":
            gui = "edgechromium"

        try:
            webview.start(debug=False, gui=gui)
        except Exception as e:
            logger.warning(f"Falha no backend webview '{gui}': {e}. Tentando automático.")
            webview.start(debug=False)

def launch_desktop(url="http://127.0.0.1:5000"):
    app = DesktopApp(url)
    app.start()

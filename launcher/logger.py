import logging
import os
import platform
from pathlib import Path

class ToonixLogger:
    def __init__(self):
        self.app_name = "ToonixEditor"
        self.log_dir = self._get_log_dir()
        self.log_file = self.log_dir / "launcher.log"
        self.log_buffer = [] # Buffer para o viewer interno
        
        self._setup_logging()

    def _get_log_dir(self):
        if platform.system() == "Windows":
            base = Path(os.environ.get("APPDATA", "~"))
        else:
            base = Path.home() / ".config"
            
        log_path = base / self.app_name / "logs"
        log_path.mkdir(parents=True, exist_ok=True)
        return log_path

    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("Launcher")

    def info(self, msg):
        self.logger.info(msg)
        self._add_to_buffer("INFO", msg)

    def error(self, msg):
        self.logger.error(msg)
        self._add_to_buffer("ERROR", msg)

    def _add_to_buffer(self, level, msg):
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_buffer.append(f"[{timestamp}] [{level}] {msg}")
        # Manter apenas os últimos 500 logs no buffer de memória
        if len(self.log_buffer) > 500:
            self.log_buffer.pop(0)

    def get_buffer(self):
        return "\n".join(self.log_buffer)

# Singleton
logger = ToonixLogger()

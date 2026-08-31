import json
import logging
import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from urllib.request import urlopen
import psutil


def _clean_port(port: int, logger: logging.Logger):
    """Tenta liberar a porta caso esteja ocupada por um processo zumbi."""
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            for conns in proc.connections(kind='inet'):
                if conns.laddr.port == port:
                    logger.warning(f"Limpando porta {port} (Processo: {proc.info['name']}, PID: {proc.info['pid']})")
                    proc.terminate()
                    try:
                        proc.wait(timeout=3)
                    except psutil.TimeoutExpired:
                        proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

from launcher.updater import UpdateManager


def _setup_logger(base_dir: Path) -> logging.Logger:
    logger = logging.getLogger("ToonixLauncher")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    log_path = base_dir / "launcher.log"
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


def _user_home_dirs(base_dir: Path) -> dict:
    home = Path.home() / ".toonix"
    try:
        home.mkdir(parents=True, exist_ok=True)
    except Exception:
        home = base_dir / ".toonix"
        home.mkdir(parents=True, exist_ok=True)
    models = home / "models"
    projects = home / "projects"
    config = home / "config"
    logs = home / "logs"
    for d in (home, models, projects, config, logs):
        d.mkdir(parents=True, exist_ok=True)

    projects_index = config / "projects.json"
    if not projects_index.exists():
        projects_index.write_text(json.dumps({"recent": []}, indent=2), encoding="utf-8")

    return {
        "home": home,
        "models": models,
        "projects": projects,
        "config": config,
        "logs": logs,
        "projects_index": projects_index,
    }


def _wait_for_http(url: str, timeout_s: int = 60) -> bool:
    end = time.time() + timeout_s
    while time.time() < end:
        try:
            with urlopen(url, timeout=2) as resp:
                if 200 <= resp.status < 500:
                    return True
        except Exception:
            pass
        time.sleep(1)
    return False


def _backend_env(user_dirs: dict, current_dir: Path, base_dir: Path) -> dict:
    env = os.environ.copy()
    env["TOONIX_HOME"] = str(user_dirs["home"])
    env["TOONIX_MODELS_DIR"] = str(user_dirs["models"])
    env["TOONIX_PROJECTS_DIR"] = str(user_dirs["projects"])
    env["TOONIX_CONFIG_DIR"] = str(user_dirs["config"])
    manifest_path = current_dir / "update.json"
    if not manifest_path.exists():
        manifest_path = base_dir / "update.json"
    env["TOONIX_MANIFEST_PATH"] = str(manifest_path)
    return env


def _run_backend(current_dir: Path, python_bin: Path, user_dirs: dict, logger: logging.Logger, base_dir: Path) -> int:
    env = _backend_env(user_dirs, current_dir, base_dir)
    
    # Limpar portas antes de iniciar
    _clean_port(5000, logger)
    _clean_port(5002, logger)
    
    # 1. Comando do Servidor Principal (FastAPI)
    cmd_main = [
        str(python_bin),
        "-m",
        "uvicorn",
        "web_app.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "5000",
        "--log-level",
        "info",
    ]

    # 2. Comando do Editor Pro (Flask)
    pro_path = current_dir / "webtoon_editor_test" / "app.py"
    cmd_pro = [str(python_bin), str(pro_path)]

    processes = []
    
    logger.info("Iniciando servidores do ecossistema Toonix...")
    
    # Iniciar Main Backend
    proc_main = subprocess.Popen(cmd_main, cwd=str(current_dir), env=env)
    processes.append(proc_main)
    
    # Iniciar Editor Pro se existir
    proc_pro = None
    if pro_path.exists():
        logger.info("Iniciando Editor Pro na porta 5002...")
        proc_pro = subprocess.Popen(cmd_pro, cwd=str(current_dir), env=env)
        processes.append(proc_pro)
    else:
        logger.warning(f"Editor Pro não encontrado em: {pro_path}")

    try:
        # Aguardar servidor principal
        if _wait_for_http("http://127.0.0.1:5000/health", timeout_s=60):
            logger.info("Servidor principal pronto em http://127.0.0.1:5000")
            
            # Abrir navegador
            # webbrowser.open("http://127.0.0.1:5000") 
            # Nota: O bootstrap original abria o navegador. Mantemos o comportamento.
            webbrowser.open("http://127.0.0.1:5000")
        else:
            logger.error("Servidor principal não ficou pronto.")

        # Manter o processo pai vivo enquanto os filhos estiverem rodando
        while all(p.poll() is None for p in processes):
            time.sleep(1)
            
        return 0
    except KeyboardInterrupt:
        logger.info("Interrupção recebida. Encerrando servidores...")
        for p in processes:
            p.terminate()
        
        # Aguardar encerramento gracioso
        time.sleep(2)
        for p in processes:
            if p.poll() is None:
                p.kill()
        return 130


def main() -> None:
    base_dir = Path(__file__).resolve().parent.parent
    logger = _setup_logger(base_dir)
    user_dirs = _user_home_dirs(base_dir)

    logger.info("Toonix Launcher bootstrap iniciado")
    updater = UpdateManager(base_dir=base_dir, user_dirs=user_dirs, logger=logger)

    try:
        current_dir, python_bin = updater.ensure_current_version()
    except Exception as exc:
        logger.exception(f"Falha no update/bootstrap: {exc}")
        sys.exit(1)

    exit_code = _run_backend(current_dir, python_bin, user_dirs, logger, base_dir)
    sys.exit(exit_code)

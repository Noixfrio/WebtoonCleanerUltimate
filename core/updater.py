import os
import sys
import requests
import zipfile
import shutil
import logging
from pathlib import Path

# Configuração de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Updater")

GITHUB_REPO = "Noixfrio/WebtoonCleanerUltimate"
VERSION_FILE = "version.txt"

def get_local_version():
    """Lê a versão atual do arquivo local."""
    try:
        if os.path.exists(VERSION_FILE):
            with open(VERSION_FILE, "r") as f:
                return f.read().strip()
    except Exception:
        pass
    return "0.0.0"

def get_remote_version():
    """Busca a versão mais recente na API do GitHub."""
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()["tag_name"]
    except Exception as e:
        logger.error(f"Erro ao verificar versão remota: {e}")
    return None

def download_source_patch(download_url, target_path):
    """Baixa o ZIP do código fonte."""
    try:
        logger.info(f"Baixando atualização de {download_url}...")
        response = requests.get(download_url, stream=True, timeout=30)
        if response.status_code == 200:
            with open(target_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
    except Exception as e:
        logger.error(f"Erro no download: {e}")
    return False

def apply_update(zip_path, extract_dir):
    """Extrai os arquivos atualizados, ignorando os pesados."""
    try:
        logger.info("Aplicando atualização...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Lista de arquivos no ZIP
            for member in zip_ref.namelist():
                filename = os.path.basename(member)
                # Ignora pastas de drivers, modelos e venv se estiverem no ZIP por engano
                if any(x in member for x in ["venv/", "_internal/", "dist/", "build/", "assets/models/", "models/"]):
                    continue
                
                # Extrai apenas arquivos relevantes (web_app, core, etc.)
                if member.startswith(("web_app/", "core/", "scripts/")) or filename.endswith((".py", ".html", ".css", ".js")):
                    zip_ref.extract(member, extract_dir)
        return True
    except Exception as e:
        logger.error(f"Erro ao extrair atualização: {e}")
    return False

def run_update_process():
    """Executa o fluxo completo de atualização."""
    local_v = get_local_version()
    remote_v = get_remote_version()

    if not remote_v or local_v == remote_v:
        logger.info("Sistema já está atualizado ou offline.")
        return

    logger.info(f"Nova versão encontrada: {remote_v} (Atual: {local_v})")
    
    # URL do ZIP do código fonte (GitHub fornece isso automaticamente)
    download_url = f"https://github.com/Noixfrio/WebtoonCleanerUltimate/archive/refs/heads/master.zip"
    tmp_zip = "update_temp.zip"
    
    if download_source_patch(download_url, tmp_zip):
        if apply_update(tmp_zip, "."):
            with open(VERSION_FILE, "w") as f:
                f.write(remote_v)
            logger.info("Atualização concluída com sucesso!")
        
        if os.path.exists(tmp_zip):
            os.remove(tmp_zip)

if __name__ == "__main__":
    run_update_process()

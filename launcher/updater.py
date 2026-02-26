import hashlib
import requests
import os
import sys
import platform
import shutil
import subprocess
import time
from pathlib import Path
from .logger import logger

class ToonixUpdater:
    def __init__(self, current_v="0.0.0"):
        self.current_version = current_v
        self.version_url = "https://raw.githubusercontent.com/Noixfrio/WebtoonCleanerUltimate/master/version.json"
        
        # Identificação dinâmica do executável
        self.current_exe = Path(sys.executable)
        self.os_name = platform.system().lower() # 'windows' or 'linux'
        
    def calculate_sha256(self, file_path):
        if not os.path.exists(file_path):
            return None
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(8192), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Erro ao calcular hash: {e}")
            return None

    def check_for_updates(self):
        """Consulta o version.json e retorna os dados se houver nova versão."""
        try:
            logger.info("Checando atualizações no GitHub...")
            response = requests.get(self.version_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                remote_v = data.get("version", "0.0.0")
                
                # Comparação simples de versão
                if remote_v != self.current_version:
                    logger.info(f"Nova versão disponível: {remote_v}")
                    return data
                else:
                    logger.info("Sistema atualizado.")
            else:
                logger.warning(f"Falha ao consultar version.json: HTTP {response.status_code}")
        except Exception as e:
            logger.error(f"Erro ao verificar updates: {e}")
        return None

    def download_file(self, url, dest_path, progress_callback=None):
        """Download com callback de progresso para a UI."""
        try:
            response = requests.get(url, stream=True, timeout=30)
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(dest_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=16384):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total_size > 0:
                            progress_callback(downloaded / total_size)
            return True
        except Exception as e:
            logger.error(f"Erro no download: {e}")
            return False

    def perform_update(self, remote_data, progress_callback=None):
        """Executa a troca do executável baseada no OS."""
        platform_data = remote_data.get(self.os_name)
        if not platform_data:
            logger.error(f"Dados de atualização não encontrados para a plataforma: {self.os_name}")
            return False

        download_url = platform_data.get("url")
        expected_hash = platform_data.get("sha256")
        temp_file = Path(f"{self.current_exe}.new")
        backup_file = Path(f"{self.current_exe}.bak")

        # 1. Download para arquivo temporário
        logger.info(f"Baixando atualização para {temp_file}")
        if not self.download_file(download_url, temp_file, progress_callback=progress_callback):
            return False

        # 2. Validar integridade
        actual_hash = self.calculate_sha256(temp_file)
        if actual_hash != expected_hash:
            logger.error(f"Falha de integridade! Esperado: {expected_hash}, Obtido: {actual_hash}")
            if temp_file.exists(): temp_file.unlink()
            return False

        # 3. Preparar Swap (Diferente por OS)
        try:
            if self.os_name == "windows":
                self._apply_windows_update(temp_file)
            else:
                self._apply_linux_update(temp_file, backup_file)
            return True
        except Exception as e:
            logger.error(f"Falha ao aplicar atualização: {e}")
            return False

    def _apply_linux_update(self, new_file, backup_file):
        """Lógica para Linux (AppImage ou Executável): Atômica via Rename."""
        logger.info("Aplicando update Linux...")
        
        # Backup da versão atual
        if backup_file.exists(): backup_file.unlink()
        shutil.move(str(self.current_exe), str(backup_file))
        
        # Mover nova versão e dar permissão
        shutil.move(str(new_file), str(self.current_exe))
        os.chmod(str(self.current_exe), 0o755)
        
        logger.info("Update aplicado. Reiniciando...")
        # Reiniciar processo
        os.execv(sys.executable, sys.argv)

    def _apply_windows_update(self, new_file):
        """Lógica para Windows: Requer script auxiliar para matar e trocar."""
        logger.info("Preparando script de atualização para Windows...")
        bat_path = Path("update_toonix.bat")
        
        # Conteúdo do BAT: espera o pai fechar, troca e reabre
        bat_content = f"""@echo off
timeout /t 2 /nobreak > nul
del "{self.current_exe}"
move "{new_file}" "{self.current_exe}"
start "" "{self.current_exe}"
del "%~f0"
"""
        with open(bat_path, "w") as f:
            f.write(bat_content)
        
        # Executar o BAT de forma independente e fechar o app atual
        subprocess.Popen([str(bat_path)], shell=True)
        sys.exit(0)

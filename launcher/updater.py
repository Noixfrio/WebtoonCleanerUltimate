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
        """Download com callback de progresso e lógica de retry (3 tentativas)."""
        retries = 3
        for attempt in range(retries):
            try:
                logger.info(f"Tentativa {attempt + 1} de download...")
                response = requests.get(url, stream=True, timeout=30)
                response.raise_for_status() # Lança erro para status HTTP 4xx/5xx
                
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
            except (requests.RequestException, IOError) as e:
                logger.warning(f"Falha na tentativa {attempt + 1}: {e}")
                if attempt < retries - 1:
                    time.sleep(2)
                else:
                    logger.error("Todas as tentativas de download falharam.")
        return False

    def perform_update(self, remote_data, progress_callback=None):
        """Executa a troca do executável baseada no OS com validação de boot."""
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

        # 2. Validar integridade SHA256
        actual_hash = self.calculate_sha256(temp_file)
        if actual_hash != expected_hash:
            logger.error(f"Falha de integridade! Esperado: {expected_hash}, Obtido: {actual_hash}")
            if temp_file.exists(): temp_file.unlink()
            return False

        # 3. Extrair se for ZIP
        binary_to_test = temp_file
        extract_dir = Path("temp_update_extract")
        if download_url.endswith(".zip"):
            try:
                import zipfile
                if extract_dir.exists(): shutil.rmtree(extract_dir)
                extract_dir.mkdir()
                
                logger.info("Extraindo pacote de atualização...")
                with zipfile.ZipFile(temp_file, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                
                # Localizar o binário dentro da extração (ToonixEditor/ToonixLauncher)
                if self.os_name == "windows":
                    found = list(extract_dir.glob("**/ToonixLauncher.exe"))
                else:
                    found = list(extract_dir.glob("**/ToonixLauncher"))
                
                if not found:
                    logger.error("Binário não encontrado dentro do ZIP extraído!")
                    return False
                binary_to_test = found[0]
            except Exception as e:
                logger.error(f"Erro ao extrair ZIP: {e}")
                return False

        # 4. Validar se o novo binário abre corretamente (Rollback Automático de Boot)
        if not self._test_boot(binary_to_test):
            logger.error("O novo binário falhou no teste de boot! Abortando update.")
            if temp_file.exists(): temp_file.unlink()
            if extract_dir.exists(): shutil.rmtree(extract_dir)
            return False

        # 5. Preparar Swap (Diferente por OS)
        try:
            if self.os_name == "windows":
                self._apply_windows_update(binary_to_test)
            else:
                self._apply_linux_update(binary_to_test, backup_file)
            return True
        except Exception as e:
            logger.error(f"Falha ao aplicar atualização: {e}")
            return False

    def _test_boot(self, binary_path):
        """Valida se o binário está funcional rodando-o com flag de teste."""
        try:
            # Dar permissão de execução para o teste no Linux
            if self.os_name == "linux":
                os.chmod(str(binary_path), 0o755)
            
            logger.info("Validando boot do novo binário...")
            # Rodar com timeout curto para garantir que ele responde
            result = subprocess.run(
                [str(binary_path), "--test-boot"], 
                capture_output=True, 
                text=True,
                timeout=15
            )
            return "BOOT_OK" in result.stdout
        except Exception as e:
            logger.error(f"Novo binário falhou no teste de execução: {e}")
            return False

    def _apply_linux_update(self, new_file, backup_file):
        """Lógica para Linux: Atômica via Rename com Backup."""
        logger.info("Aplicando update Linux...")
        
        # Backup da versão atual
        if backup_file.exists(): backup_file.unlink()
        
        # Operação atômica: backup -> novo
        try:
            shutil.copy2(str(self.current_exe), str(backup_file)) # Copy para manter metadados e segurança
            shutil.move(str(new_file), str(self.current_exe))
            os.chmod(str(self.current_exe), 0o755)
            
            logger.info("Update aplicado com sucesso. Reiniciando...")
            os.execv(sys.executable, sys.argv)
        except Exception as e:
            logger.error(f"Falha no swap Linux: {e}")
            raise e

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

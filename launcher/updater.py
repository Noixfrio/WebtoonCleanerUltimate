import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path

import requests

from launcher.logger import logger
from launcher.utils import get_app_dir, get_installed_version_path, get_live_modules_dir

PATCH_ROOTS = (
    "core",
    "web_app",
    "launcher",
    "config",
    "locales",
    "tools",
    "webtoon_editor_test",
    "experimental_hybrid_cleaner",
)

REQUEST_HEADERS = {
    "User-Agent": "ToonixUpdater/1.0",
    "Cache-Control": "no-cache",
}


class ToonixUpdater:
    def __init__(self, current_v="0.0.0", binary_v=None):
        self.current_version = current_v
        self.binary_version = binary_v or current_v
        self.version_url = "https://raw.githubusercontent.com/Noixfrio/WebtoonCleanerUltimate/master/version.json"
        self.current_exe = Path(sys.executable)
        self.os_name = "windows" if sys.platform.startswith("win") else "linux"

    def calculate_sha256(self, file_path, progress_callback=None):
        if not os.path.exists(file_path):
            return None
        sha256_hash = hashlib.sha256()
        total = os.path.getsize(file_path) or 1
        done = 0
        try:
            with open(file_path, "rb") as f:
                while True:
                    byte_block = f.read(1024 * 1024)
                    if not byte_block:
                        break
                    sha256_hash.update(byte_block)
                    done += len(byte_block)
                    if progress_callback:
                        progress_callback(min(done / total, 1.0), "verify")
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Erro ao calcular hash: {e}")
            return None

    def check_for_updates(self):
        """Consulta o version.json e retorna um payload único se houver update."""
        try:
            logger.info("Checando atualizações no GitHub...")
            response = requests.get(
                self.version_url,
                timeout=15,
                headers=REQUEST_HEADERS,
                params={"t": int(time.time())},
            )
            if response.status_code != 200:
                logger.warning(f"Falha ao consultar version.json: HTTP {response.status_code}")
                return None

            data = response.json()
            offer = self._select_update(data)
            if offer:
                logger.info(f"Nova versão ({offer['update_type']}): {offer['version']}")
                return offer
            logger.info("Sistema atualizado.")
        except Exception as e:
            logger.error(f"Erro ao verificar updates: {e}")
        return None

    def _select_update(self, data):
        patch = data.get("patch") or {}
        platform_data = data.get(self.os_name) or {}
        changelog = (
            patch.get("changelog")
            or data.get("changelog")
            or "\n".join(data.get("news") or [])
            or "Nenhum log fornecido."
        )

        patch_version = (patch.get("version") or "").strip()
        patch_url = (patch.get("url") or "").strip()
        if patch_version and patch_url and self._is_newer(patch_version, self.current_version):
            min_binary = (patch.get("min_binary") or "").strip()
            if min_binary and self._is_newer(min_binary, self.binary_version):
                logger.warning(
                    f"Patch {patch_version} exige binário {min_binary}; "
                    f"binário atual {self.binary_version}."
                )
            else:
                return {
                    "version": patch_version,
                    "changelog": changelog,
                    "mandatory": bool(data.get("mandatory") or patch.get("mandatory")),
                    "update_type": "patch",
                    "url": patch_url,
                    "sha256": (patch.get("sha256") or "").strip(),
                    "windows": data.get("windows") or {},
                    "linux": data.get("linux") or {},
                }

        full_update = bool(platform_data.get("full_update"))
        remote_full = (platform_data.get("version") or "").strip()
        full_url = (platform_data.get("url") or "").strip()
        if full_update and remote_full and full_url and self._is_newer(remote_full, self.binary_version):
            return {
                "version": remote_full,
                "changelog": changelog,
                "mandatory": bool(data.get("mandatory")),
                "update_type": "full",
                "url": full_url,
                "sha256": (platform_data.get("sha256") or "").strip(),
                "windows": data.get("windows") or {},
                "linux": data.get("linux") or {},
            }
        return None

    @staticmethod
    def _is_newer(remote, local):
        def norm(value):
            text = (value or "").strip().lower()
            if text.startswith("v"):
                text = text[1:]
            return text

        r, l = norm(remote), norm(local)
        return bool(r) and r != l

    def download_file(self, url, dest_path, progress_callback=None):
        retries = 3
        download_url = url
        if "huggingface.co" in url and "download=true" not in url:
            download_url = url + ("&" if "?" in url else "?") + "download=true"

        for attempt in range(retries):
            try:
                logger.info(f"Tentativa {attempt + 1} de download...")
                response = requests.get(
                    download_url,
                    stream=True,
                    timeout=(20, 120),
                    headers=REQUEST_HEADERS,
                    allow_redirects=True,
                )
                response.raise_for_status()

                total_size = int(response.headers.get("content-length", 0))
                downloaded = 0

                with open(dest_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=256 * 1024):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if progress_callback and total_size > 0:
                                progress_callback(downloaded / total_size, "download")
                return True
            except (requests.RequestException, IOError) as e:
                logger.warning(f"Falha na tentativa {attempt + 1}: {e}")
                if attempt < retries - 1:
                    time.sleep(2)
                else:
                    logger.error("Todas as tentativas de download falharam.")
        return False

    def perform_update(self, remote_data, progress_callback=None):
        update_type = remote_data.get("update_type") or "full"
        download_url = remote_data.get("url")
        expected_hash = (remote_data.get("sha256") or "").strip()
        if not download_url:
            logger.error("URL de atualização ausente.")
            return False

        app_dir = get_app_dir()
        temp_file = app_dir / "toonix_update_download.zip"

        logger.info(f"Baixando atualização ({update_type}) para {temp_file}")
        if not self.download_file(download_url, temp_file, progress_callback=progress_callback):
            return False

        if not zipfile.is_zipfile(temp_file):
            logger.error("O arquivo baixado não é um ZIP válido (possível página HTML/erro).")
            self._safe_unlink(temp_file)
            return False

        if expected_hash:
            if progress_callback:
                progress_callback(1.0, "verify")
            actual_hash = self.calculate_sha256(temp_file, progress_callback=progress_callback)
            if not actual_hash or actual_hash.lower() != expected_hash.lower():
                logger.error(
                    f"Falha de integridade! Esperado: {expected_hash}, Obtido: {actual_hash}"
                )
                self._safe_unlink(temp_file)
                return False
        else:
            logger.warning("SHA256 não informado; validando apenas o formato ZIP.")

        try:
            if update_type == "patch":
                ok = self._apply_patch(temp_file, remote_data.get("version"), progress_callback)
            else:
                ok = self._apply_full(temp_file, remote_data, progress_callback)
            return ok
        finally:
            self._safe_unlink(temp_file)

    def _apply_patch(self, zip_path, new_version, progress_callback=None):
        live_dir = get_live_modules_dir()
        staging = Path(tempfile.mkdtemp(prefix="toonix_patch_", dir=str(get_app_dir())))
        logger.info("Aplicando patch incremental...")
        if progress_callback:
            progress_callback(0.3, "apply")
        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(staging)

            source_root = self._detect_patch_root(staging)
            if live_dir.exists():
                shutil.rmtree(live_dir, ignore_errors=True)
            live_dir.mkdir(parents=True, exist_ok=True)

            copied = 0
            for root_name in PATCH_ROOTS:
                src = source_root / root_name
                if not src.exists():
                    continue
                dest = live_dir / root_name
                if src.is_dir():
                    shutil.copytree(src, dest, dirs_exist_ok=True)
                else:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dest)
                copied += 1

            extra_version = source_root / "version.json"
            if extra_version.exists():
                shutil.copy2(extra_version, live_dir / "version.json")

            version_path = get_installed_version_path()
            version_path.write_text(new_version or self.current_version, encoding="utf-8")
            logger.info(f"Patch aplicado ({copied} pastas). Versão: {new_version}")
            if progress_callback:
                progress_callback(1.0, "apply")
            self._restart_app()
            return True
        except Exception as e:
            logger.error(f"Falha ao aplicar patch: {e}")
            return False
        finally:
            shutil.rmtree(staging, ignore_errors=True)

    def _detect_patch_root(self, extracted: Path) -> Path:
        if any((extracted / name).exists() for name in PATCH_ROOTS):
            return extracted
        for child in extracted.iterdir():
            if child.is_dir() and any((child / name).exists() for name in PATCH_ROOTS):
                return child
        return extracted

    def _apply_full(self, zip_path, remote_data, progress_callback=None):
        extract_dir = get_app_dir() / "temp_update_extract"
        try:
            if extract_dir.exists():
                shutil.rmtree(extract_dir)
            extract_dir.mkdir()
            logger.info("Extraindo pacote completo...")
            if progress_callback:
                progress_callback(0.2, "apply")
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)

            if self.os_name == "windows":
                found = list(extract_dir.glob("**/ToonixLauncher.exe"))
            else:
                found = list(extract_dir.glob("**/ToonixLauncher"))

            if not found:
                logger.error("Binário não encontrado dentro do ZIP extraído!")
                return False
            binary_to_test = found[0]
            payload_root = binary_to_test.parent

            if not self._test_boot(binary_to_test):
                logger.error("O novo binário falhou no teste de boot! Abortando update.")
                return False

            if progress_callback:
                progress_callback(0.8, "apply")

            if self.os_name == "windows":
                self._apply_windows_update(payload_root)
            else:
                self._apply_linux_update(payload_root)
            return True
        except Exception as e:
            logger.error(f"Falha ao aplicar atualização completa: {e}")
            return False
        finally:
            if extract_dir.exists():
                shutil.rmtree(extract_dir, ignore_errors=True)

    def _test_boot(self, binary_path):
        try:
            if self.os_name == "linux":
                os.chmod(str(binary_path), 0o755)

            logger.info("Validando boot do novo binário...")
            result = subprocess.run(
                [str(binary_path), "--test-boot"],
                capture_output=True,
                text=True,
                timeout=20,
            )
            return "BOOT_OK" in (result.stdout or "")
        except Exception as e:
            logger.error(f"Novo binário falhou no teste de execução: {e}")
            return False

    def _apply_linux_update(self, payload_root: Path):
        logger.info("Aplicando update Linux (cópia do pacote)...")
        target = get_app_dir()
        self._copy_payload(payload_root, target)
        os.chmod(str(self.current_exe), 0o755)
        self._restart_app()

    def _apply_windows_update(self, payload_root: Path):
        """Copia o pacote extraído por um .bat depois que o processo atual sair."""
        logger.info("Preparando script de atualização anti-lock para Windows...")
        bat_path = get_app_dir() / "update_toonix.bat"
        staging = get_app_dir() / "_pending_full_update"
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
        shutil.copytree(payload_root, staging)

        bat_content = f"""@echo off
setlocal
cd /d "{get_app_dir()}"
echo Aguardando processo "{self.current_exe.name}" encerrar...

:waitloop
tasklist | find /i "{self.current_exe.name}" > nul
if not errorlevel 1 (
    timeout /t 1 > nul
    goto waitloop
)

echo Processo finalizado. Atualizando arquivos...
xcopy /E /Y /I /Q "{staging}\\*" "{get_app_dir()}\\"
if exist "{self.current_exe}" (
    echo Atualizacao concluida com sucesso.
    rmdir /S /Q "{staging}" 2>nul
    start "" "{self.current_exe}"
) else (
    echo [ERRO] Falha na atualizacao: executavel nao encontrado!
    pause
)

del "%~f0"
exit
"""
        with open(bat_path, "w", encoding="cp1252") as f:
            f.write(bat_content)

        logger.info("Disparando script de atualização e encerrando app.")
        CREATE_NEW_CONSOLE = 0x00000010
        try:
            subprocess.Popen(["cmd", "/c", str(bat_path)], creationflags=CREATE_NEW_CONSOLE)
            sys.exit(0)
        except Exception as e:
            logger.error(f"Erro ao disparar Popen no Windows: {e}")
            subprocess.Popen([str(bat_path)], shell=True)
            sys.exit(0)

    def _copy_payload(self, source: Path, dest: Path):
        for item in source.iterdir():
            target = dest / item.name
            if item.is_dir():
                if target.exists():
                    shutil.rmtree(target, ignore_errors=True)
                shutil.copytree(item, target)
            else:
                shutil.copy2(item, target)

    def _restart_app(self):
        logger.info("Reiniciando após atualização...")
        args = [str(self.current_exe)] + [a for a in sys.argv[1:] if a != "--test-boot"]
        if getattr(sys, "frozen", False):
            subprocess.Popen(args, cwd=str(get_app_dir()))
        else:
            subprocess.Popen([sys.executable, *sys.argv], cwd=str(get_app_dir()))
        sys.exit(0)

    @staticmethod
    def _safe_unlink(path: Path):
        try:
            if path.exists():
                path.unlink()
        except OSError:
            pass

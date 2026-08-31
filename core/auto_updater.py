"""
Sistema de Atualização Automática via Git/GitHub
Atualiza código vivo (web_app, core, layouts) sem rebuild do PyInstaller.
"""
import os
import sys
import json
import shutil
import logging
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import Optional, Dict, Tuple

logger = logging.getLogger(__name__)

# Fallback se não detectar origin
DEFAULT_REPO = "Noixfrio/WebtoonCleanerUltimate"
DEFAULT_BRANCH = "master"

# Pastas que serão atualizadas (código vivo)
LIVE_FOLDERS = [
    "web_app",
    "core",
    "launcher",
    "config",
    "locales",
    "tools",
    "experimental_hybrid_cleaner",
    "webtoon_editor_test",
]


class AutoUpdater:
    def __init__(self, app_dir: Path):
        self.app_dir = Path(app_dir)
        self.is_frozen = getattr(sys, "frozen", False)
        self.skip_update = os.environ.get("TOONIX_SKIP_UPDATE", "0") == "1"

        # Detectar se é git clone ou instalação release
        self.git_dir = self.app_dir / ".git"
        self.is_git_repo = self.git_dir.exists()

        # Arquivo de commit local
        self.commit_file = self.app_dir / "runtime" / "current_commit.txt"
        self.commit_file.parent.mkdir(exist_ok=True)

    def get_repo_info(self) -> Tuple[str, str]:
        """Retorna (owner/repo, branch) detectando do git ou usando fallback."""
        if self.is_git_repo:
            try:
                # Pegar remote origin URL
                result = subprocess.run(
                    ["git", "config", "--get", "remote.origin.url"],
                    cwd=str(self.app_dir),
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    url = result.stdout.strip()
                    # Parse github.com/owner/repo ou git@github.com:owner/repo
                    if "github.com" in url:
                        if url.endswith(".git"):
                            url = url[:-4]
                        if "github.com/" in url:
                            repo = url.split("github.com/")[1]
                        elif "github.com:" in url:
                            repo = url.split("github.com:")[1]
                        else:
                            repo = DEFAULT_REPO
                    else:
                        repo = DEFAULT_REPO
                else:
                    repo = DEFAULT_REPO

                # Pegar branch atual
                result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    cwd=str(self.app_dir),
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                branch = result.stdout.strip() if result.returncode == 0 else DEFAULT_BRANCH

                return repo, branch
            except Exception as e:
                logger.warning(f"Falha ao detectar repo git: {e}")

        return DEFAULT_REPO, DEFAULT_BRANCH

    def get_local_commit(self) -> Optional[str]:
        """Retorna o SHA do commit local atual."""
        if self.is_git_repo:
            try:
                result = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=str(self.app_dir),
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    return result.stdout.strip()[:7]  # Short SHA
            except Exception as e:
                logger.debug(f"git rev-parse falhou: {e}")

        # Fallback: ler do arquivo
        if self.commit_file.exists():
            try:
                return self.commit_file.read_text(encoding="utf-8").strip()
            except Exception:
                pass

        return None

    def get_remote_commit(self, repo: str, branch: str) -> Optional[Dict]:
        """Consulta o commit mais recente via GitHub API."""
        try:
            import requests

            url = f"https://api.github.com/repos/{repo}/commits/{branch}"
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "ToonixAutoUpdater/1.0",
            }

            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    "sha": data["sha"][:7],
                    "full_sha": data["sha"],
                    "message": data["commit"]["message"].split("\n")[0][:80],
                    "author": data["commit"]["author"]["name"],
                    "date": data["commit"]["author"]["date"],
                }
        except Exception as e:
            logger.error(f"Falha ao consultar GitHub API: {e}")

        return None

    def check_for_updates(self) -> Optional[Dict]:
        """
        Verifica se há atualização disponível.
        Retorna dict com info do update ou None se já está atualizado.
        """
        if self.skip_update:
            logger.info("Auto-update desabilitado (TOONIX_SKIP_UPDATE=1)")
            return None

        logger.info("Verificando atualizações...")

        repo, branch = self.get_repo_info()
        local_commit = self.get_local_commit()

        logger.info(f"Repo: {repo}, Branch: {branch}, Commit local: {local_commit or 'desconhecido'}")

        try:
            remote_info = self.get_remote_commit(repo, branch)
            if not remote_info:
                logger.warning("Não foi possível consultar commit remoto")
                return None

            remote_sha = remote_info["sha"]

            if local_commit and local_commit == remote_sha:
                logger.info(f"✓ Já está atualizado ({remote_sha})")
                return None

            logger.info(f"Nova versão disponível: {remote_sha} - {remote_info['message']}")
            return {
                "repo": repo,
                "branch": branch,
                "local_sha": local_commit,
                "remote_sha": remote_sha,
                "remote_info": remote_info,
            }
        except Exception as e:
            logger.error(f"Erro ao verificar updates: {e}")
            return None

    def apply_update(self, update_info: Dict) -> bool:
        """
        Aplica a atualização usando git pull (se repo) ou download ZIP.
        Retorna True se aplicou com sucesso.
        """
        repo = update_info["repo"]
        branch = update_info["branch"]
        remote_sha = update_info["remote_sha"]

        logger.info(f"Aplicando atualização para {remote_sha}...")

        # Método 1: Git pull (preferido para desenvolvimento)
        if self.is_git_repo:
            if self._git_pull(branch):
                self._save_commit(remote_sha)
                logger.info("✓ Atualização via git pull concluída")
                return True
            else:
                logger.warning("git pull falhou, tentando download ZIP...")

        # Método 2: Download ZIP do GitHub (para release/instalação)
        if self._download_and_extract_zip(repo, branch):
            self._save_commit(remote_sha)
            logger.info("✓ Atualização via ZIP concluída")
            return True

        logger.error("Falha ao aplicar atualização")
        return False

    def _git_pull(self, branch: str) -> bool:
        """Executa git pull na branch."""
        try:
            # Primeiro, verificar se há mudanças locais
            result = subprocess.run(
                ["git", "diff", "--quiet"],
                cwd=str(self.app_dir),
                timeout=5,
            )
            has_changes = result.returncode != 0

            if has_changes:
                logger.warning("Há mudanças locais não commitadas, fazendo stash...")
                subprocess.run(
                    ["git", "stash"],
                    cwd=str(self.app_dir),
                    timeout=10,
                )

            # Pull
            result = subprocess.run(
                ["git", "pull", "origin", branch],
                cwd=str(self.app_dir),
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                logger.info(f"git pull: {result.stdout.strip()}")
                return True
            else:
                logger.error(f"git pull falhou: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Erro no git pull: {e}")
            return False

    def _download_and_extract_zip(self, repo: str, branch: str) -> bool:
        """Baixa ZIP do GitHub e extrai para a pasta viva."""
        try:
            import requests

            # URL do ZIP: https://github.com/owner/repo/archive/refs/heads/branch.zip
            zip_url = f"https://github.com/{repo}/archive/refs/heads/{branch}.zip"

            logger.info(f"Baixando {zip_url}...")

            # Download para temp (no disco S: se possível)
            temp_dir = Path(os.environ.get("TEMP", tempfile.gettempdir()))
            # Preferir disco do app_dir se temp for C:
            if "C:\\" in str(temp_dir) or "c:\\" in str(temp_dir):
                temp_dir = self.app_dir / "temp"
                temp_dir.mkdir(exist_ok=True)

            zip_path = temp_dir / f"toonix_update_{branch}.zip"

            response = requests.get(zip_url, timeout=120, stream=True)
            response.raise_for_status()

            with open(zip_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)

            logger.info(f"Download concluído: {zip_path}")

            # Extrair
            extract_dir = temp_dir / "toonix_extract"
            if extract_dir.exists():
                shutil.rmtree(extract_dir)
            extract_dir.mkdir()

            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(extract_dir)

            # Encontrar a pasta raiz (GitHub cria pasta owner-repo-branch)
            root_folders = list(extract_dir.iterdir())
            if len(root_folders) == 1 and root_folders[0].is_dir():
                source_root = root_folders[0]
            else:
                source_root = extract_dir

            # Copiar pastas vivas
            logger.info("Copiando arquivos atualizados...")
            for folder_name in LIVE_FOLDERS:
                source = source_root / folder_name
                if not source.exists():
                    continue

                dest = self.app_dir / folder_name
                if dest.exists():
                    shutil.rmtree(dest)

                shutil.copytree(source, dest)
                logger.debug(f"  ✓ {folder_name}")

            # Cleanup
            zip_path.unlink()
            shutil.rmtree(extract_dir)

            return True

        except Exception as e:
            logger.error(f"Erro ao baixar/extrair ZIP: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _save_commit(self, sha: str):
        """Salva o commit atual no arquivo."""
        try:
            self.commit_file.write_text(sha, encoding="utf-8")
        except Exception as e:
            logger.warning(f"Falha ao salvar commit: {e}")

    def run_update_check_and_apply(self) -> Tuple[bool, Optional[str]]:
        """
        Execução completa: verifica e aplica update se disponível.
        Retorna (updated, commit_sha).
        """
        try:
            update_info = self.check_for_updates()
            if not update_info:
                return False, self.get_local_commit()

            # Aplicar atualização
            success = self.apply_update(update_info)
            new_commit = update_info["remote_sha"] if success else self.get_local_commit()

            return success, new_commit

        except Exception as e:
            logger.error(f"Erro no update check/apply: {e}")
            return False, self.get_local_commit()

"""
Script de teste rápido do sistema de atualização automática.
Execute com: python test_auto_update.py
"""
import sys
from pathlib import Path

# Adicionar path do projeto
sys.path.insert(0, str(Path(__file__).parent))

from core.auto_updater import AutoUpdater


def test_update_check():
    print("=" * 60)
    print("TESTE: Sistema de Atualização Automática")
    print("=" * 60)
    print()

    app_dir = Path(__file__).parent
    updater = AutoUpdater(app_dir)

    print(f"[INFO] Diretório: {updater.app_dir}")
    print(f"[INFO] É repo Git: {updater.is_git_repo}")
    print(f"[INFO] Skip update: {updater.skip_update}")
    print()

    # Detectar repositório
    repo, branch = updater.get_repo_info()
    print(f"[REPO] {repo} @ {branch}")
    print()

    # Commit local
    local_commit = updater.get_local_commit()
    print(f"[LOCAL] Commit: {local_commit or '(não detectado)'}")
    print()

    # Verificar atualização
    print("[CHECK] Consultando GitHub API...")
    update_info = updater.check_for_updates()

    if update_info:
        print(f"[UPDATE] Nova versão disponível!")
        print(f"         Local:  {update_info['local_sha']}")
        print(f"         Remoto: {update_info['remote_sha']}")
        print(f"         Msg:    {update_info['remote_info']['message']}")
        print()
        print("[INFO] Para aplicar, feche e abra o app normalmente")
    else:
        print("[OK] Sistema já está atualizado!")

    print()
    print("=" * 60)
    print("Teste concluído!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_update_check()
    except KeyboardInterrupt:
        print("\n[CANCEL] Teste cancelado pelo usuário")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

import sys
import os
import webbrowser
import threading
import time
import uvicorn
import multiprocessing

# Necessário para que o PyInstaller funcione com multiprocessing no Windows
if __name__ == "__main__":
    multiprocessing.freeze_support()

def open_browser():
    """Abre o navegador automaticamente após um pequeno delay."""
    time.sleep(2.5)
    print("\n[+] Abrindo navegador em http://localhost:5000")
    webbrowser.open("http://localhost:5000")

def run_ultra_server():
    """Inicia o servidor Ultra IA (Porta 5001)"""
    try:
        from web_app.ultra_main import app as ultra_app
        print("[+] Servidor Ultra IA pronto na porta 5001")
        uvicorn.run(ultra_app, host="127.0.0.1", port=5001, log_level="error")
    except Exception as e:
        print(f"[!] Erro ao iniciar Ultra IA: {e}")

def run_pro_editor_server():
    """Inicia o servidor Editor Profissional (Porta 5002)"""
    try:
        from webtoon_editor_test.app import app as pro_app
        print("[+] Servidor Editor Pro pronto na porta 5002")
        # Flask run em modo produção (sem debug para não spawnar thread extra no freeze)
        pro_app.run(host="127.0.0.1", port=5002, debug=False, threaded=True)
    except Exception as e:
        print(f"[!] Erro ao iniciar Editor Pro: {e}")

def main():
    # Detecta se está rodando como executável
    is_frozen = getattr(sys, 'frozen', False)
    
    if is_frozen:
        # No modo frozen, o PyInstaller descompacta tudo em um temp dir ou na pasta do exe
        # Precisamos garantir que os paths de templates/static funcionem
        print(f"[+] Iniciando Manga Cleaner em modo executável...")
    else:
        print(f"[+] Iniciando em modo de desenvolvimento...")

    # Tenta rodar o auto-updater antes de iniciar o servidor
    try:
        from core.updater import run_update_process
        print("[+] Verificando atualizações no GitHub...")
        run_update_process()
    except Exception as e:
        print(f"[!] Aviso: Nao foi possivel verificar atualizações: {e}")

    # Iniciar Servidores Auxiliares em Threads
    threading.Thread(target=run_ultra_server, daemon=True).start()
    threading.Thread(target=run_pro_editor_server, daemon=True).start()

    # Inicia a thread do navegador
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Importa o app aqui para garantir que o path esteja correto
    try:
        from web_app.main import app
        print("[+] Servidor Principal pronto na porta 5000")
        uvicorn.run(app, host="127.0.0.1", port=5000, log_level="info")
    except Exception as e:
        print(f"\n[ERRO CRÍTICO] Falha ao iniciar o servidor principal: {e}")
        input("\nPressione Enter para sair...")

if __name__ == "__main__":
    main()

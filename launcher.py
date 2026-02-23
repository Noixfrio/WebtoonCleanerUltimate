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

def main():
    # Detecta se está rodando como executável
    is_frozen = getattr(sys, 'frozen', False)
    
    if is_frozen:
        # Define o diretório base como a pasta do .exe
        base_dir = os.path.dirname(sys.executable)
        os.chdir(base_dir)
        print(f"[+] Iniciando Manga Cleaner em modo executável...")
    else:
        print(f"[+] Iniciando em modo de desenvolvimento...")

    # Se estiver congelado, o PyInstaller coloca os arquivos em sys._MEIPASS
    # Mas queremos que o banco de dados e arquivos processados fiquem na pasta do .exe
    
    # Inicia a thread do navegador
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Importa o app aqui para garantir que o path esteja correto
    try:
        from web_app.main import app
        print("[+] Servidor pronto na porta 5000")
        uvicorn.run(app, host="127.0.0.1", port=5000, log_level="info")
    except Exception as e:
        print(f"\n[ERRO CRÍTICO] Falha ao iniciar o servidor: {e}")
        input("\nPressione Enter para sair...")

if __name__ == "__main__":
    main()

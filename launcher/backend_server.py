import uvicorn
import threading
try:
    from web_app.main import app
except Exception as e:
    import logging
    logging.error(f"FALHA CRÍTICA AO IMPORTAR WEB_APP: {e}")
    app = None

from launcher.logger import logger

class BackendServer:
    def __init__(self, host="127.0.0.1", port=5000):
        self.host = host
        self.port = port
        self.server_thread = None
        self.should_exit = False
        self._kill_existing_server()

    def _kill_existing_server(self):
        """ Garante que a porta não esteja em uso por uma instância anterior. """
        import subprocess
        try:
            # Tentar matar processo na porta (Linux/macOS)
            subprocess.run(["fuser", "-k", f"{self.port}/tcp"], capture_output=True)
            logger.info(f"Limpeza da porta {self.port} concluída.")
        except:
            pass

    def _run_server(self):
        try:
            logger.info(f"Iniciando servidor interno em {self.host}:{self.port}")
            if app is None:
                logger.error("App não carregado corretamente no servidor.")
                return

            config = uvicorn.Config(
                app, 
                host=self.host, 
                port=self.port, 
                log_level="info",
                reload=False,
                access_log=False
            )
            server = uvicorn.Server(config)
            server.run()
        except Exception as e:
            logger.error(f"Erro na thread do servidor: {e}")

    def _run_pro_server(self):
        """ Inicia o Editor Pro (Flask) em uma thread interna para compartilhar o ambiente. """
        import sys
        import os
        from launcher.utils import get_resource_path
        
        pro_app_path = get_resource_path("webtoon_editor_test/app.py")
        if pro_app_path.exists():
            logger.info("Iniciando Editor Pro em port 5002 via thread interna.")
            
            # Garantir que a porta 5002 esteja livre
            try:
                import subprocess
                subprocess.run(["fuser", "-k", "5002/tcp"], capture_output=True)
            except:
                pass

            try:
                # Adicionar caminhos críticos ao sys.path para permitir imports internos do app
                root_path = get_resource_path(".")
                pro_dir = get_resource_path("webtoon_editor_test")
                
                # Inserir no início para prioridade
                for p in [str(root_path), str(pro_dir)]:
                    if p not in sys.path:
                        sys.path.insert(0, p)
                
                # Importar dinamicamente o app do Editor Pro
                from webtoon_editor_test.app import app as pro_flask_app
                
                logger.info("Flask App (Pro) carregado. Iniciando servidor...")
                # Rodar Flask sem debug e sem reloader para evitar threads duplicadas
                pro_flask_app.run(host="127.0.0.1", port=5002, debug=False, use_reloader=False)
            except Exception as e:
                logger.error(f"Erro Crítico ao rodar Editor Pro internamente: {e}")
                import traceback
                logger.error(traceback.format_exc())
        else:
            logger.warning("Editor Pro não encontrado para carregamento interno.")

    def start(self):
        try:
            # 1. Thread do Servidor Principal (5000)
            self.server_thread = threading.Thread(target=self._run_server, daemon=True)
            self.server_thread.start()
            
            # 2. Thread do Servidor Pro (5002) - Opcional
            self.pro_server_thread = threading.Thread(target=self._run_pro_server, daemon=True)
            self.pro_server_thread.start()
            
            logger.info("Threads do backend disparadas.")
        except Exception as e:
            logger.error(f"Falha ao disparar threads: {e}")

def start_backend():
    try:
        logger.info("Tentando instanciar BackendServer...")
        server = BackendServer()
        logger.info("Chamando server.start()...")
        server.start()
        return server
    except Exception as e:
        logger.error(f"Erro Crítico em start_backend: {e}")
        print(f"[ERROR] start_backend: {e}")
        raise e

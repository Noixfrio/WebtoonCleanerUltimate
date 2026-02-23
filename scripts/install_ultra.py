import os
import sys
import logging

# Adiciona o diretório raiz ao path para importar o core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.advanced_inpaint import get_lama_engine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    print("======================================================")
    print("      Instalador de Modelos - IA ULTRA")
    print("======================================================")
    print("\n[+] Iniciando download do modelo LaMa (aprox. 190MB)...")
    print("[+] Isso pode demorar dependendo da sua internet.")
    
    try:
        # A função get_lama_engine() já chama _load_model() que faz o download se não existir
        engine = get_lama_engine()
        
        if engine.is_available():
            print("\n======================================================")
            print("      MODELO BAIXADO E CARREGADO COM SUCESSO!")
            print("======================================================")
            print(f"\nLocal: {engine.model_path}")
        else:
            print("\n[ERRO] O modelo foi baixado mas não pôde ser carregado.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n[ERRO CRÍTICO] Falha ao baixar o modelo: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

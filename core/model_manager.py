import os
import logging
from pathlib import Path
from huggingface_hub import hf_hub_download

# Configuração de logger local
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("ModelManager")

class ModelManager:
    """
    Gerencia o download e a verificação de modelos de IA via Hugging Face Hub.
    Elimina dependência de URLs externas de terceiros.
    """
    
    HF_REPO_ID = "samyuush/ToonixModels"
    
    # Mapeamento do nome do arquivo no repositório para o caminho local de destino
    MODELS = {
        "lama.onnx": {
            "remote_name": "lama.onnx",
            "path": "models/lama_512.onnx"
        },
        "craft_mlt_25k.pth": {
            "remote_name": "craft_mlt_25k.pth",
            "path": "assets/ocr/model/craft_mlt_25k.pth"
        },
        "english_g2.pth": {
            "remote_name": "english_g2.pth",
            "path": "assets/ocr/model/english_g2.pth"
        }
    }

    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path(os.getcwd())
        # Garantir pasta models padrão caso não exista
        (self.base_dir / "models").mkdir(parents=True, exist_ok=True)

    def get_missing_models(self):
        """Retorna uma lista de modelos que ainda não foram baixados."""
        missing = []
        for name, info in self.MODELS.items():
            full_path = self.base_dir / info["path"]
            if not full_path.exists():
                missing.append(name)
        return missing

    def download_model(self, model_name, progress_callback=None):
        """
        Baixa um modelo do Hugging Face Hub usando hf_hub_download.
        Necessário configurar HF_TOKEN no ambiente.
        """
        if model_name not in self.MODELS:
            raise ValueError(f"Modelo {model_name} desconhecido.")

        token = os.getenv("HF_TOKEN")
        if not token:
            logger.error("Erro: Variável de ambiente HF_TOKEN não encontrada.")
            return False

        info = self.MODELS[model_name]
        remote_name = info["remote_name"]
        dest_path = self.base_dir / info["path"]
        
        # Garantir diretório pai
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            logger.info(f"Iniciando download robusto de {model_name}...")
            
            # hf_hub_download verifica se o arquivo já é o mais atual e baixa se necessário
            # Usamos local_dir para manter a estrutura do projeto
            local_path = hf_hub_download(
                repo_id=self.HF_REPO_ID,
                filename=remote_name,
                token=token,
                local_dir=self.base_dir,
                local_dir_use_symlinks=False # Importante para portabilidade do PyInstaller
            )
            
            # Como hf_hub_download baixa para a estrutura do repositório,
            # talvez precisemos mover para o caminho específico esperado se forem diferentes.
            # No nosso caso, 'path' em MODELS define o destino final esperado pelo código legado.
            
            downloaded_file = Path(local_path)
            if downloaded_file.exists() and downloaded_file != dest_path:
                # Mover para o local exato esperado caso o hf_hub_download use a estrutura do repo
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                downloaded_file.replace(dest_path)

            logger.info(f"Modelo {model_name} integrado com sucesso.")
            return True

        except Exception as e:
            if "401" in str(e):
                logger.error(f"Erro de Autorização (401): Verifique se o seu HF_TOKEN é válido e tem acesso ao repositório {self.HF_REPO_ID}.")
            elif "404" in str(e):
                logger.error(f"Erro: Arquivo {remote_name} não encontrado no repositório {self.HF_REPO_ID} (404).")
            else:
                logger.error(f"Falha ao baixar modelo {model_name}: {e}")
            return False

    def check_and_download_all(self, progress_hook=None):
        """Lógica de inicialização automática."""
        missing = self.get_missing_models()
        if not missing:
            logger.info("Todos os modelos de IA estão pronto para uso.")
            return True

        for model_name in missing:
            # hf_hub_download gerencia progresso internamente na console
            success = self.download_model(model_name)
            if not success:
                return False
                
        return True

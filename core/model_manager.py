import os
import requests
import logging
from pathlib import Path

# Configuração de logger local para garantir independência total do arquivo
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("ModelManager")

class ModelManager:
    """
    Gerencia o download e a verificação de modelos de IA.
    Evita que o binário do app exceda 2GB ao baixar modelos sob demanda.
    """
    
    # Mapeamento de modelos e URLs (Pode ser movido para um config.json no futuro)
    MODELS = {
        "lama.onnx": {
            "url": "https://huggingface.co/Carve/LaMa-ONNX/resolve/main/lama.onnx",
            "path": "models/lama_512.onnx", 
            "size_approx": "194MB"
        },
        "craft_mlt_25k.pth": {
            "url": "https://github.com/JaidedAI/EasyOCR/releases/download/v1.3/craft_mlt_25k.zip",
            "path": "assets/ocr/model/craft_mlt_25k.pth",
            "is_zip": True,
            "size_approx": "15MB"
        },
        "english_g2.pth": {
            "url": "https://github.com/JaidedAI/EasyOCR/releases/download/v1.3/english_g2.zip",
            "path": "assets/ocr/model/english_g2.pth",
            "is_zip": True,
            "size_approx": "25MB"
        }
    }

    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path(os.getcwd())

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
        Baixa um modelo específico com feedback de progresso.
        
        Args:
            model_name: Chave no dicionário MODELS.
            progress_callback: Função que recebe (current_bytes, total_bytes).
        """
        if model_name not in self.MODELS:
            raise ValueError(f"Modelo {model_name} desconhecido.")

        info = self.MODELS[model_name]
        url = info["url"]
        dest_path = self.base_dir / info["path"]
        
        # Garantir diretório pai
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        temp_path = dest_path.with_suffix(".tmp")
        
        try:
            logger.info(f"Iniciando download de {model_name}...")
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            with open(temp_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        if progress_callback and total_size > 0:
                            progress_callback(downloaded_size, total_size)

            # Se for ZIP (caso do EasyOCR), deveríamos extrair. 
            # Para simplificar este módulo seguindo o requisito de "requests", 
            # vamos assumir download direto ou tratar extração se necessário.
            if info.get("is_zip"):
                import zipfile
                import io
                with zipfile.ZipFile(temp_path, 'r') as zip_ref:
                    # Extrair apenas o arquivo .pth para o destino correto
                    # O EasyOCR espera o .pth direto no diretório
                    filename = Path(info["path"]).name
                    with zip_ref.open(filename) as source, open(dest_path, "wb") as target:
                        target.write(source.read())
                temp_path.unlink()
            else:
                temp_path.replace(dest_path)
                
            logger.info(f"Download de {model_name} concluído com sucesso.")
            return True

        except Exception as e:
            logger.error(f"Erro ao baixar {model_name}: {e}")
            if temp_path.exists():
                temp_path.unlink() # Limpa arquivo corrompido
            return False

    def check_and_download_all(self, progress_hook=None):
        """
        Lógica principal de inicialização. 
        Pode ser chamada no boot do app.
        """
        missing = self.get_missing_models()
        if not missing:
            logger.info("Todos os modelos de IA já estão presentes.")
            return True

        total_models = len(missing)
        for i, model_name in enumerate(missing):
            # Hook para UI atualizar status geral (ex: "Baixando modelo 1/3")
            current_model_idx = i + 1
            
            def individual_progress(current, total):
                if progress_hook:
                    # Normaliza o progresso entre 0 e 1 considerando o total de modelos
                    base_progress = i / total_models
                    model_progress = (current / total) / total_models
                    progress_hook(base_progress + model_progress, model_name)

            success = self.download_model(model_name, progress_callback=individual_progress)
            if not success:
                return False
                
        return True

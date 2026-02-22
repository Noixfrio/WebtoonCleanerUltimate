import os
import json
import shutil
from typing import List, Dict

class WebtoonFontManager:
    def __init__(self):
        # Define base_dir absolute based on file location
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_path = os.path.join(self.base_path, "config", "webtoon_font_database.json")
        self.fonts_dir = os.path.join(self.base_path, "assets", "fonts")
        self.custom_dir = os.path.join(self.fonts_dir, "custom")
        
        if not os.path.exists(self.custom_dir):
            os.makedirs(self.custom_dir, exist_ok=True)
            
        # Ensure all category directories exist to avoid mounting or scan errors
        categories = ["dialogue", "impact", "thought", "narrator", "sfx", "romance", "digital", "custom"]
        for cat in categories:
            cat_path = os.path.join(self.fonts_dir, cat)
            os.makedirs(cat_path, exist_ok=True)

    def _load_config(self) -> Dict:
        if not os.path.exists(self.config_path):
            return {
                "dialogue": [], "impact": [], "thought": [], 
                "narrator": [], "sfx": [], "romance": [], 
                "digital": [], "custom": []
            }
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_config(self, config: Dict):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def list_fonts(self) -> Dict[str, List[str]]:
        """Retorna todas as fontes organizadas por categoria."""
        return self._load_config()

    def get_by_category(self, category: str) -> List[str]:
        """Retorna fontes de uma categoria específica."""
        config = self._load_config()
        return config.get(category, [])

    def import_font(self, file_path: str) -> bool:
        """
        Importa um arquivo de fonte (.ttf ou .otf) para a pasta custom.
        file_path deve ser um caminho absoluto para o arquivo temporário.
        """
        if not (file_path.endswith('.ttf') or file_path.endswith('.otf')):
            raise ValueError("Apenas arquivos .ttf e .otf são aceitos.")

        font_name = os.path.basename(file_path)
        dest_path = os.path.join(self.custom_dir, font_name)

        if os.path.exists(dest_path):
            # Já existe, mas vamos registrar no JSON se não estiver lá
            self.register_custom_font(font_name)
            return True

        shutil.copy2(file_path, dest_path)
        self.register_custom_font(font_name)
        return True

    def register_custom_font(self, font_name: str):
        """Registra o nome da fonte na categoria 'custom' do JSON."""
        config = self._load_config()
        if font_name not in config["custom"]:
            config["custom"].append(font_name)
            self._save_config(config)

if __name__ == "__main__":
    # Exemplo simples de uso
    manager = WebtoonFontManager()
    print("Fontes Dialogue:", manager.get_by_category("dialogue"))

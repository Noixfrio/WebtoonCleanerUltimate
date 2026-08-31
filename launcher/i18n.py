import json
from launcher.utils import get_resource_path

class Translator:
    def __init__(self, default_lang="pt-br"):
        self.current_lang = default_lang
        self.locales_dir = get_resource_path("locales")
        self.translations = {}
        self.load_language(default_lang)

    def load_language(self, lang_code):
        file_path = self.locales_dir / f"{lang_code}.json"
        if not file_path.exists():
            # Fallback para o primeiro arquivo disponível se o solicitado falhar
            files = list(self.locales_dir.glob("*.json"))
            if not files:
                self.translations = {}
                return
            file_path = files[0]
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.translations = json.load(f)
            self.current_lang = lang_code
        except Exception:
            self.translations = {}

    def translate(self, key, default=None):
        return self.translations.get(key, default or key)

    def get_available_languages(self):
        return [f.stem for f in self.locales_dir.glob("*.json")]

# Singleton (será inicializado no boot)
i18n = Translator()
_ = i18n.translate

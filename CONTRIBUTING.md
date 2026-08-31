# 🤝 Guia de Contribuição

Obrigado por considerar contribuir para o **Webtoon Cleaner Ultimate**! Este documento fornece diretrizes e orientações para contribuir com o projeto.

---

## 📋 Código de Conduta

Por favor leia nosso [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) para entender nossos padrões de comunidade.

---

## 🐛 Reportar Bugs

### Antes de Reportar
- Verifique se o bug já foi reportado em [Issues](https://github.com/Noixfrio/WebtoonCleanerUltimate/issues)
- Confirme que está usando a versão mais recente
- Teste em ambiente limpo se possível

### Como Reportar
1. Vá para [Issues](https://github.com/Noixfrio/WebtoonCleanerUltimate/issues/new?template=bug_report.md)
2. Use o template disponível
3. Forneça:
   - Descrição clara do bug
   - Passos para reproduzir
   - Comportamento esperado vs. observado
   - Screenshots/logs se aplicável
   - Seu sistema (Windows/Linux/macOS, Python version, etc)

---

## 💡 Sugerir Melhorias

1. Verifique [Discussions](https://github.com/Noixfrio/WebtoonCleanerUltimate/discussions) se já foi sugerido
2. Crie uma nova discussion ou issue com:
   - Descrição clara da funcionalidade
   - Caso de uso / por que seria útil
   - Exemplo de como funcionaria idealmente

---

## 🚀 Pull Requests

### Preparação
1. **Fork** o repositório
2. **Clone** seu fork:
   ```bash
   git clone https://github.com/seu-usuario/WebtoonCleanerUltimate.git
   cd WebtoonCleanerUltimate
   ```
3. **Crie uma branch** descritiva:
   ```bash
   git checkout -b fix/ocr-windows-charmap
   # ou
   git checkout -b feature/dark-theme
   ```

### Desenvolvimento
1. **Configure o ambiente:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # ou venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

2. **Faça suas mudanças** seguindo o estilo de código:
   - PEP 8 para Python
   - Nomes descritivos para variáveis/funções
   - Docstrings em todas as funções públicas
   - Comentários para lógica complexa

3. **Teste suas mudanças:**
   ```bash
   pytest tests/ -v
   # ou teste manualmente
   python launcher.py --skip-update
   ```

4. **Commit com mensagens claras:**
   ```bash
   git add .
   git commit -m "fix: resolve charmap encoding on Windows OCR
   
   - Added UTF-8 encoding wrapper for stdout/stderr
   - Redirects easyocr output during initialization
   - Fixes issue #123"
   ```

### Submeter PR
1. **Push para seu fork:**
   ```bash
   git push origin fix/ocr-windows-charmap
   ```

2. **Abra um Pull Request** no repositório principal
3. Use o template fornecido
4. Descreva suas mudanças claramente
5. Referencie issues relacionadas (#123)
6. Espere por revisão e feedback

---

## 📝 Convenções de Código

### Python
```python
# ✅ Bom
def process_image(image_path: str, quality: int = 85) -> np.ndarray:
    """
    Process image with specified quality.
    
    Args:
        image_path: Path to input image
        quality: Output quality (0-100)
        
    Returns:
        Processed image array
    """
    image = cv2.imread(image_path)
    # Process...
    return result

# ❌ Ruim
def process_img(img_path, q=85):
    img = cv2.imread(img_path)
    # Process...
    return result
```

### Commits
```bash
# ✅ Bom
git commit -m "feat: add dark theme support

- Implement theme switching in UI
- Add config persistence
- Update docs"

git commit -m "fix: windows charmap encoding in OCR"

# ❌ Ruim
git commit -m "stuff"
git commit -m "fixed bugs"
```

### Branches
```bash
# ✅ Bom
git checkout -b feature/dark-theme
git checkout -b fix/ocr-crash
git checkout -b docs/update-readme
git checkout -b refactor/pipeline-core

# ❌ Ruim
git checkout -b my-fix
git checkout -b new-stuff
```

---

## 🏗️ Estrutura do Projeto

```
WebtoonCleanerUltimate/
├── launcher/           # Interface GUI (CustomTkinter)
│   ├── main.py        # Entry point
│   ├── ui.py          # UI components
│   └── backend_server.py
├── web_app/           # Backend FastAPI
│   ├── main.py        # API routes
│   ├── routes.py      # Additional routes
│   └── templates/     # HTML templates
├── core/              # Motor de processamento
│   ├── pipeline.py    # Main processing pipeline
│   ├── detector.py    # OCR engine
│   ├── inpaint_engine.py  # IA inpainting
│   ├── mask_builder.py    # Mask generation
│   └── model_manager.py   # Model downloads
├── tools/             # Utilities
├── tests/             # Test suite
├── config/            # Configurations
│   └── settings.py    # App settings
├── assets/            # Resources
├── docs/              # Documentation
└── requirements.txt   # Dependencies
```

---

## 🧪 Testes

### Rodando Testes
```bash
# Todos os testes
pytest tests/ -v

# Teste específico
pytest tests/test_core_mvp.py::test_ocr_detection -v

# Com coverage
pytest --cov=core tests/
```

### Escrevendo Testes
```python
import pytest
from core.pipeline import MangaCleanerPipeline

def test_pipeline_initialization():
    """Test that pipeline initializes correctly."""
    pipeline = MangaCleanerPipeline()
    assert pipeline is not None
    assert hasattr(pipeline, 'process_webtoon_streaming')

def test_image_processing():
    """Test basic image processing."""
    pipeline = MangaCleanerPipeline()
    # Create test image
    # Process
    # Assert results
    pass
```

---

## 📚 Documentação

Ao adicionar features, atualize:

1. **README.md** - Para grandes mudanças
2. **docs/WALKTHROUGH.md** - Para novas funcionalidades
3. **Docstrings** - Em código Python
4. **CHANGELOG.md** - Descreva suas mudanças

---

## 🔄 Processo de Revisão

1. **Automated Checks**: Tests, linting, type checking
2. **Code Review**: Feedback de maintainers
3. **Discussion**: Se necessário, refinement
4. **Merge**: Quando aprovado

---

## 📦 Release Process

Releases são feitas via GitHub Releases com:
- Versão semântica (v0.9.9)
- Changelog completo
- Binários pré-compilados (quando aplicável)

---

## 🎯 Áreas com Oportunidades de Contribuição

- [ ] **Documentação** - Melhorar docs/wikis
- [ ] **Testes** - Aumentar cobertura de testes
- [ ] **Performance** - Otimizar processamento
- [ ] **UX/UI** - Melhorar interface
- [ ] **Traduções** - Adicionar novos idiomas
- [ ] **Modelos** - Treinar modelos melhores
- [ ] **Plugins** - Sistema de plugins

---

## ❓ Dúvidas?

- 📖 Leia a [Documentação](docs/)
- 💬 Abra uma [Discussion](https://github.com/Noixfrio/WebtoonCleanerUltimate/discussions)
- 🐛 Crie uma [Issue](https://github.com/Noixfrio/WebtoonCleanerUltimate/issues)

---

**Obrigado por contribuir! 🙏**

Seu trabalho ajuda a melhorar a ferramenta para toda a comunidade de mangá e webtoons.

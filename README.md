# 🧹 Webtoon Cleaner Ultimate

<div align="center">

[![GitHub release](https://img.shields.io/github/v/release/Noixfrio/WebtoonCleanerUltimate?color=green&style=flat-square&label=Latest%20Release)](https://github.com/Noixfrio/WebtoonCleanerUltimate/releases)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/Noixfrio/WebtoonCleanerUltimate?style=flat-square&color=gold)](https://github.com/Noixfrio/WebtoonCleanerUltimate)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-blueviolet?style=flat-square)](README.md)

**⚡ Ferramenta de IA para limpeza profissional de mangás e webtoons**

[🚀 Começar](#-quick-start) • [📖 Documentação](#-documentação) • [🐛 Issues](https://github.com/Noixfrio/WebtoonCleanerUltimate/issues) • [💬 Discussões](https://github.com/Noixfrio/WebtoonCleanerUltimate/discussions)

</div>

---

## ✨ O que é?

**Webtoon Cleaner Ultimate** é uma aplicação desktop multiplataforma que utiliza **Inteligência Artificial** para:

- 🧹 **Remover automaticamente** balões de fala, textos e ruídos
- 🎨 **Retoque inteligente** com inpainting neural (LAMA)
- 🔤 **Edição de textos** com reconhecimento OCR
- 🖌️ **Ferramentas manuais** para controle fino
- ⚡ **Processamento rápido** otimizado para GPU/CPU
- 🌍 **Multilíngue** (PT-BR, EN, e mais)

Perfeito para **mangakás**, **tradutores**, **editores** e **entusiastas de webtoons**.

---

## 🚀 Quick Start

### Opção 1: Executável Rápido (Recomendado)

**Windows:**
```bash
git clone https://github.com/Noixfrio/WebtoonCleanerUltimate.git
cd WebtoonCleanerUltimate
START_WINDOWS.bat
```

**Linux/macOS:**
```bash
git clone https://github.com/Noixfrio/WebtoonCleanerUltimate.git
cd WebtoonCleanerUltimate
chmod +x START_LINUX.sh
./START_LINUX.sh
```

---

## 📘 Guia Completo de Instalação - Windows

### ⚡ **Para Usuários Windows - Leia Isto Primeiro!**

Se você é novo no projeto e quer instalação passo a passo, **[clique aqui e siga o INSTALL_WINDOWS.md](INSTALL_WINDOWS.md)**.

Este guia ensina **TUDO**, incluindo:
- ✅ Onde baixar Python (com link direto)
- ✅ Como instalar passo a passo
- ✅ Explicação de cada comando
- ✅ Troubleshooting completo
- ✅ Links úteis

### 🧹 Limpar Instalação Anterior (Antes de Reinstalar)

Se você tinha o projeto instalado e quer começar do zero:

**Opção 1: Clique duplo (Mais Fácil)**
1. Abra a pasta do projeto
2. Duplo clique em `CLEANUP_WINDOWS.bat`
3. Confirme e aguarde

**Opção 2: PowerShell (Mais Rápido)**
```powershell
# Abra PowerShell como Administrador
powershell -ExecutionPolicy Bypass -File cleanup_windows.ps1
```

---

### Opção 2: Instalação Manual

```bash
# 1. Clone o repositório
git clone https://github.com/Noixfrio/WebtoonCleanerUltimate.git
cd WebtoonCleanerUltimate

# 2. Crie um ambiente virtual (opcional, recomendado)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate  # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute
python launcher.py --skip-update
```

> **⏱️ Primeira execução:** Pode levar 3-5 minutos para baixar os modelos de IA (~250MB)

---

## � Links Rápidos

| Item | Link |
|------|------|
| **📘 Guia Windows Completo** | [INSTALL_WINDOWS.md](INSTALL_WINDOWS.md) |
| **🧹 Limpeza Automática** | `CLEANUP_WINDOWS.bat` ou `cleanup_windows.ps1` |
| **📥 Baixar Python 3.11** | [python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe](https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe) |
| **❓ Perguntas Frequentes** | [FAQ.md](FAQ.md) |
| **🤝 Como Contribuir** | [CONTRIBUTING.md](CONTRIBUTING.md) |
| **🔒 Segurança** | [SECURITY.md](SECURITY.md) |
| **📺 Tutorial Completo** | [docs/WALKTHROUGH.md](docs/WALKTHROUGH.md) |

---

| Componente | Mínimo | Recomendado |
|-----------|--------|-------------|
| **Python** | 3.10 | 3.10+ |
| **RAM** | 4GB | 8GB+ |
| **GPU** | Não obrigatória | NVIDIA CUDA 11.8+ |
| **Espaço em Disco** | 1GB | 5GB+ |
| **Internet** | Sim (1ª vez) | Só para atualizações |

### Dependências Principais
- FastAPI + Uvicorn (Backend)
- PyQt6 (Interface Gráfica)
- EasyOCR (Reconhecimento de Texto)
- LAMA + Torch (Inpainting IA)
- OpenCV (Processamento de Imagens)

---

## 🎯 Funcionalidades

### ✨ Ultra IA
Limpeza automática inteligente com retoque neural avançado.

### 🖌️ Ferramentas de Edição
- **Pincel de Limpeza:** Remove rápido qualquer elemento
- **Seleção Inteligente:** Detecta balões automaticamente
- **OCR Local:** Extrai textos sem enviar para nuvem
- **Editor de Texto:** Reescreva diálogos com fontes personalizadas

### 📊 Processamento em Lote
- Processe múltiplas imagens em sequência
- Preview em tempo real
- Exportação em qualidade original

### 🎨 Personalização
- **Presets de Estilo:** Diferentes estilos de limpeza
- **Fontes Customizadas:** Biblioteca com 50+ fontes de mangá
- **Temas UI:** Modo claro/escuro
- **Configurações Avançadas:** Controle fino de processamento

---

## 📖 Documentação

- 📘 [WALKTHROUGH.md](docs/WALKTHROUGH.md) - Guia passo-a-passo
- 🏗️ [WEBTOON_ARCHITECTURE.md](docs/WEBTOON_ARCHITECTURE.md) - Arquitetura técnica
- 📋 [CHANGELOG.md](CHANGELOG.md) - Histórico de versões
- 📊 [Relatórios de Fase](docs/) - Documentação técnica completa

---

## 🔄 Atualizações

O projeto usa **Git incremental** para atualizações:

```bash
# Puxe as últimas alterações (rápido!)
git pull origin master

# Depois execute normalmente
python launcher.py
```

**Benefícios:**
- ✅ Download apenas do que foi alterado
- ✅ Sem reinstalação necessária
- ✅ Histórico completo do projeto
- ✅ Possibilidade de reverter versões

---

## 🛠️ Desenvolvimento

### Clonar e Configurar

```bash
git clone https://github.com/Noixfrio/WebtoonCleanerUltimate.git
cd WebtoonCleanerUltimate
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Estrutura do Projeto

```
WebtoonCleanerUltimate/
├── launcher/              # Interface gráfica (CustomTkinter)
├── web_app/              # Backend FastAPI
├── core/                 # Motor de processamento
│   ├── pipeline.py       # Pipeline de limpeza
│   ├── detector.py       # OCR com EasyOCR
│   ├── inpaint_engine.py # LAMA inpainting
│   └── font_manager.py   # Gerenciador de fontes
├── tools/                # Ferramentas utilitárias
├── tests/                # Testes automatizados
├── config/               # Configurações
├── assets/               # Recursos (modelos, ícones)
└── docs/                 # Documentação
```

### Rodando Testes

```bash
# Testes unitários
pytest tests/

# Teste específico
pytest tests/test_core_mvp.py -v
```

---

## 🐛 Troubleshooting

### Erro: "Failed to start OCR engine: 'charmap' codec can't encode"
**Solução:** Está corrigido na v0.9.9+. Atualize com:
```bash
git pull origin master
```

### Erro: "ModuleNotFoundError: No module named 'customtkinter'"
**Solução:**
```bash
pip install customtkinter pyqt6 qtpy
```

### A interface não aparece
**Teste:**
```bash
python launcher.py --skip-update
```

### Processamento muito lento
- Verifique RAM disponível (`top` ou Task Manager)
- Considere usar GPU (NVIDIA CUDA)
- Reduza tamanho das imagens

---

## 🤝 Contribuir

Adoramos contribuições! Aqui como:

1. **Fork** o repositório
2. **Crie uma branch** (`git checkout -b feature/MinhaFeature`)
3. **Faça commits** com mensagens claras
4. **Push para o GitHub** (`git push origin feature/MinhaFeature`)
5. **Abra um Pull Request** com descrição da mudança

### Diretrizes
- Siga o estilo de código PEP 8
- Adicione testes para novas funcionalidades
- Atualize documentação se necessário
- Mensagens de commit em português ou inglês claro

---

## 📝 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

---

## 💬 Suporte e Comunidade

- 🐛 [Reportar Bug](https://github.com/Noixfrio/WebtoonCleanerUltimate/issues/new?template=bug_report.md)
- 💡 [Sugerir Feature](https://github.com/Noixfrio/WebtoonCleanerUltimate/issues/new?template=feature_request.md)
- 💬 [Discussões](https://github.com/Noixfrio/WebtoonCleanerUltimate/discussions)
- 📧 Issues & Pull Requests sempre bem-vindos!

---

## 🙏 Créditos

- **EasyOCR** - Reconhecimento de texto
- **LAMA** - Inpainting neural
- **PyTorch/TorchVision** - Deep Learning
- **FastAPI** - Framework web
- **CustomTkinter** - Interface moderna

---

## 📊 Estatísticas

![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/Noixfrio/WebtoonCleanerUltimate?style=flat-square)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/Noixfrio/WebtoonCleanerUltimate?style=flat-square)
![Top Language](https://img.shields.io/github/languages/top/Noixfrio/WebtoonCleanerUltimate?style=flat-square&logo=python)

---

<div align="center">

**Feito com ❤️ para a comunidade de mangá e webtoons**

[⬆ voltar ao topo](#-webtoon-cleaner-ultimate)

</div>

## 📄 Licença
Distribuído sob a licença **MIT**. Veja o arquivo `LICENSE` para detalhes.

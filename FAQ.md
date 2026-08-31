# ❓ Perguntas Frequentes (FAQ)

## 🚀 Instalação & Setup

### P: Posso usar no macOS?
**R:** Sim! Suportamos Windows, Linux e macOS. Execute `./START_MAC.sh` após clonar.

### P: Preciso de GPU?
**R:** Não é obrigatório, mas acelera muito. Se tiver NVIDIA CUDA 11.8+, será usado automaticamente.

### P: Quanto de RAM preciso?
**R:** Mínimo 4GB, recomendado 8GB+. Com menos, pode ficar lento.

### P: Na primeira execução, por que demora tanto?
**R:** Está baixando os modelos de IA (~250MB). Conexão de internet rápida ajuda. Depois é rápido!

### P: Posso instalar em uma pendriver USB?
**R:** Tecnicamente sim, mas não recomendamos. O projeto é grande e o desempenho seria ruim.

---

## 🛠️ Problemas Comuns

### P: "ModuleNotFoundError: No module named 'customtkinter'"
**R:** Instale com:
```bash
pip install customtkinter pyqt6 qtpy
```

### P: "Failed to start OCR engine: 'charmap' codec..."
**R:** Erro no Windows. Atualize para v0.9.9+:
```bash
git pull origin master
```

### P: A interface não aparece / fica branca
**R:** Tente:
```bash
python launcher.py --skip-update
```

### P: "Connection refused" na porta 5000/5002
**R:** Outra aplicação está usando. Tente reiniciar ou mude a porta em `config/settings.py`.

### P: Processamento muito lento
**R:** 
1. Verifique RAM disponível
2. Reduza tamanho das imagens
3. Considere comprar GPU NVIDIA
4. Aumente timeout em `config/settings.py`

### P: Erro "CUDA out of memory"
**R:** Imagens muito grandes ou GPU com pouca VRAM. Tente:
```bash
# Desabilitar GPU
export ENABLE_GPU=false
python launcher.py
```

---

## 🎨 Uso & Features

### P: Posso processar múltiplas imagens?
**R:** Sim! Use o modo "Processamento em Lote" na interface.

### P: Quais formatos de imagem são suportados?
**R:** JPG, PNG, WEBP. Melhor qualidade com PNG.

### P: Posso editar texto depois da limpeza?
**R:** Sim! Use a "Ferramenta de Texto" para reescrever com fontes customizadas.

### P: Os textos originais são mantidos em OCR?
**R:** O OCR extrai o texto. Você pode usar para tradução ou referência.

### P: Posso desfazer uma edição?
**R:** Ainda não há undo/redo. Use "Descartar" e reprocesse.

### P: Qual qualidade de saída devo usar?
**R:** 85-95 é bom balanço. 100 mantém qualidade máxima.

---

## 🔧 Desenvolvimento

### P: Como contribuir com código?
**R:** Leia [CONTRIBUTING.md](CONTRIBUTING.md) para diretrizes detalhadas.

### P: Como rodar os testes?
**R:** 
```bash
pytest tests/ -v
```

### P: Posso adicionar um novo idioma?
**R:** Sim! Edite `locales/*.json` e abra um PR.

### P: Como treinar modelos customizados?
**R:** Documentação em desenvolvimento. Veja [docs/WEBTOON_ARCHITECTURE.md](docs/WEBTOON_ARCHITECTURE.md).

---

## 💾 Dados & Privacidade

### P: Meus dados são enviados para servidores?
**R:** **Não!** Tudo é processado localmente no seu computador.

### P: Há coleta de telemetria?
**R:** Não há coleta de dados invasiva. Apenas logs locais para debug.

### P: Posso usar comercialmente?
**R:** Sim! Licença MIT permite uso comercial. Veja [LICENSE](LICENSE).

### P: As imagens são armazenadas?
**R:** Apenas os arquivos que você escolhe salvar. Nada permanente além disso.

---

## 🤝 Comunidade

### P: Como reportar um bug?
**R:** Abra uma [Issue](https://github.com/Noixfrio/WebtoonCleanerUltimate/issues) com [este template](.github/ISSUE_TEMPLATE/bug_report.md).

### P: Como sugerir uma feature?
**R:** Crie uma [Discussion](https://github.com/Noixfrio/WebtoonCleanerUltimate/discussions) ou [Issue](https://github.com/Noixfrio/WebtoonCleanerUltimate/issues) com [este template](.github/ISSUE_TEMPLATE/feature_request.md).

### P: Há servidor Discord/comunidade?
**R:** Ainda não, mas estamos considerando. Acompanhe as Discussions!

### P: Posso fazer fork e criar minha própria versão?
**R:** Sim! Licença MIT permite. Leia [LICENSE](LICENSE) para detalhes.

---

## 📚 Aprendizado

### P: Qual IA é usada?
**R:** 
- **OCR:** EasyOCR
- **Inpainting:** LAMA
- **Detecção:** CRAFT + EasyOCR

Veja [WEBTOON_ARCHITECTURE.md](docs/WEBTOON_ARCHITECTURE.md).

### P: Como funciona o inpainting?
**R:** O modelo LAMA usa deep learning para "completar" áreas removidas naturalmente.

### P: Posso usar modelos de terceiros?
**R:** Parcialmente. Sistema de plugins está em desenvolvimento.

---

## 💰 Licença & Custos

### P: É grátis?
**R:** Sim! Totalmente grátis e open-source (MIT License).

### P: Há versão paga/premium?
**R:** Não. Projeto comunitário sem monetização.

### P: Posso usar para comercial?
**R:** Sim, MIT License permite. Apenas cite a origem.

---

## 🐛 Quando Tudo Mais Falha

### Passo 1: Limpe Cache
```bash
rm -rf ~/.cache/webtoon*
rm -rf __pycache__/
```

### Passo 2: Recriar Ambiente
```bash
python -m venv venv_new
source venv_new/bin/activate
pip install -r requirements.txt
```

### Passo 3: Atualizar Tudo
```bash
git pull origin master
pip install --upgrade -r requirements.txt
```

### Passo 4: Abrir Issue
Se nada funcionar, [abra uma issue](https://github.com/Noixfrio/WebtoonCleanerUltimate/issues/new) com:
- Seu SO e versão Python
- Mensagem de erro completa
- Passos que tentou
- Logs (se houver)

---

## 📞 Ainda Tem Dúvida?

- 📖 Leia [WALKTHROUGH.md](docs/WALKTHROUGH.md)
- 💬 Abra uma [Discussion](https://github.com/Noixfrio/WebtoonCleanerUltimate/discussions)
- 🐛 Crie uma [Issue](https://github.com/Noixfrio/WebtoonCleanerUltimate/issues)
- 📚 Consulte a [Documentação](docs/)

**Estamos aqui para ajudar! 🙏**

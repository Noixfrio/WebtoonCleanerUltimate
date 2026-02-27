# 🧹 Webtoon Cleaner Ultimate
![GitHub release (latest by date)](https://img.shields.io/github/v/release/Noixfrio/WebtoonCleanerUltimate?color=green&label=Vers%C3%A3o%20Mais%20Nova&style=for-the-badge)


O **Webtoon Cleaner Ultimate** é uma ferramenta de IA para limpeza de mangás e webtoons que roda direto no seu computador.

---

## 🎥 Demonstração em Vídeo
Assista ao vídeo demonstrativo para ver o Manga Cleaner v2 em ação:
[![Manga Cleaner v2 Demo](https://img.youtube.com/vi/390o1EWne-E/0.jpg)](https://youtu.be/390o1EWne-E)

---

## 📥 ESCOLHA SUA FORMA DE ACESSO

Existem três maneiras de usar o editor, escolha a que for melhor para você:

### 1. 🚀 Executável Portátil (Maneira Mais Fácil)
Não precisa instalar nada! Ideal para quem quer apenas usar o programa.
*   **Baixar:** Acesse a página de [RELEASES](https://github.com/Noixfrio/WebtoonCleanerUltimate/releases/latest) e baixe o arquivo `.zip` da versão mais nova.
*   **Downloads Diretos (Hugging Face):** [Windows (v0.9.9-beta.18-win)](https://huggingface.co/samyuush/WebtoonCleanerUltimate/resolve/main/binaries/Toonix-v0.9.9-beta.18-win-windows.zip) | [Linux (v0.9.9-beta.12)](https://huggingface.co/samyuush/WebtoonCleanerUltimate/resolve/main/binaries/Toonix-v0.9.9-beta.12-linux.zip)
*   **Como usar:** Extraia o arquivo e abra o executável `ToonixLauncher` (Windows) ou `ToonixLauncher` (Linux).
*   **Nota:** Na primeira execução, o programa baixará automaticamente os modelos de IA necessários (~250MB).

### 2. 🐧 Linux / MacOS (Scripts Rápidos)
Se você está no Linux, temos scripts que automatizam o setup:
1.  Execute `./INSTALAR_BIBLIOTECAS.sh` (faz o setup do ambiente Python).
2.  Para usar, execute `./INICIAR_PROGRAMA.sh`.
3.  O sistema agora utiliza **Lazy Loading**, baixando os motores de IA apenas quando necessário.

### 3. 🛠️ Instalação Tradicional (Para Desenvolvedores)
Se você quer rodar o código fonte puro e fazer modificações:

---

## 🚀 Como Funciona (Inteligência Dinâmica)
Este projeto foi refatorado para ser leve e eficiente.
*   **Executável Ultraleve:** O download inicial tem apenas ~200MB.
*   **Modelos On-Demand:** Os modelos pesados de OCR e Inpainting são baixados automaticamente na primeira vez que você inicia o app.
*   **Hospedagem Híbrida:** Binários hospedados no Hugging Face para garantir velocidade e estabilidade.

---

## 💻 Instalação

### Windows (Recomendado)
1. Baixe a **[LATEST RELEASE](https://github.com/Noixfrio/WebtoonCleanerUltimate/releases/latest)** no GitHub.
2. Extraia e execute o `ToonixLauncher.exe`.
3. Aguarde o download automático dos modelos na tela inicial.

### Linux / MacOS
1. Recomendado **Python 3.10** para estabilidade.
2. No terminal:
   ```bash
   git clone https://github.com/Noixfrio/WebtoonCleanerUltimate.git
   cd WebtoonCleanerUltimate
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python3 launcher/main.py
   ```
3. Abra `localhost:5000` no seu navegador.

---

## 🛠️ Ferramentas Avançadas (Experimental)
Se você quer resultados superiores com IA:
*   **Ultra Clean Tool:** Execute `python3 scripts/ultra_cleaner.py` para usar o inpainter avançado (LaMa + ROI).

---

## 🎨 Principais Ferramentas
*   **✨ Ultra IA (Individual):** Agora cada imagem possui seu próprio botão flutuante para abertura instantânea no laboratório avançado (Porta 5001).
*   **↩️ Reverter IA (Undo):** Proteção contra erros! Se não gostar do resultado da Ultra IA, você pode desfazer a alteração e recuperar a imagem anterior com um clique.
*   **🖌️ Pincel de Limpeza:** IA local para remoção rápida de balões e textos simples.
*   **🪄 Restauração:** Pincel que recupera o desenho original apagado.
*   **🔤 Ferramenta de Texto:** Edição de diálogos com pré-visualização em tempo real.
*   **🔍 Copiar (OCR):** Extração de texto japonês/coreano/chinês direto da imagem.
*   **📱 Modo Leitor (Webtoon):** Visualização vertical infinita sem quebras ou espaços entre as páginas, otimizada para leitura e edição fluida.
*   **⌨️ Atalhos Rápidos:** Use `ESC` para sair da Ultra IA e ferramentas de atalhos integradas para alternância de modos.

---

## 🔄 Atualizações
Sempre que o desenvolvedor lançar uma melhoria, basta rodar o script `update_project.bat` (Windows) ou `update_project.sh` (Linux) para baixar a versão mais nova sem perder suas configurações.

---

## 🐛 Reporte de Bugs e Sugestões
Encontrou algum problema ou tem uma ideia para melhorar a IA? Sua ajuda é fundamental!
*   **Issues do GitHub:** Abra uma [Issue](https://github.com/Noixfrio/WebtoonCleanerUltimate/issues) com o print do erro.
*   **Melhoria da IA:** Se a limpeza falhou em alguma imagem, envie a imagem original para análise.

---

## 📄 Licença
Distribuído sob a licença **MIT**. Veja o arquivo `LICENSE` para detalhes.

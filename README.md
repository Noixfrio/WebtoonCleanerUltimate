# 🧹 Webtoon Cleaner Ultimate

O **Webtoon Cleaner Ultimate** é uma ferramenta de IA para limpeza de mangás e webtoons que roda direto no seu computador.

---

## 📥 COMO BAIXAR (PASSO A PASSO)
Se você não sabe usar o GitHub, siga estas instruções simples:

1.  **Clique no Botão Verde:** No topo desta página, clique no botão que diz **"<> Code"** (cor verde).
2.  **Baixe o ZIP:** No menu que abrir, clique na última opção: **"Download ZIP"**.
3.  **Extraia os Arquivos:** Após baixar, abra o arquivo `.zip` e arraste a pasta para sua Área de Trabalho.
4.  **Siga a Instalação:** Agora é só seguir os passos da seção **Windows** ou **Linux** abaixo!

---

## 🚀 Como Funciona (Transparência)
Este projeto foi construído com foco total na segurança. Ele roda **localmente**.
*   **Privacidade:** Suas imagens nunca saem do seu PC. O processamento acontece no seu próprio hardware.

---

## 💻 Instalação

### Windows (Recomendado)
1. Baixe este projeto e extraia a pasta.
2. Clique duas vezes no arquivo `1_BAIXAR_PYTHON_3.10.bat` (O Python será instalado automaticamente, marque a opção "Add Python to PATH" na tela).
3. Depois, clique em `2_INSTALAR_BIBLIOTECAS.bat`. Ele vai baixar as inteligências artificiais necessárias automaticamente.
4. Para abrir o programa, clique em `3_INICIAR_PROGRAMA.bat`.

### Linux / MacOS
1. Instale **EXATAMENTE o Python 3.10** (versões 3.12 ou mais novas não são compatíveis com o PaddleOCR no momento).
2. No terminal:
   ```bash
   git clone [url-do-repositorio]
   cd manga_cleaner_v2
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python3 -m uvicorn web_app.main:app --host 0.0.0.0 --port 5000
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

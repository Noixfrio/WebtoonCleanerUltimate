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
1. Certifique-se de ter o [Python 3.10+](https://www.python.org/downloads/) instalado.
2. Baixe este projeto e extraia a pasta.
3. Clique duas vezes no arquivo `install_windows.bat`. Ele vai baixar as bibliotecas necessárias automaticamente.
4. Para abrir o programa, use o atalho criado na Área de Trabalho ou execute `iniciar_servidor.bat`.

### Linux / MacOS
1. Instale o Python 3.10+.
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

## 🎨 Principais Ferramentas
*   **🖌️ Pincel de Limpeza:** IA que remove textos e reconstrói o desenho por baixo.
*   **🪄 Restauração:** Recupera partes apagadas acidentalmente.
*   **🔤 Ferramenta de Texto:** Adicione diálogos com suporte a fontes customizadas.
*   **🔍 Copiar (OCR):** Selecione uma área para extrair o texto original da imagem instantaneamente.
*   **📱 Modo Leitor:** Visualize o webtoon em scroll vertical infinito enquanto edita em tempo real.

---

## 🔄 Atualizações
Sempre que o desenvolvedor lançar uma melhoria, basta rodar o script `update_project.bat` (Windows) ou `update_project.sh` (Linux) para baixar a versão mais nova sem perder suas configurações.

---

## 📄 Licença
Distribuído sob a licença **MIT**. Veja o arquivo `LICENSE` para detalhes.

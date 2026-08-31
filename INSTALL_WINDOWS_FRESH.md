# 📥 Guia de Instalação - Webtoon Cleaner Ultimate

**Neste guia, vamos instalar o Webtoon Cleaner Ultimate no seu Windows, do zero.**

> ⏱️ Tempo estimado: 15-20 minutos (incluindo download dos modelos)

---

## 🎯 PASSO 1: Instale o Python 3.11

O Python é a linguagem que o programa usa.

### 1.1 Baixe o Python

**Clique no link abaixo para baixar Python 3.11:**

👉 **[CLIQUE AQUI PARA BAIXAR PYTHON 3.11](https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe)**

O arquivo `python-3.11.9-amd64.exe` vai ser baixado em cerca de 1-2 minutos.

### 1.2 Execute o Instalador

1. Abra o arquivo `python-3.11.9-amd64.exe` que foi baixado
2. **⚠️ IMPORTANTE:** Na primeira tela, marque a caixa ✅ **"Add Python 3.11 to PATH"**
3. Clique em **"Install Now"**
4. Aguarde a instalação completar (2-3 minutos)

> Se você ver "Setup was successful", significa que Python foi instalado corretamente!

### 1.3 Verifique a Instalação

Abra o **PowerShell** (ou Prompt de Comando):

1. Aperte `Windows + R`
2. Digite `powershell`
3. Aperte Enter

Agora digite este comando:

```powershell
python --version
```

**Você deve ver:** `Python 3.11.9` ou parecido.

Se vir "comando não encontrado", tente reiniciar o computador e repetir.

---

## 🎯 PASSO 2: Baixe o Projeto

### 2.1 (Opcional) Instale o Git

Se você não tem Git no seu computador, pode baixar:

👉 **[Clique aqui para baixar Git](https://git-scm.com/download/win)**

Execute o instalador com as opções padrão.

### 2.2a MÉTODO A: Com Git (Recomendado)

Se você tem Git instalado, abra o **PowerShell** e execute:

```powershell
# Escolha onde guardar (aqui usamos Desktop como exemplo)
cd Desktop

# Baixe o projeto
git clone https://github.com/Noixfrio/WebtoonCleanerUltimate.git

# Entre na pasta
cd WebtoonCleanerUltimate

Write-Host "✅ Projeto baixado com sucesso!" -ForegroundColor Green
```

### 2.2b MÉTODO B: Sem Git (Se não instalou)

1. Visite: **https://github.com/Noixfrio/WebtoonCleanerUltimate**
2. Clique no botão verde **"Code"**
3. Selecione **"Download ZIP"**
4. Espere baixar (~15-20MB)
5. Extraia a pasta em um local de fácil acesso (ex: Desktop)
6. Abra PowerShell e navegue:

```powershell
cd Desktop\WebtoonCleanerUltimate
```

---

## 🎯 PASSO 3: Configure o Ambiente Python

Agora vamos preparar o Python para o projeto.

### 3.1 Crie um Ambiente Virtual

Abra **PowerShell** na pasta do projeto:

```powershell
# Certifique-se que está na pasta WebtoonCleanerUltimate
# Veja se o caminho mostra algo como: ...WebtoonCleanerUltimate>

# Crie o ambiente virtual
python -m venv venv

# Ative o ambiente
venv\Scripts\activate

# Sucesso! Você verá (venv) no início da linha:
# (venv) PS C:\Users\...\WebtoonCleanerUltimate>
```

### 3.2 Atualize o pip

```powershell
# Com (venv) ativado:
python -m pip install --upgrade pip

# Deve mostrar: Successfully installed pip-X.X.X
```

---

## 🎯 PASSO 4: Instale as Dependências

```powershell
# Certifique-se que (venv) está ativado na linha
# Se não estiver, execute: venv\Scripts\activate

# Instale tudo
pip install -r requirements.txt

# ⏱️ Isso leva 5-10 minutos na primeira vez
# Você verá muitas linhas de progresso - é NORMAL!
```

**Se tiver erro:**
- Verifique sua conexão com internet
- Tente novamente: `pip install -r requirements.txt`
- Se persistir, tente: `pip install --upgrade setuptools wheel`

---

## 🎯 PASSO 5: Execute o Programa

### Primeira Execução (vai baixar modelos de IA)

```powershell
# Com (venv) ativado:
python launcher.py --skip-update

# ⏱️ Primeira vez leva 3-5 minutos (baixando modelos ~250MB)
# Você verá linhas de progresso
# Ao final, a interface gráfica vai abrir automaticamente
```

**Se a interface não abrir:**
- Verifique se não há mensagens de erro
- Tente fechar e executar novamente

### Próximas Execuções (muito rápidas!)

```powershell
# Basta executar:
python launcher.py
```

---

## ✅ Você Conseguiu! 🎉

Se chegou aqui, parabéns! O programa está funcionando.

**Próximos passos:**
1. Explore as ferramentas na interface
2. Leia o tutorial completo em: [docs/WALKTHROUGH.md](docs/WALKTHROUGH.md)
3. Tem dúvidas? Consulte [FAQ.md](FAQ.md) com 30+ perguntas respondidas

---

## 🚀 Atalho para Futuras Vezes

Próxima vez que quiser usar, basta:

```powershell
# Navegue até a pasta
cd Desktop\WebtoonCleanerUltimate

# Ative o ambiente
venv\Scripts\activate

# Execute
python launcher.py
```

**Dica:** Você pode criar um atalho no Desktop para acelerar!

---

## 🐛 Problemas na Instalação?

### Erro: "python: comando não encontrado"
- Python não está no PATH
- Reinstale Python e marque "Add to PATH"
- Reinicie o computador

### Erro: "pip: comando não encontrado"
```powershell
python -m pip install -r requirements.txt
```

### Erro: "venv: não reconhecido"
```powershell
python -m venv venv
```

### Erro: "Porta 5000 em uso"
```powershell
taskkill /F /IM python.exe
```
Depois execute novamente.

### Interface não aparece
```powershell
# Tente com skip-update
python launcher.py --skip-update
```

### Internet lenta (modelos não baixam)
- Tente em outro horário com melhor conexão
- Certifique-se que não há limites de banda

---

## 📞 Precisa de Ajuda?

- **FAQ Completo:** [FAQ.md](FAQ.md)
- **Issues no GitHub:** [Reportar Bug](https://github.com/Noixfrio/WebtoonCleanerUltimate/issues)
- **Discussões:** [Conversar com outros usuários](https://github.com/Noixfrio/WebtoonCleanerUltimate/discussions)

---

## 📋 Checklist Final

- [ ] Python 3.10+ instalado e no PATH ✅
- [ ] Projeto baixado em uma pasta ✅
- [ ] Ambiente virtual (venv) criado ✅
- [ ] pip atualizado ✅
- [ ] requirements.txt instalado ✅
- [ ] launcher.py executado ✅
- [ ] Interface gráfica abriu ✅
- [ ] Modelos de IA baixados ✅

---

## 🎨 Bem-vindo!

Agora você está pronto para:
- 🧹 Limpar seus mangás e webtoons
- 🔤 Editar textos com OCR
- 🎨 Fazer retoques inteligentes com IA
- 💾 Salvar em alta qualidade

**Divirta-se! 🚀**

---

<div align="center">

**Feito com ❤️ para a comunidade de mangá e webtoons**

[⬆ voltar ao topo](#-guia-de-instalação---webtoon-cleaner-ultimate)

</div>

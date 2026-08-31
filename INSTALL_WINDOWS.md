# 📥 Guia Completo de Instalação - Windows

**Neste guia, vamos instalar o Webtoon Cleaner Ultimate do zero, passo a passo.**

> ⏱️ Tempo estimado: 15-20 minutos (incluindo download dos modelos)

---

## ⚠️ ANTES DE COMEÇAR: Limpar Instalações Anteriores

Se você já teve o projeto instalado e quer começar do zero, execute este script:

### Opção 1: Automático (Recomendado)

1. **Abra o PowerShell como administrador:**
   - Aperte `Windows + X`
   - Selecione **Windows PowerShell (Admin)** ou **Terminal (Admin)**

2. **Cole e execute:**
```powershell
# Execute o script de limpeza (baixe de: https://github.com/Noixfrio/WebtoonCleanerUltimate/blob/master/cleanup_windows.ps1)
iex (New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/Noixfrio/WebtoonCleanerUltimate/master/cleanup_windows.ps1')
```

### Opção 2: Manual

Se preferir limpar manualmente:

```powershell
# Abra PowerShell e execute:

# 1. Remova a pasta do projeto
Remove-Item -Path "C:\WebtoonCleanerUltimate" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$env:USERPROFILE\Downloads\WebtoonCleanerUltimate*" -Recurse -Force -ErrorAction SilentlyContinue

# 2. Limpe cache do Python
Remove-Item -Path "$env:USERPROFILE\AppData\Local\pip" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$env:USERPROFILE\.cache\pip" -Recurse -Force -ErrorAction SilentlyContinue

# 3. Limpe modelos baixados
Remove-Item -Path "$env:USERPROFILE\AppData\Roaming\webtoon*" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$env:USERPROFILE\.webtoon*" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "✅ Limpeza concluída!" -ForegroundColor Green
```

---

## 🎯 INSTALAÇÃO PASSO A PASSO

### PASSO 1: Instale o Python 3.10+

O Python é a linguagem que o programa usa. Vamos baixar e instalar.

#### 1.1 Baixe o Python

Vá para: **https://www.python.org/downloads/windows/**

**Ou clique direto no link para Python 3.11** (recomendado):
- 👉 https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe

#### 1.2 Execute o Instalador

1. Abra o arquivo `python-3.11.9-amd64.exe` que foi baixado
2. **IMPORTANTE:** Marque a caixa ✅ **"Add Python 3.11 to PATH"**
3. Clique em **"Install Now"**
4. Aguarde a instalação completar (1-2 minutos)

#### 1.3 Verifique a Instalação

Abra o **PowerShell** (ou Prompt de Comando) e teste:

```powershell
python --version
```

Deve mostrar algo como: `Python 3.11.9`

Se não funcionar:
- Reinicie o computador e tente novamente
- Ou adicione Python manualmente ao PATH

---

### PASSO 2: Baixe o Projeto

#### 2.1 Instale o Git (Opcional, mas Recomendado)

Se você não tem Git instalado:
- Baixe de: https://git-scm.com/download/win
- Execute e instale com as opções padrão

#### 2.2a OPÇÃO A: Usando Git (Recomendado)

Abra o **PowerShell** e execute:

```powershell
# Navegue até onde quer guardar o projeto
# Exemplo: Área de Trabalho
cd Desktop

# Clone o projeto
git clone https://github.com/Noixfrio/WebtoonCleanerUltimate.git

# Entre na pasta
cd WebtoonCleanerUltimate

Write-Host "✅ Projeto baixado com sucesso!" -ForegroundColor Green
```

#### 2.2b OPÇÃO B: Sem Git (Se não instalou)

1. Visite: https://github.com/Noixfrio/WebtoonCleanerUltimate
2. Clique no botão **"Code" (verde)**
3. Selecione **"Download ZIP"**
4. Extraia a pasta em um local de fácil acesso (ex: Desktop ou C:\)
5. Abra PowerShell e navegue até a pasta:

```powershell
cd "C:\WebtoonCleanerUltimate"
```

---

### PASSO 3: Configure o Ambiente

#### 3.1 Crie um Ambiente Virtual

O ambiente virtual isola as dependências do projeto.

```powershell
# Veja se está na pasta certa (WebtoonCleanerUltimate)
# Se não estiver, use: cd C:\caminho\para\WebtoonCleanerUltimate

# Crie o ambiente virtual
python -m venv venv

# Ative o ambiente
venv\Scripts\activate

# Você verá (venv) no início da linha:
# (venv) PS C:\WebtoonCleanerUltimate>
```

#### 3.2 Atualize o pip

```powershell
# Com o ambiente ativado (venv):
python -m pip install --upgrade pip

# Deve mostrar: Successfully installed pip-X.X.X
```

---

### PASSO 4: Instale as Dependências

```powershell
# Certifique-se que o ambiente está ativado (venv)
# Você verá (venv) no início da linha

# Instale as dependências
pip install -r requirements.txt

# ⏱️ Isso pode levar 5-10 minutos na primeira vez
# Você verá muitas linhas de progresso - é normal!
```

**Se tiver erro:**
- Certifique-se que Python 3.10+ está instalado
- Se tiver erro de conexão, verifique sua internet
- Tente novamente: `pip install -r requirements.txt`

---

### PASSO 5: Execute o Programa

#### 5.1 Primeira Execução (com download dos modelos)

```powershell
# Com o ambiente ativado (venv):
python launcher.py --skip-update

# ⏱️ Primeira vez leva 3-5 minutos (baixando modelos de IA ~250MB)
# É normal ver linhas de progresso
# Ao fim, a interface gráfica deve abrir
```

#### 5.2 Próximas Execuções (bem rápidas)

```powershell
# Simplesmente execute:
python launcher.py
```

---

## ✅ Checklist de Instalação

- [ ] Python 3.10+ instalado e no PATH
- [ ] Projeto baixado em uma pasta local
- [ ] Git instalado (opcional, mas recomendado)
- [ ] Ambiente virtual (venv) criado
- [ ] pip atualizado
- [ ] requirements.txt instalado com sucesso
- [ ] launcher.py executado sem erros
- [ ] Modelos de IA baixados (~250MB)
- [ ] Interface gráfica abriu

---

## 🚀 Atalho Rápido para Futuras Execuções

Para próximas vezes, basta abrir PowerShell e executar:

```powershell
# Se a pasta não tiver símbolo 'C:\' em branco antes, navegue até ela:
cd C:\caminho\para\WebtoonCleanerUltimate

# Ative o ambiente
venv\Scripts\activate

# Execute
python launcher.py
```

---

## 🐛 Troubleshooting

### ❌ "Python não é reconhecido"

**Solução:** Python não está no PATH. Reinstale Python e marque "Add Python to PATH".

### ❌ "pip: comando não encontrado"

**Solução:** 
```powershell
# Use:
python -m pip install -r requirements.txt
```

### ❌ "Erro de permissão ao instalar"

**Solução:** Abra PowerShell como Administrador:
- Aperte `Windows + X`
- Selecione `Windows PowerShell (Admin)`

### ❌ "Porta 5000/5002 em uso"

**Solução:** Outro programa está usando. Tente:
```powershell
# Encerre processos Python
taskkill /F /IM python.exe
```

### ❌ "Erro de charmap ou encoding"

**Solução:** Atualize para v0.9.9+:
```powershell
git pull origin master
```

### ❌ "Modelos não baixam"

**Solução:** Verifique internet e tente:
```powershell
python launcher.py --skip-update
```

---

## 🆘 Precisando de Ajuda?

1. **FAQ:** https://github.com/Noixfrio/WebtoonCleanerUltimate/blob/master/FAQ.md
2. **Issues:** https://github.com/Noixfrio/WebtoonCleanerUltimate/issues
3. **Discussions:** https://github.com/Noixfrio/WebtoonCleanerUltimate/discussions

---

## 📋 Links Úteis

| Recurso | Link |
|---------|------|
| **Python 3.11** | https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe |
| **Git para Windows** | https://git-scm.com/download/win |
| **Projeto GitHub** | https://github.com/Noixfrio/WebtoonCleanerUltimate |
| **Issues & Bugs** | https://github.com/Noixfrio/WebtoonCleanerUltimate/issues |
| **FAQ Completo** | https://github.com/Noixfrio/WebtoonCleanerUltimate/blob/master/FAQ.md |
| **Documentação** | https://github.com/Noixfrio/WebtoonCleanerUltimate/tree/master/docs |

---

## 🎉 Sucesso!

Se você chegou até aqui, parabéns! O programa deve estar funcionando. 

**Próximos passos:**
- Explore as ferramentas
- Leia o [WALKTHROUGH.md](docs/WALKTHROUGH.md) para tutorial completo
- Reporte bugs ou sugira features nas [Issues](https://github.com/Noixfrio/WebtoonCleanerUltimate/issues)

**Divirta-se limpando seus mangás! 🎨**

---

<div align="center">

**Feito com ❤️ para a comunidade de mangá e webtoons**

[⬆ voltar ao topo](#-guia-completo-de-instalação---windows)

</div>

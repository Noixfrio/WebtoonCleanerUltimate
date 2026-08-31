# Sistema de Atualização Automática

O Toonix Editor possui um sistema de atualização automática que baixa código novo do GitHub sem precisar rebuildar com PyInstaller.

## Como Funciona

### Arquitetura

O sistema separa o código em duas camadas:

1. **Launcher estável** (PyInstaller, muda raramente)
   - Executável compilado (`ToonixLauncher.exe`)
   - Só precisa rebuild quando mudar dependências nativas ou o próprio launcher

2. **Código vivo** (atualiza sem rebuild)
   - `web_app/` - Frontend HTML/CSS/JS/templates
   - `core/` - Lógica Python da aplicação
   - `launcher/` - UI e backend do launcher
   - `config/`, `locales/`, `tools/`, etc.

### Fluxo de Atualização

```
Abrir App → Verificar GitHub → Há commit novo? → Sim → Baixar/Aplicar → Abrir com código novo
                                                → Não → Abrir normalmente
```

**Importante:** Se a rede falhar, o app abre com a versão que já está no disco (não trava).

## Uso no Desenvolvimento

### Testar Mudança de Layout/Código

1. Fazer mudança em `web_app/`, `core/`, etc.
2. Commitar e dar push:
   ```bash
   git add .
   git commit -m "fix: corrigir layout do botão"
   git push origin master
   ```
3. **Fechar o app**
4. **Abrir de novo** (sem rebuild!)
5. O launcher vai:
   - Detectar o commit novo
   - Fazer `git pull` (desenvolvimento) ou baixar ZIP
   - Abrir o app já com o código atualizado

### Ver Qual Commit Está Rodando

- **Título da janela:** `Toonix Editor v0.9.9 (a1b2c3d)` ← commit curto
- **Rodapé do launcher:** `v0.9.9 • a1b2c3d`

### Pular Atualização (Offline)

**Método 1: Variável de ambiente**
```bash
set TOONIX_SKIP_UPDATE=1
ToonixLauncher.exe
```

**Método 2: Flag de linha de comando**
```bash
python launcher/main.py --skip-update
```

## Métodos de Atualização

### Desenvolvimento (Git Clone)

Se a pasta tiver `.git/`, o sistema usa `git pull`:

```bash
git pull origin master
```

- **Vantagens:** Rápido, preserva histórico
- **Requisito:** Ter Git instalado e internet

### Instalação Release (Sem .git)

Se não houver `.git/`, baixa ZIP do GitHub:

```
https://github.com/Noixfrio/WebtoonCleanerUltimate/archive/refs/heads/master.zip
```

- **Vantagens:** Funciona sem Git
- **Desvantagem:** Download maior (~50MB)

## Detecção de Repositório

O sistema detecta automaticamente:

1. **Owner/Repo:** Do `git remote -v` (origin)
2. **Branch:** Do `git branch --show-current`
3. **Fallback:** `Noixfrio/WebtoonCleanerUltimate` branch `master`

## Verificação de Commits

Compara commits via GitHub API:

```
GET https://api.github.com/repos/{owner}/{repo}/commits/{branch}
```

Retorna:
- SHA do commit
- Mensagem do commit
- Autor e data

Se o SHA remoto for diferente do local → atualização disponível.

## Onde os Arquivos São Salvos

### Cache de Download (ZIP)

Preferência:
1. `{app_dir}/temp/` (se C: estiver cheio)
2. `%TEMP%` do sistema

### Commit Atual

Salvo em: `{app_dir}/runtime/current_commit.txt`

### Pastas Preservadas (NÃO são atualizadas)

- `models/` - Modelos de IA baixados
- `processed/` - Imagens processadas
- `config/config.json` - Configurações do usuário
- Cache do Hugging Face (configurável)

## Segurança e Rollback

### Validação

1. Download completo antes de aplicar
2. ZIP válido (não HTML de erro)
3. Pastas esperadas presentes no ZIP

### Falha de Atualização

Se falhar:
- **NÃO corrompe** a instalação
- App abre com versão anterior
- Erro aparece no log

### Git com Mudanças Locais

Se houver mudanças não commitadas:
```bash
git stash     # Guarda mudanças locais
git pull      # Atualiza
```

## Quando Rebuildar PyInstaller

Rebuild só é necessário quando:

1. Adicionar **dependência Python nova** (no `requirements.txt`)
2. Mudar o **próprio launcher** (`launcher/main.py`, `launcher/bootstrap.py`)
3. Adicionar **arquivo nativo** (.dll, .so, binários)
4. Mudar o **executável** (ícone, manifest, assinatura)

**Mudanças que NÃO precisam rebuild:**
- ✅ HTML/CSS/JS
- ✅ Python em `web_app/`, `core/`
- ✅ Textos de UI, traduções
- ✅ Bugfix de lógica
- ✅ Novos assets (imagens, fontes)

## Estrutura de Arquivos

```
ToonixEditor/
├── ToonixLauncher.exe          # Launcher estável (PyInstaller)
├── runtime/
│   └── current_commit.txt      # SHA do commit atual
├── web_app/                    # ← Atualiza automaticamente
├── core/                       # ← Atualiza automaticamente
├── launcher/                   # ← Atualiza automaticamente
├── config/
│   └── config.json             # Preservado (configurações do usuário)
├── models/                     # Preservado (modelos de IA)
└── processed/                  # Preservado (saída do usuário)
```

## Troubleshooting

### "Falha ao verificar atualização"

**Causa:** Sem internet ou GitHub fora do ar
**Solução:** App abre normalmente com versão local

### "git pull falhou"

**Causa:** Conflito de merge ou Git não instalado
**Solução:** Sistema tenta baixar ZIP automaticamente

### "Commit não aparece na UI"

**Causa:** `runtime/current_commit.txt` ausente
**Solução:** Na próxima atualização será criado

### Download está indo para C: (cheio)

**Causa:** `%TEMP%` aponta para C:
**Solução:** Sistema detecta e usa `{app_dir}/temp/` automaticamente

## Exemplo de Workflow Completo

### Cenário: Corrigir cor de botão

```bash
# 1. Editar o CSS
nano web_app/static/style.css

# 2. Commitar
git add web_app/static/style.css
git commit -m "fix: corrigir cor do botão de salvar"

# 3. Push
git push origin master

# 4. No computador de teste/produção:
# - Fechar o Toonix Editor
# - Abrir de novo
# - Launcher mostra: "✓ Atualizado para commit a1b2c3d"
# - App abre com o botão na cor correta!
```

**Tempo total:** ~5 segundos (vs ~2 minutos de rebuild)

## Configuração Avançada

### Usar Outro Repositório

Editar `core/auto_updater.py`:
```python
DEFAULT_REPO = "SeuUsuario/SeuRepo"
DEFAULT_BRANCH = "main"  # ou "develop", etc.
```

### Debug de Atualização

Ver logs em tempo real:
```bash
python launcher/main.py
# Logs aparecem no console
```

Pular update e rodar manualmente:
```python
from core.auto_updater import AutoUpdater
from pathlib import Path

updater = AutoUpdater(Path("."))
update_info = updater.check_for_updates()
if update_info:
    updater.apply_update(update_info)
```

## Limitações Conhecidas

1. **Não atualiza o .exe em si** - launcher precisa rebuild manual
2. **Requer Git ou internet** - não funciona 100% offline
3. **GitHub API rate limit** - 60 requisições/hora sem autenticação (suficiente para uso normal)

## Performance

- **Verificação:** ~1-2 segundos (se rede OK)
- **Download ZIP:** ~5-15 segundos (~50MB)
- **Git pull:** ~2-5 segundos (apenas diff)
- **Aplicação:** ~1 segundo (copiar arquivos)

**Total:** 3-20 segundos vs 2-5 minutos de rebuild PyInstaller.

---

**Última atualização:** 2026-08-31

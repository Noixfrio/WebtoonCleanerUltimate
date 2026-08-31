# Script de Limpeza Completa - Webtoon Cleaner Ultimate
# Execute como Administrador para melhor resultado

Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🧹 Limpeza Completa - Webtoon Cleaner Ultimate        ║" -ForegroundColor Cyan
Write-Host "║  Removerá todas as instalações anteriores              ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

Write-Host ""
Write-Host "⚠️  Este script vai APAGAR:" -ForegroundColor Yellow
Write-Host "   - Pastas do projeto"
Write-Host "   - Ambientes virtuais (venv)"
Write-Host "   - Cache do pip"
Write-Host "   - Modelos de IA baixados"
Write-Host "   - Configurações salvas"
Write-Host ""

$confirm = Read-Host "Deseja continuar? (S/N)"
if ($confirm -ne "S" -and $confirm -ne "s") {
    Write-Host "❌ Cancelado" -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "🔄 Iniciando limpeza..." -ForegroundColor Cyan
Write-Host ""

# Parar processos Python em execução
Write-Host "⏹️  Encerrando processos Python..." -ForegroundColor Yellow
taskkill /F /IM python.exe 2>$null | Out-Null
Start-Sleep -Milliseconds 500

# 1. Limpar pasta do projeto em locais comuns
$locations = @(
    "C:\WebtoonCleanerUltimate",
    "C:\Users\$env:USERNAME\Desktop\WebtoonCleanerUltimate",
    "C:\Users\$env:USERNAME\Downloads\WebtoonCleanerUltimate*",
    "$env:USERPROFILE\WebtoonCleanerUltimate"
)

Write-Host "📁 Removendo pastas do projeto..." -ForegroundColor Yellow
foreach ($location in $locations) {
    if (Test-Path $location) {
        try {
            Remove-Item -Path $location -Recurse -Force -ErrorAction Stop
            Write-Host "   ✅ Removido: $location"
        } catch {
            Write-Host "   ⚠️  Não foi possível remover: $location (pode estar em uso)"
        }
    }
}

# 2. Limpar ambientes virtuais
Write-Host ""
Write-Host "🐍 Removendo ambientes virtuais (venv)..." -ForegroundColor Yellow
$venvLocations = @(
    "C:\Users\$env:USERNAME\venv*",
    "$env:USERPROFILE\AppData\Local\Programs\Python\*\venv*",
    ".\venv",
    ".\venv-build*"
)

foreach ($venv in $venvLocations) {
    Get-Item $venv -ErrorAction SilentlyContinue | ForEach-Object {
        try {
            Remove-Item $_.FullName -Recurse -Force -ErrorAction Stop
            Write-Host "   ✅ Removido: $($_.FullName)"
        } catch {
            Write-Host "   ⚠️  Erro ao remover: $($_.FullName)"
        }
    }
}

# 3. Limpar cache do pip
Write-Host ""
Write-Host "📦 Limpando cache do pip..." -ForegroundColor Yellow
$pipCacheLocations = @(
    "$env:USERPROFILE\AppData\Local\pip\Cache",
    "$env:USERPROFILE\.cache\pip"
)

foreach ($cache in $pipCacheLocations) {
    if (Test-Path $cache) {
        try {
            Remove-Item -Path $cache -Recurse -Force -ErrorAction Stop
            Write-Host "   ✅ Removido: $cache"
        } catch {
            Write-Host "   ⚠️  Erro ao remover: $cache"
        }
    }
}

# 4. Limpar modelos de IA baixados
Write-Host ""
Write-Host "🤖 Removendo modelos de IA..." -ForegroundColor Yellow
$modelLocations = @(
    "$env:USERPROFILE\.cache\huggingface",
    "$env:USERPROFILE\AppData\Local\huggingface",
    "$env:USERPROFILE\.easyocr",
    "$env:USERPROFILE\AppData\Local\easyocr",
    "$env:USERPROFILE\webtoon*",
    "$env:USERPROFILE\.*webtoon*"
)

foreach ($model in $modelLocations) {
    Get-Item $model -ErrorAction SilentlyContinue | ForEach-Object {
        try {
            Remove-Item $_.FullName -Recurse -Force -ErrorAction Stop
            Write-Host "   ✅ Removido: $($_.FullName)"
        } catch {
            Write-Host "   ⚠️  Erro ao remover: $($_.FullName)"
        }
    }
}

# 5. Limpar configurações salvas
Write-Host ""
Write-Host "⚙️  Removendo configurações salvas..." -ForegroundColor Yellow
$configLocations = @(
    "$env:USERPROFILE\AppData\Roaming\webtoon*",
    "$env:USERPROFILE\.webtoon*",
    "$env:USERPROFILE\AppData\Local\webtoon*"
)

foreach ($config in $configLocations) {
    Get-Item $config -ErrorAction SilentlyContinue | ForEach-Object {
        try {
            Remove-Item $_.FullName -Recurse -Force -ErrorAction Stop
            Write-Host "   ✅ Removido: $($_.FullName)"
        } catch {
            Write-Host "   ⚠️  Erro ao remover: $($_.FullName)"
        }
    }
}

# 6. Limpar __pycache__ recursivamente
Write-Host ""
Write-Host "🗑️  Removendo __pycache__ e *.pyc..." -ForegroundColor Yellow
Get-ChildItem -Path "C:\" -Filter "__pycache__" -Recurse -ErrorAction SilentlyContinue -Force | ForEach-Object {
    try {
        Remove-Item $_.FullName -Recurse -Force -ErrorAction Stop
        Write-Host "   ✅ Removido: $($_.FullName)"
    } catch {
        # Silencioso para evitar muita saída
    }
} 2>$null

# 7. Limpeza do npm (se tiver)
Write-Host ""
Write-Host "🔧 Removendo cache de ferramentas..." -ForegroundColor Yellow
if (Test-Path "$env:USERPROFILE\AppData\Roaming\npm-cache") {
    Remove-Item "$env:USERPROFILE\AppData\Roaming\npm-cache" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "   ✅ Removido: npm cache"
}

# Resultado final
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  ✅ LIMPEZA CONCLUÍDA COM SUCESSO!                     ║" -ForegroundColor Green
Write-Host "║                                                        ║" -ForegroundColor Green
Write-Host "║  Próximos passos:                                      ║" -ForegroundColor Green
Write-Host "║  1. Feche este terminal                                ║" -ForegroundColor Green
Write-Host "║  2. Reinicie o computador (recomendado)                ║" -ForegroundColor Green
Write-Host "║  3. Siga o guia INSTALL_WINDOWS.md para instalar       ║" -ForegroundColor Green
Write-Host "║     novamente                                          ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Green

Write-Host ""
Write-Host "📚 Documentação: https://github.com/Noixfrio/WebtoonCleanerUltimate/blob/master/INSTALL_WINDOWS.md" -ForegroundColor Cyan
Write-Host ""

# Aguarde antes de fechar
Write-Host "Pressione qualquer tecla para fechar..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

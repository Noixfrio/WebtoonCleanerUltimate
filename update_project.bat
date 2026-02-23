@echo off
title Atualizador - Webtoon Cleaner Ultimate
setlocal enabledelayedexpansion

echo ==========================================
echo    ATUALIZADOR DO WEBTOON CLEANER
echo ==========================================
echo.

echo [+] Passo 1: Verificando conexao com o GitHub...
git fetch --all
if %errorlevel% neq 0 (
    echo [!] ERRO: Nao foi possivel conectar ao GitHub. Verifique sua internet.
    pause
    exit /b
)

echo [+] Passo 2: Tentando atualizar arquivos (Pull)...
echo [AVISO] Se voce editou o index.html ou outros arquivos, este passo pode falhar.
git pull origin master
if %errorlevel% neq 0 (
    echo.
    echo [!!!] ATENCAO: A atualizacao falhou por conflitos locais.
    echo [!!!] Se voce mudou o codigo manualmente, o Git nao quer sobrescrever.
    echo.
    echo [RECOMENDACAO] Rode o arquivo "FORCE_UPDATE_EVERYTHING.bat" para resetar tudo.
    pause
    exit /b
)

echo [+] Passo 3: Sincronizando bibliotecas...
if exist venv (
    call venv\Scripts\activate
    pip install -r requirements.txt
) else (
    echo [!] Venv nao encontrada. Pulando atualizacao de bibliotecas.
)

echo.
echo ==========================================
echo [+] PROJETO ATUALIZADO COM SUCESSO!
echo ==========================================
pause

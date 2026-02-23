@echo off
title Atualizador - Webtoon Cleaner Ultimate
setlocal enabledelayedexpansion

echo ==========================================
echo    ATUALIZADOR DO WEBTOON CLEANER
echo ==========================================
echo.

echo [+] Passo 1: Verificando conexao com a rede...
ping -n 1 github.com >nul
if %errorlevel% neq 0 (
    echo [!] ERRO: Nao foi possivel alcancar o GitHub.
    echo     Verifique se voce tem acesso a internet.
    pause
    exit /b
)

echo [+] Passo 2: Sincronizando com o servidor...
git fetch origin master
if %errorlevel% neq 0 (
    echo [!] ERRO: Falha ao conversar com o Git. O servidor pode estar fora do ar
    echo     ou seu repositorio local tem um problema.
    pause
    exit /b
)

echo [+] Passo 3: Tentando atualizar arquivos (Pull)...
echo [AVISO] Se voce editou arquivos do projeto, este passo pode falhar.
git pull origin master
if %errorlevel% neq 0 (
    echo.
    echo [!!!] ATENCAO: A atualizacao falhou por conflitos locais.
    echo [!!!] Isso acontece se voce alterou o codigo manualmente.
    echo.
    echo [SOLUCAO] Rode o arquivo "FORCE_UPDATE_EVERYTHING.bat" para resetar.
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

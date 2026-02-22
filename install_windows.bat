@echo off
setlocal
title Instalador - Webtoon Cleaner Ultimate

echo ======================================================
echo       Instalador Webtoon Cleaner Ultimate
echo ======================================================
echo.

:: Verifica se o Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado! 
    echo Por favor, instale o Python 3.10 ou superior do site python.org 
    echo Marque a opcao "Add Python to PATH" durante a instalacao.
    pause
    exit /b
)

echo [+] Criando ambiente virtual (venv)...
python -m venv venv

echo [+] Instalando dependencias (isso pode demorar alguns minutos)...
echo [+] Por favor, aguarde...
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo [ERRO] Ocorreu um problema na instalacao das bibliotecas.
    echo Verifique sua conexao com a internet e tente novamente.
    pause
    exit /b
)

echo.
echo ======================================================
echo       INSTALACAO CONCLUIDA COM SUCESSO!
echo ======================================================
echo.
echo Para iniciar o programa, use o arquivo "iniciar_servidor.bat"
echo.
pause

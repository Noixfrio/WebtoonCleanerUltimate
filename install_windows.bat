@echo off
setlocal
title Instalador - Webtoon Cleaner Ultimate

echo ======================================================
echo       Instalador Webtoon Cleaner Ultimate
echo ======================================================
echo.

:: Verifica se o Python está instalado e é a versão EXATA 3.10
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado! 
    echo Por favor, instale EXATAMENTE o Python 3.10.11 do site oficial.
    echo Marque a opcao "Add Python to PATH" durante a instalacao.
    pause
    exit /b
)

:: Extrai a versao do Python (ex: "Python 3.10.11" -> "3.10")
for /f "tokens=2 delims= " %%I in ('python --version 2^>^&1') do set PYTHON_VERSION=%%I
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do set PYTHON_MAJOR_MINOR=%%a.%%b

if not "%PYTHON_MAJOR_MINOR%"=="3.10" (
    echo ==============================================================
    echo [ERRO CRITICO DE VERSAO DO PYTHON]
    echo ==============================================================
    echo Voce esta usando o Python %PYTHON_VERSION%.
    echo A Inteligencia Artificial deste programa (PaddleOCR) EXIGE 
    echo EXATAMENTE a versao 3.10 para funcionar no Windows.
    echo.
    echo Como resolver:
    echo 1. Desinstale o seu Python %PYTHON_VERSION%.
    echo 2. Baixe o Python 3.10.11 no Google e instale.
    echo ==============================================================
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
    echo ==============================================================
    echo [ERRO CRITICO] Ocorreu um problema na instalacao das bibliotecas!
    echo ==============================================================
    echo Se o erro acima mencionar "paddlepaddle" ou "paddleocr",
    echo ISSO SIGNIFICA QUE SEU PYTHON E MUITO NOVO ^(3.12, 3.13 ou 3.14^).
    echo.
    echo A Inteligencia Artificial deste programa EXIGE O PYTHON 3.10.
    echo.
    echo Como resolver:
    echo 1. Desinstale o seu Python atual no Windows.
    echo 2. Baixe o Python 3.10.11 EXATAMENTE ^(procure no Google por Python 3.10.11^).
    echo 3. Apague a pasta "venv" amarela que foi criada aqui.
    echo 4. Rode este instalador novamente.
    echo ==============================================================
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

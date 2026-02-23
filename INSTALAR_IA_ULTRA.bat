@echo off
setlocal
title Instalador IA ULTRA - Webtoon Cleaner

echo ======================================================
echo       Instalador de Componentes IA ULTRA
echo ======================================================
echo.

:: Verifica se o Python está instalado
python --version >nul 2>&1
if errorlevel 1 goto python_nao_encontrado

:: Verifica se a venv existe
if not exist "venv\Scripts\activate.bat" goto venv_nao_encontrada

echo [+] Ativando ambiente virtual...
call venv\Scripts\activate

echo [+] Verificando dependencias necessarias...
pip install onnxruntime huggingface-hub --quiet

echo [+] Iniciando configuracao da IA Ultra...
python scripts/install_ultra.py

if errorlevel 1 goto erro_instalacao

echo.
echo ======================================================
echo       IA ULTRA INSTALADA COM SUCESSO!
echo ======================================================
echo.
echo Agora voce pode usar o "PROCESSAR IA (CALIBRADO)" 
echo no modo Ultra do programa.
echo.
pause
exit /b

:python_nao_encontrado
echo [ERRO] Python nao encontrado! 
echo Por favor, rode o arquivo "1_BAIXAR_PYTHON_3.10.bat" primeiro.
pause
exit /b

:venv_nao_encontrada
echo [ERRO] Ambiente virtual (venv) nao encontrado!
echo Por favor, rode o arquivo "2_INSTALAR_BIBLIOTECAS.bat" primeiro.
pause
exit /b

:erro_instalacao
echo.
echo [ERRO] Ocorreu um problema ao baixar os modelos da IA Ultra.
echo Verifique sua conexao com a internet e tente novamente.
pause
exit /b

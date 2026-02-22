@echo off
setlocal EnableDelayedExpansion
title Instalador Automático do Python 3.10

echo ==============================================================
echo       BAIXADOR AUTOMÁTICO DO PYTHON 3.10
echo ==============================================================
echo.
echo Este script vai baixar o instalador oficial do Python 3.10.11
echo diretamente do site oficial (python.org).
echo.
echo [!] ATENCAO QUANDO A INSTALACAO ABRIR:
echo Marque a opcao "Add Python 3.10 to PATH" na primeira tela!
echo.
echo Pressione qualquer tecla para comecar o download...
pause >nul

echo.
echo Baixando Python 3.10.11 (Aguarde, tem aprox. 27MB)...
curl -L -k -o python-3.10.11-amd64.exe https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe

if not exist python-3.10.11-amd64.exe (
    echo.
    echo [ERRO] Falha ao baixar! Verifique sua internet.
    echo Ou baixe manualmente de: https://www.python.org/downloads/release/python-31011/
    pause
    exit /b
)

echo.
echo Download concluido!
echo Abrindo o instalador...
echo Lembre-se de marcar a caixa "Add Python 3.10 to PATH"!
echo.
start /wait python-3.10.11-amd64.exe

echo.
echo ==============================================================
echo Instalacao concluida (ou cancelada). 
echo Se a instalacao deu certo, agora voce pode rodar o arquivo:
echo "install_windows.bat" (ou "2_INSTALAR_BIBLIOTECAS.bat")
echo ==============================================================
pause

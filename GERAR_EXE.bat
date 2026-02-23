@echo off
setlocal
title Gerador de Executavel - Manga Cleaner

echo ======================================================
echo       Gerador de Executavel (PyInstaller)
echo ======================================================
echo.

:: Verifica se a venv existe
if not exist "venv\Scripts\activate.bat" (
    echo [ERRO] Ambiente virtual (venv) nao encontrado!
    echo Por favor, rode o arquivo "2_INSTALAR_BIBLIOTECAS.bat" primeiro.
    pause
    exit /b
)

echo [+] Ativando ambiente virtual...
call venv\Scripts\activate

echo [+] Verificando PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [+] Instalando PyInstaller...
    pip install pyinstaller
)

echo [+] Iniciando processo de compilação (isso pode demorar muito)...
echo [+] Criando pasta portatil em dist/MangaCleaner...
pyinstaller --clean manga_cleaner.spec

if errorlevel 1 goto erro_build

echo.
echo ======================================================
echo       EXECUTAVEL GERADO COM SUCESSO!
echo ======================================================
echo.
echo O seu programa estah pronto na pasta:
echo dist\MangaCleaner
echo.
echo Para usar, basta abrir o arquivo "MangaCleaner.exe" 
echo dentro dessa pasta.
echo.
echo DICA: Voce pode mover a pasta "MangaCleaner" para
echo onde quiser e o programa continuarah funcionando.
echo.
pause
exit /b

:erro_build
echo.
echo [ERRO] Ocorreu um problema ao gerar o executavel.
echo Verifique as mensagens de erro acima.
pause
exit /b

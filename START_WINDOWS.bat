@echo off
echo Iniciando Toonix...
python ToonixLauncher.py
if %errorlevel% neq 0 (
    echo.
    echo Ocorreu um erro ao iniciar. Verifique se o Python esta instalado.
    pause
)

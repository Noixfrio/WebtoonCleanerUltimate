@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo  Toonix Editor - Build Windows (PyInstaller)
echo ============================================
echo.
echo Isso gera a pasta dist\ToonixEditor com ToonixLauncher.exe
echo NAO e um unico arquivo: o app precisa da pasta inteira.
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo Python nao encontrado no PATH.
    echo Instale Python 3.10 ou 3.11 e marque "Add python.exe to PATH".
    pause
    exit /b 1
)

python -c "import sys; raise SystemExit(0 if sys.version_info[:2] >= (3,10) else 1)"
if errorlevel 1 (
    echo Este projeto precisa de Python 3.10 ou 3.11.
    python --version
    pause
    exit /b 1
)

echo [1/3] Instalando dependencias...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller customtkinter
if errorlevel 1 (
    echo Falha ao instalar dependencias.
    pause
    exit /b 1
)

echo.
echo [2/3] Empacotando com PyInstaller...
python -m PyInstaller launcher.spec --clean --noconfirm
if errorlevel 1 (
    echo.
    echo O build falhou. Leia o erro acima.
    echo Causas comuns: pacote faltando, antivirus bloqueando dist\, disco cheio.
    pause
    exit /b 1
)

echo.
echo [3/3] Pronto.
echo Execute: dist\ToonixEditor\ToonixLauncher.exe
echo Na primeira vez use tambem: --skip-update
echo.
pause

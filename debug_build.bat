@echo off
echo [1/3] Limpando pastas antigas...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo [2/3] Iniciando Build com PyInstaller (v15)...
python -m PyInstaller launcher.spec --clean --noconfirm

echo [3/3] Iniciando Executavel para teste...
cd dist\ToonixEditor
echo.
echo ========================================================
echo O PROGRAMA VAI ABRIR COM UM CONSOLE PARA DEBUG.
echo SE ELE FECHAR SOZINHO, O ERRO FICARA NESTA TELA.
echo ========================================================
ToonixLauncher.exe
echo ========================================================
echo.
pause

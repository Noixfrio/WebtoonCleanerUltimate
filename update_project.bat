@echo off
title Atualizador - Webtoon Cleaner Ultimate

echo [+] Buscando novas atualizacoes no GitHub...
git pull

echo [+] Atualizando bibliotecas...
call venv\Scripts\activate
pip install -r requirements.txt

echo.
echo [+] Projeto atualizado!
pause

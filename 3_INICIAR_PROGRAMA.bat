@echo off
title Servidor - Webtoon Cleaner Ultimate
echo [+] Iniciando Webtoon Cleaner Ultimate...
echo [+] Abrindo servidor em http://localhost:5000

if not exist venv (
    echo [ERRO] Ambiente virtual nao encontrado. 
    echo Por favor, rode o arquivo "2_INSTALAR_BIBLIOTECAS.bat" primeiro.
    pause
    exit /b
)

call venv\Scripts\activate
python -m uvicorn web_app.main:app --host 0.0.0.0 --port 5000 --reload
pause

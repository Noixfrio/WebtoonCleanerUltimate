#!/bin/bash
echo "[+] Iniciando Webtoon Cleaner Ultimate..."
echo "[+] Abrindo servidor em http://localhost:5000"

if [ ! -d "venv" ]; then
    echo "[ERRO] Ambiente virtual não encontrado."
    echo "Por favor, rode './INSTALAR_BIBLIOTECAS.sh' primeiro."
    exit 1
fi

source venv/bin/activate
python3 -m uvicorn web_app.main:app --host 0.0.0.0 --port 5000 --reload

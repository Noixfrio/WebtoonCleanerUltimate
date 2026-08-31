#!/bin/bash
echo "Iniciando Toonix..."
python3 ToonixLauncher.py
if [ $? -ne 0 ]; then
    echo ""
    echo "Ocorreu um erro ao iniciar. Verifique se o Python 3 está instalado."
    read -p "Pressione Enter para fechar..."
fi

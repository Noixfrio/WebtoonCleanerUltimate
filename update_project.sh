#!/bin/bash
echo "Busando atualizações..."
git pull
source venv/bin/activate
pip install -r requirements.txt
echo "Projeto atualizado!"

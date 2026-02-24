#!/bin/bash
echo "======================================================"
echo "      Gerador de Executável - Manga Cleaner"
echo "======================================================"

if [ ! -f "venv/bin/activate" ]; then
    echo "[ERRO] Ambiente virtual (venv) não encontrado!"
    echo "Por favor, rode './INSTALAR_BIBLIOTECAS.sh' primeiro."
    exit 1
fi

echo "[+] Ativando ambiente virtual..."
source venv/bin/activate

echo "[+] Verificando PyInstaller..."
pip show pyinstaller >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "[+] Instalando PyInstaller..."
    pip install pyinstaller
fi

echo "[+] Iniciando processo de compilação..."
pyinstaller --clean manga_cleaner.spec

if [ $? -eq 0 ]; then
    echo ""
    echo "======================================================"
    echo "      EXECUTÁVEL GERADO COM SUCESSO!"
    echo "======================================================"
    echo "O programa está em: dist/MangaCleaner/MangaCleaner"
else
    echo ""
    echo "[ERRO] Falha ao gerar o executável."
fi

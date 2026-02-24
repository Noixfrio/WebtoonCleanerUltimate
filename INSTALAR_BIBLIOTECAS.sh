#!/bin/bash
echo "======================================================"
echo "      Instalador de Bibliotecas - Manga Cleaner"
echo "======================================================"
echo ""

# Cria o ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo "[+] Criando ambiente virtual (Python 3)..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[ERRO] Falha ao criar venv. Verifique se o python3.10 está instalado."
        exit 1
    fi
fi

echo "[+] Ativando ambiente virtual..."
source venv/bin/activate

echo "[+] Atualizando pip..."
pip install --upgrade pip

echo "[+] Instalando dependências (isso pode demorar)..."
pip install -r requirements.txt

echo "[+] Verificando PyInstaller..."
pip show pyinstaller >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "[+] Instalando PyInstaller..."
    pip install pyinstaller
fi

echo ""
echo "======================================================"
echo "      INSTALAÇÃO CONCLUÍDA COM SUCESSO!"
echo "======================================================"
echo "Agora você pode usar './INICIAR_PROGRAMA.sh' para rodar."

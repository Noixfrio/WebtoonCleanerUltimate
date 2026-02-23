@echo off
title RESET E ATUALIZACAO FORCADA
echo ======================================================
echo    BOMBA ATOMICA: RESET TOTAL PARA VERSAO DO GITHUB
echo ======================================================
echo.
echo [!] ATENCAO: Isso vai APAGAR qualquer mudanca que voce
echo     tenha feito manualmente no codigo e voltar para
echo     a versao ORIGINAL e LIMPA do desenvolvedor.
echo.
set /p escolha="Tem certeza que deseja resetar tudo? (S/N): "

if /i "%escolha%" neq "S" (
    echo [+] Operacao cancelada.
    pause
    exit /b
)

echo [+] Resetando arquivos locais...
git reset --hard origin/master
git clean -df

echo [+] Puxando versao mais recente...
git pull origin master

echo [+] Atualizando bibliotecas...
if exist venv (
    call venv\Scripts\activate
    pip install -r requirements.txt
)

echo.
echo [+] PRONTO! Seu projeto agora esta IDENTICO ao do GitHub.
echo.
pause

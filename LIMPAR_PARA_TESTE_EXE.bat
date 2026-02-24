@echo off
title Limpeza Provisoria para Teste de EXE
setlocal

echo ======================================================
echo    LIMPANDO AMBIENTE PARA TESTAR O EXECUTAVEL
echo ======================================================
echo.
echo ATENCAO: Este script vai apagar a pasta 'venv' (onde estao as bibliotecas).
echo Isso permitira testar se o .EXE realmente funciona sozinho.
echo.
set /p confirm="Deseja continuar? (S/N): "
if /i "%confirm%" neq "S" exit /b

echo [+] Removendo pasta de bibliotecas (venv)...
if exist venv (
    rmdir /s /q venv
    echo [OK] venv removida.
) else (
    echo [!] venv nao encontrada.
)

echo [+] Removendo pastas temporarias de build...
if exist build (
    rmdir /s /q build
    echo [OK] build removida.
)

echo.
echo ======================================================
echo    LIMPEZA CONCLUIDA!
echo ======================================================
echo.
echo Agora tente rodar o programa pela pasta:
echo dist\MangaCleaner\MangaCleaner.exe
echo.
echo Se ele abrir, significa que o seu executavel e 100%% independente!
echo.
pause

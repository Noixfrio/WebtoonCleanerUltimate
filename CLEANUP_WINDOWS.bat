@echo off
REM Script de Limpeza Completa - Webtoon Cleaner Ultimate
REM Execute como Administrador

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║  Limpeza Completa - Webtoon Cleaner Ultimate           ║
echo ║  Removerá todas as instalações anteriores              ║
echo ╚════════════════════════════════════════════════════════╝
echo.
echo ⚠️  Este script vai APAGAR:
echo    - Pastas do projeto
echo    - Ambientes virtuais ^(venv^)
echo    - Cache do pip
echo    - Modelos de IA baixados
echo    - Configurações salvas
echo.

set /p confirm="Deseja continuar? (S/N): "
if /i not "%confirm%"=="S" (
    echo Cancelado.
    pause
    exit /b
)

echo.
echo Iniciando limpeza...
echo.

REM Parar processos Python
echo Encerrando processos Python...
taskkill /F /IM python.exe 2>nul >nul
timeout /t 1 /nobreak >nul

REM Remover pastas do projeto
echo Removendo pastas do projeto...
if exist "C:\WebtoonCleanerUltimate" rmdir /s /q "C:\WebtoonCleanerUltimate" 2>nul
if exist "%USERPROFILE%\Desktop\WebtoonCleanerUltimate" rmdir /s /q "%USERPROFILE%\Desktop\WebtoonCleanerUltimate" 2>nul
if exist "%USERPROFILE%\Downloads\WebtoonCleanerUltimate" rmdir /s /q "%USERPROFILE%\Downloads\WebtoonCleanerUltimate" 2>nul

REM Remover venv
echo Removendo ambientes virtuais...
if exist "venv" rmdir /s /q "venv" 2>nul
if exist "%USERPROFILE%\venv" rmdir /s /q "%USERPROFILE%\venv" 2>nul

REM Limpar cache do pip
echo Limpando cache do pip...
if exist "%USERPROFILE%\AppData\Local\pip\Cache" rmdir /s /q "%USERPROFILE%\AppData\Local\pip\Cache" 2>nul
if exist "%USERPROFILE%\.cache\pip" rmdir /s /q "%USERPROFILE%\.cache\pip" 2>nul

REM Limpar modelos de IA
echo Removendo modelos de IA...
if exist "%USERPROFILE%\.cache\huggingface" rmdir /s /q "%USERPROFILE%\.cache\huggingface" 2>nul
if exist "%USERPROFILE%\.easyocr" rmdir /s /q "%USERPROFILE%\.easyocr" 2>nul
if exist "%USERPROFILE%\AppData\Local\huggingface" rmdir /s /q "%USERPROFILE%\AppData\Local\huggingface" 2>nul

REM Limpar configurações
echo Removendo configurações salvas...
if exist "%USERPROFILE%\AppData\Roaming\webtoon" rmdir /s /q "%USERPROFILE%\AppData\Roaming\webtoon" 2>nul

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║  LIMPEZA CONCLUÍDA COM SUCESSO!                        ║
echo ║                                                        ║
echo ║  Próximos passos:                                      ║
echo ║  1. Feche este terminal                                ║
echo ║  2. Reinicie o computador ^(recomendado^)               ║
echo ║  3. Siga o guia INSTALL_WINDOWS.md para instalar       ║
echo ║     novamente                                          ║
echo ╚════════════════════════════════════════════════════════╝
echo.
echo Documentação: https://github.com/Noixfrio/WebtoonCleanerUltimate/blob/master/INSTALL_WINDOWS.md
echo.

pause

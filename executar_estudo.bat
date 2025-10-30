@echo off
chcp 65001 >nul
:: ============================================================================
:: Script Batch para Executar Estudo Paramétrico
:: Facilita execução no Windows
:: ============================================================================

echo.
echo ================================================================================
echo   ESTUDO PARAMÉTRICO - CAMADA LIMITE LAMINAR
echo   Automação GMSH + SU2
echo ================================================================================
echo.

:MENU
echo.
echo Escolha uma opção:
echo.
echo   1. Localizar GMSH e SU2 (execute primeiro!)
echo   2. Gerar malhas parametricamente
echo   3. Executar SU2 para malhas existentes
echo   4. Estudo paramétrico completo (Recomendado)
echo   5. Analisar resultados
echo   6. Gerar relatório HTML
echo   7. Instalar dependências Python
echo   0. Sair
echo.
set /p opcao="Digite o número da opção: "

if "%opcao%"=="1" goto FIND
if "%opcao%"=="2" goto GENMESH
if "%opcao%"=="3" goto RUNSU2
if "%opcao%"=="4" goto PARAMETRIC
if "%opcao%"=="5" goto ANALYZE
if "%opcao%"=="6" goto REPORT
if "%opcao%"=="7" goto INSTALL
if "%opcao%"=="0" goto END
goto MENU

:FIND
echo.
echo ================================================================================
echo Localizando executáveis...
echo ================================================================================
python find_executables.py
pause
goto MENU

:GENMESH
echo.
echo ================================================================================
echo Gerando malhas parametricamente...
echo ================================================================================
python generate_meshes.py
pause
goto MENU

:RUNSU2
echo.
echo ================================================================================
echo Executando SU2 para todas as malhas...
echo ================================================================================
python run_su2_batch.py
pause
goto MENU

:PARAMETRIC
echo.
echo ================================================================================
echo Executando estudo paramétrico completo...
echo ================================================================================
echo.
echo Este processo pode demorar várias horas dependendo do número de casos.
echo Você pode acompanhar o progresso no terminal.
echo.
set /p confirm="Deseja continuar? (S/N): "
if /i "%confirm%"=="S" (
    python run_parametric_study.py
) else (
    echo Operação cancelada.
)
pause
goto MENU

:ANALYZE
echo.
echo ================================================================================
echo Analisando resultados...
echo ================================================================================
python analyze_results.py
pause
goto MENU

:REPORT
echo.
echo ================================================================================
echo Gerando relatório HTML...
echo ================================================================================
python generate_report.py
pause
goto MENU

:INSTALL
echo.
echo ================================================================================
echo Instalando dependências Python...
echo ================================================================================
echo.
echo Instalando matplotlib e pandas...
pip install matplotlib pandas
echo.
echo ✓ Instalação concluída!
pause
goto MENU

:END
echo.
echo Encerrando...
echo.
exit


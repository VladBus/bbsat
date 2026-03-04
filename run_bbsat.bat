@echo off
setlocal

:: --- НАСТРОЙКИ ПУТЕЙ ---
:: Актуальный путь к проекту в VS Code
set "PROJECT_DIR=E:\Programming_Work\VScode_Work\bbsat"
:: Путь к логам на диске S
set "LOG_FILE=S:\message\logofile\bat_log.txt"
:: Путь к python из виртуального окружения
set "PYTHON_EXE=%PROJECT_DIR%\.venv\Scripts\python.exe"
:: Путь к основному скрипту
set "MAIN_SCRIPT=%PROJECT_DIR%\main.py"

echo ======================================== >> "%LOG_FILE%"
echo Starts script main.py at %date% %time%... >> "%LOG_FILE%"

:: Проверка наличия python.exe перед запуском
if not exist "%PYTHON_EXE%" (
    echo [ERROR] Python not found at: %PYTHON_EXE% >> "%LOG_FILE%"
    exit /b 1
)

:: Запуск скрипта
"%PYTHON_EXE%" "%MAIN_SCRIPT%" >> "%LOG_FILE%" 2>&1

set "EXIT_CODE=%ERRORLEVEL%"

if %EXIT_CODE% NEQ 0 (
    echo [ERROR] Ошибка при выполнении main.py. Код ошибки: %EXIT_CODE% >> "%LOG_FILE%"
) else (
    echo [SUCCESS] Script finished successfully. >> "%LOG_FILE%"
)

echo Script main.py end at %date% %time% >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"

exit /b %EXIT_CODE%

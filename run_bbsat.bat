@echo off
setlocal

:: --- НАСТРОЙКИ ПУТЕЙ ---
set "PROJECT_DIR=E:\Programming_Work\VScode_Work\bbsat"
:: Обновленный путь к логам в новой структуре
set "LOG_DIR=S:\reports\logs"
set "LOG_FILE=%LOG_DIR%\bat_startup_log.txt"
set "PYTHON_EXE=%PROJECT_DIR%\.venv\Scripts\python.exe"
set "MAIN_SCRIPT=%PROJECT_DIR%\main.py"

:: Создаем папку для логов, если сетевой диск доступен, но папки еще нет
if exist S:\ (
    if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
) else (
    echo [CRITICAL] Сетевой диск S: не доступен!
    exit /b 1
)

echo ======================================== >> "%LOG_FILE%"
echo Запуск планировщика: %date% %time% >> "%LOG_FILE%"

:: Проверка наличия виртуального окружения
if not exist "%PYTHON_EXE%" (
    echo [ERROR] Виртуальное окружение не найдено: %PYTHON_EXE% >> "%LOG_FILE%"
    exit /b 1
)

:: Проверка наличия главного скрипта
if not exist "%MAIN_SCRIPT%" (
    echo [ERROR] Файл main.py не найден: %MAIN_SCRIPT% >> "%LOG_FILE%"
    exit /b 1
)

:: Переходим в рабочую директорию (важно для относительных путей в Python)
cd /d "%PROJECT_DIR%"

:: Запуск основного процесса
echo Запуск main.py... >> "%LOG_FILE%"
"%PYTHON_EXE%" "%MAIN_SCRIPT%" >> "%LOG_FILE%" 2>&1

set "EXIT_CODE=%ERRORLEVEL%"

if %EXIT_CODE% NEQ 0 (
    echo [ERROR] Сбой main.py. Код ошибки: %EXIT_CODE% >> "%LOG_FILE%"
) else (
    echo [SUCCESS] Работа завершена успешно. >> "%LOG_FILE%"
)

echo Завершение сессии: %date% %time% >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"

exit /b %EXIT_CODE%
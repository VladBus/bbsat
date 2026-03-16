@echo off
chcp 65001 >nul 2>&1
setlocal

:: --- НАСТРОЙКИ ПУТЕЙ ---
set "PROJECT_DIR=E:\Programming_Work\VScode_Work\bbsat"
set "LOG_DIR=S:\reports\logs"
set "LOG_FILE=%LOG_DIR%\bat_startup_log.txt"
set "PYTHON_EXE=%PROJECT_DIR%\.venv\Scripts\python.exe"
set "MAIN_SCRIPT=%PROJECT_DIR%\main.py"

:: Создаем папку для логов, если сетевой диск доступен
if exist S:\ (
    if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
) else (
    echo [CRITICAL] Сетевой диск S: не доступен!
    exit /b 1
)

echo ======================================== >> "%LOG_FILE%"
echo Проверка запуска: %date% %time% >> "%LOG_FILE%"

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

:: Переходим в рабочую директорию
cd /d "%PROJECT_DIR%"

:: Запуск основного процесса в фоновом режиме
echo Запуск main.py... >> "%LOG_FILE%"
start "BBSAT Scheduler" /min "%PYTHON_EXE%" "%MAIN_SCRIPT%"

echo [SUCCESS] Планировщик запущен (или уже работает) >> "%LOG_FILE%"
echo Завершение сессии: %date% %time% >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"

exit /b 0

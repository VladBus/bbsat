@echo off

echo Starts skript main.py at %date% %time%... >> "S:\message\logofile\bat_log.txt"

"E:\Programming_Work\Pycharm_Work\bbsat\.venv\Scripts\python.exe" "E:\Programming_Work\Pycharm_Work\bbsat\main.py" >> "S:\message\logofile\bat_log.txt" 2>&1

if %ERRORLEVEL% NEQ 0 (
    echo Ошибка при выполнении main.py. Код ошибки: %ERRORLEVEL% >> "S:\message\logofile\bat_log.txt"
)

echo Skript main.py end at %date% %time% >> "S:\message\logofile\bat_log.txt"

echo. >> "S:\message\logofile\bat_log.txt"  REM Добавляем пустую строку для удобства чтения

exit /b %ERRORLEVEL%

import schedule
import time
import os
import logging
import subprocess

# Настройки
LOG_FILE = "S:\\message\\logofile\\task_log.txt"  # Путь к файлу логов
SORT_FILES_PATH = "tiff_processing/SortFilesByDate.py"
TIFF_COMPRESSOR_PATH = "tiff_processing/tiff_compressor.py"
STATISTIC_PATH = "week_message/statistic.py"
SEND_MESSAGE_PATH = "week_message/send_message.py"

# Настройка логирования
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s'
)

# Задачи расписания
schedule.every().day.at("00:05").do(lambda: run_script(SORT_FILES_PATH))
schedule.every().day.at("00:50").do(lambda: run_script(TIFF_COMPRESSOR_PATH))
schedule.every().wednesday.at("02:00").do(lambda: run_script(STATISTIC_PATH))
schedule.every().wednesday.at("02:45").do(lambda: run_script(SEND_MESSAGE_PATH))

# Завершение программы в разное время для разных дней недели
schedule.every().wednesday.at("03:00").do(lambda: exit())  # Среда
schedule.every().day.at("02:10").do(lambda: exit())  # Все остальные дни


# Функция для запуска скриптов
def run_script(script_path):
    if not os.path.isfile(script_path):
        logging.error(f"Скрипт не найден: {script_path}")
        return
    try:
        logging.info(f"Запуск скрипта: {script_path}")
        result = subprocess.run(["python", script_path], capture_output=True, text=True)
        if result.returncode == 0:
            logging.info(f"Скрипт {script_path} успешно завершён.")
            if result.stdout:
                logging.info(f"Вывод: {result.stdout}")
        else:
            logging.error(
                f"Скрипт {script_path} завершился с ошибкой. Код выхода: {result.returncode}. Ошибка: {result.stderr}")
    except Exception as e:
        logging.error(f"Ошибка при запуске {script_path}: {e}")


# Бесконечный цикл для выполнения задач
while True:
    schedule.run_pending()
    time.sleep(1)

import schedule
import time
import os
import logging
import datetime

# Настройки
LOG_FILE = "S:\\message\\logofile\\task_log.txt"  # Путь к файлу логов
SORT_FILES_PATH = "tiff_processing/SortFilesByDate.py"
TIFF_COMPRESSOR_PATH = "tiff_processing/tiff_compressor.py"
STATISTIC_PATH = "week_message/statistic.py"
SEND_MESSAGE_PATH = "week_message/send_message.py"

# Настройка логирования
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s')

# Задачи расписания
schedule.every().day.at("01:00").do(lambda: run_script(SORT_FILES_PATH))
schedule.every().day.at("01:50").do(lambda: run_script(TIFF_COMPRESSOR_PATH))
schedule.every().wednesday.at("02:45").do(lambda: run_script(STATISTIC_PATH))
schedule.every().wednesday.at("03:00").do(lambda: run_script(SEND_MESSAGE_PATH))

# Завершение программы в разное время для разных дней недели
schedule.every().wednesday.at("03:08").do(lambda: exit())  # Среда
schedule.every().day.at("02:45").do(lambda: exit())  # Все остальные дни


# Функция для запуска скриптов
def run_script(script_path):
    try:
        logging.info(f"Запуск скрипта: {script_path}")
        os.system(f"python {script_path}")
    except Exception as e:
        logging.error(f"Ошибка при запуске {script_path}: {e}")


# Бесконечный цикл для выполнения задач
while True:
    schedule.run_pending()
    time.sleep(1)

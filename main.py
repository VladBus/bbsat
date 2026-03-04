"""
Модуль для автоматического запуска задач по расписанию:
сортировка файлов, сжатие TIFF и отправка статистики.
"""

import logging
import os
import subprocess
import sys
import time

import schedule

# Настройка базовой директории
BASE_DIR = "E:\\Programming_Work\\VScode_Work\\bbsat\\"

# Настройки путей к скриптам
LOG_FILE = os.path.join("S:\\message\\logofile\\task_log.txt")
SORT_FILES_PATH = os.path.join(BASE_DIR, "tiff_processing", "sort_files_by_date.py")
TIFF_COMPRESSOR_PATH = os.path.join(BASE_DIR, "tiff_processing", "tiff_compressor.py")
STATISTIC_PATH = os.path.join(BASE_DIR, "week_message", "statistic.py")
SEND_MESSAGE_PATH = os.path.join(BASE_DIR, "week_message", "send_message.py")

# Настройка логирования
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s",
)


def add_blank_line_to_log():
    """Добавляет пустую строку в лог файл перед началом работы программы."""
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "a", encoding="utf-8") as log_file:
            log_file.write("\n")


def tasks_and_exit():
    """Завершение программы."""
    logging.info("Программа завершилась.")
    sys.exit(0)


def run_script(script_path):
    """Запускает указанный скрипт и логирует его выполнение."""
    logging.info("Проверка существования скрипта: %s", script_path)

    if not os.path.isfile(script_path):
        logging.error("Скрипт не найден: %s", script_path)
        return

    try:
        logging.info("Запуск скрипта: %s", script_path)
        start_time = time.time()

        # Условие для исключения вывода tiff_compressor
        if script_path == TIFF_COMPRESSOR_PATH:
            result = subprocess.run(
                ["python", script_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,  # Явное указание для Pylint
            )
        else:
            result = subprocess.run(
                ["python", script_path],
                capture_output=True,
                text=True,
                check=False,
            )

        end_time = time.time()
        execution_time = end_time - start_time

        if result.returncode == 0:
            logging.info(
                "Скрипт %s успешно завершён. Время: %.2f сек.",
                script_path,
                execution_time,
            )
            if hasattr(result, "stdout") and result.stdout:
                logging.info("Вывод: %s", result.stdout)
        else:
            logging.error(
                "Ошибка в %s. Код: %s. Ошибка: %s. Время: %.2f сек.",
                script_path,
                result.returncode,
                result.stderr,
                execution_time,
            )
    except Exception as e:  # pylint: disable=broad-exception-caught
        logging.error("Критическая ошибка при запуске %s: %s", script_path, e)


# Планирование задач (передаем функцию и аргумент отдельно)
schedule.every().day.at("00:04").do(run_script, SORT_FILES_PATH)
schedule.every().day.at("00:30").do(run_script, TIFF_COMPRESSOR_PATH)
schedule.every().wednesday.at("02:25").do(run_script, STATISTIC_PATH)
schedule.every().wednesday.at("02:45").do(run_script, SEND_MESSAGE_PATH)
schedule.every().day.at("02:50").do(tasks_and_exit)

# Константы интервала
LOG_INTERVAL = 120
last_log_time = time.time()

add_blank_line_to_log()

# Бесконечный цикл
while True:
    current_time = time.time()
    if current_time - last_log_time >= LOG_INTERVAL:
        logging.info("Проверка и выполнение запланированных задач.")
        last_log_time = current_time

    schedule.run_pending()
    time.sleep(1)

"""
Модуль для автоматического запуска задач по расписанию:
сортировка файлов, сжатие TIFF и отправка статистики.
"""

import logging
import os
import subprocess
import time
import schedule

# --- КОНФИГУРАЦИЯ ПУТЕЙ ---
BASE_DIR = r"E:\Programming_Work\VScode_Work\bbsat"
# Новая структура папок согласно твоим изменениям
REPORTS_DIR = r"S:\reports"
LOG_DIR = os.path.join(REPORTS_DIR, "logs")
ARCHIVE_DIR = os.path.join(REPORTS_DIR, "archive_stat")
LOG_FILE = os.path.join(LOG_DIR, "task_log.txt")

# Пути к скриптам модулей
CLEANER_PATH = os.path.join(BASE_DIR, "tiff_processing", "tiff_viirs_cleaner.py")
SORT_FILES_PATH = os.path.join(BASE_DIR, "tiff_processing", "sort_files_by_date.py")
TIFF_COMPRESSOR_PATH = os.path.join(BASE_DIR, "tiff_processing", "tiff_compressor.py")
STATISTIC_PATH = os.path.join(BASE_DIR, "week_message", "statistic.py")
SEND_MESSAGE_PATH = os.path.join(BASE_DIR, "week_message", "send_message.py")

# --- ПОДГОТОВКА СРЕДЫ ---
for folder in [LOG_DIR, ARCHIVE_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Настройка логирования (добавлена кодировка utf-8)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
)


def run_script(script_path):
    """Безопасный запуск внешних python-скриптов."""
    if not os.path.isfile(script_path):
        logging.error("Файл не найден: %s", script_path)
        return

    script_name = os.path.basename(script_path)
    try:
        logging.info(">>> СТАРТ: %s", script_name)
        start_t = time.time()

        # Для компрессора подавляем стандартный вывод, чтобы не раздувать лог-файл
        if script_path == TIFF_COMPRESSOR_PATH:
            result = subprocess.run(
                ["python", script_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
        else:
            result = subprocess.run(
                ["python", script_path], capture_output=True, text=True, check=False
            )

        duration = time.time() - start_t

        if result.returncode == 0:
            logging.info("УСПЕХ: %s (время: %.2f сек.)", script_name, duration)
        else:
            logging.error(
                "ОШИБКА в %s (Код: %s): %s",
                script_name,
                result.returncode,
                result.stderr,
            )

    except Exception as e:  # pylint: disable=broad-exception-caught
        logging.error("КРИТИЧЕСКИЙ СБОЙ при запуске %s: %s", script_name, e)


# --- РАСПИСАНИЕ ЗАДАЧ ---

# Каждый день: очистка, сортировка, сжатие и сбор данных
schedule.every().day.at("00:01").do(run_script, CLEANER_PATH)
schedule.every().day.at("00:05").do(run_script, SORT_FILES_PATH)
schedule.every().day.at("00:30").do(run_script, TIFF_COMPRESSOR_PATH)
schedule.every().day.at("02:25").do(run_script, STATISTIC_PATH)

# Раз в неделю: отправка накопленной статистики
schedule.every().wednesday.at("02:45").do(run_script, SEND_MESSAGE_PATH)

logging.info("=== Планировщик BBSAT запущен и готов к работе ===")

if __name__ == "__main__":
    # Бесконечный цикл ожидания
    while True:
        schedule.run_pending()
        time.sleep(30)

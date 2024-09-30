import schedule
import time
import os
import logging
import subprocess

# Настройки
LOG_FILE = "S:\\message\\logofile\\task_log.txt"  # Путь к файлу логов
SORT_FILES_PATH = "tiff_processing/SortFilesByDate.py"  # Путь к скрипту сортировки файлов
TIFF_COMPRESSOR_PATH = "tiff_processing/tiff_compressor.py"  # Путь к скрипту сжатия TIFF
STATISTIC_PATH = "week_message/statistic.py"  # Путь к скрипту статистики
SEND_MESSAGE_PATH = "week_message/send_message.py"  # Путь к скрипту отправки сообщений

# Настройка логирования
logging.basicConfig(
    filename=LOG_FILE,  # Указываем файл для логирования
    level=logging.INFO,  # Устанавливаем уровень логирования
    format='%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s'  # Формат сообщений в логе
)

# Запланированные задачи
schedule.every().day.at("00:02").do(lambda: run_script(SORT_FILES_PATH))
schedule.every().day.at("00:30").do(lambda: run_script(TIFF_COMPRESSOR_PATH))
schedule.every().wednesday.at("02:20").do(lambda: run_script(STATISTIC_PATH))
schedule.every().wednesday.at("02:50").do(lambda: run_script(SEND_MESSAGE_PATH))

# Завершение программы в разное время
schedule.every().wednesday.at("03:00").do(lambda: exit(0))  # Завершение работы в среду
schedule.every().day.at("02:25").do(lambda: exit(0))  # Завершение работы в остальные дни


# Функция для запуска скриптов
def run_script(script_path):
    logging.info(f"Проверка существования скрипта: {script_path}")  # Логирование проверки существования

    if not os.path.isfile(script_path):  # Проверка, существует ли файл
        logging.error(f"Скрипт не найден: {script_path}")  # Логирование ошибки, если файл не найден
        return  # Завершение функции, если файла нет

    try:
        logging.info(f"Запуск скрипта: {script_path}")  # Логирование перед запуском скрипта

        # Запись времени начала выполнения скрипта
        start_time = time.time()  # Текущие время до запуска
        result = subprocess.run(["python", script_path], capture_output=True,
                                text=True)  # Запуск скрипта и сохранение результата

        # Запись времени окончания выполнения скрипта
        end_time = time.time()  # Текущее время после завершения
        execution_time = end_time - start_time  # Время выполнения

        # Проверяем результат выполнения
        if result.returncode == 0:
            logging.info(
                f"Скрипт {script_path} успешно завершён. Время выполнения: {execution_time:.2f} секунд.")  # Лог.успеха
            if result.stdout:  # Если есть вывод
                logging.info(f"Вывод: {result.stdout}")  # Логирование вывода скрипта
        else:
            logging.error(
                f"Скрипт {script_path} завершился с ошибкой. Код выхода: {result.returncode}. Ошибка: {result.stderr}. \
                Время выполнения: {execution_time:.2f} секунд."  # Логирование ошибки с кодом
            )
    except Exception as e:
        logging.error(f"Ошибка при запуске {script_path}: {e}")  # Логирование ошибки при запуске


# Бесконечный цикл для выполнения задач
last_log_time = time.time()  # Переменная для отслеживания времени последнего логирования
log_interval = 30  # Интервал логирования в секундах

while True:
    current_time = time.time()  # Текущее время
    if current_time - last_log_time >= log_interval:  # Проверка, прошло ли 30 секунд
        logging.info("Проверка и выполнение запланированных задач.")  # Логирование проверки задач
        last_log_time = current_time  # Обновление времени последнего логирования

    schedule.run_pending()  # Выполнение запланированных задач
    time.sleep(1)  # Пауза в 1 секунду для предотвращения излишней нагрузки на процессор

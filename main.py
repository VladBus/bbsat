import schedule
import time
import os
import logging
import subprocess

# Настройка базовой директории
BASE_DIR = "E:\\Programming_Work\\Pycharm_Work\\bbsat\\"

# Настройки путей к скриптам
LOG_FILE = os.path.join("S:\\message\\logofile\\task_log.txt")  # Путь к файлу логов
SORT_FILES_PATH = os.path.join(BASE_DIR, "tiff_processing", "SortFilesByDate.py")  # Путь к скрипту сортировки файлов
TIFF_COMPRESSOR_PATH = os.path.join(BASE_DIR, "tiff_processing", "tiff_compressor.py")  # Путь к скрипту сжатия TIFF
STATISTIC_PATH = os.path.join(BASE_DIR, "week_message", "statistic.py")  # Путь к скрипту статистики
SEND_MESSAGE_PATH = os.path.join(BASE_DIR, "week_message", "send_message.py")  # Путь к скрипту отправки сообщений

# Настройка логирования
logging.basicConfig(
    filename=LOG_FILE,  # Указываем файл для логирования
    level=logging.INFO,  # Устанавливаем уровень логирования
    format='%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s'  # Формат сообщений в логе
)


# Функция для добавления пустой строки в лог при новом запуске
def add_blank_line_to_log():
    """Добавляет пустую строку в лог файл перед началом работы программы."""
    if os.path.exists(LOG_FILE):  # Проверка на существование файла лога
        with open(LOG_FILE, "a") as log_file:
            log_file.write("\n")  # Запись пустой строки


# Запланированные задачи
schedule.every().day.at("00:02").do(lambda: run_script(SORT_FILES_PATH))  # Запуск скрипта сортировки
schedule.every().day.at("00:30").do(lambda: run_script(TIFF_COMPRESSOR_PATH))  # Запуск скрипта сжатия TIFF
schedule.every().wednesday.at("02:25").do(lambda: run_script(STATISTIC_PATH))  # Запуск скрипта статистики
schedule.every().wednesday.at("02:45").do(lambda: run_script(SEND_MESSAGE_PATH))  # Запуск скрипта отправки сообщений

# Завершение программы каждый день в 2:50
schedule.every().day.at("02:50").do(lambda: complete_tasks_and_exit())  # Проверка завершения задач и выход


# Функция для завершения работы программы с учетом выполнения всех задач
def complete_tasks_and_exit():
    """Завершает работу программы, дожидаясь выполнения всех запланированных задач."""
    unfinished_jobs = schedule.get_jobs()  # Получаем все запланированные задачи
    if unfinished_jobs:  # Проверка на незавершенные задачи
        logging.info(f"Ожидание завершения задач перед выходом: {unfinished_jobs}")  # Логирование оставшихся задач
        time.sleep(30)  # Задержка для завершения задач
        unfinished_jobs = schedule.get_jobs()  # Проверяем снова
        if unfinished_jobs:  # Если есть незавершенные задачи
            logging.info("Некоторые задачи все еще выполняются, завершение программы не будет выполнено.")
            return  # Не завершать программу, просто выход из функции
    logging.info("Все задачи завершены, выходим.")  # Логирование завершения всех задач
    exit(0)  # Завершение программы


# Функция для запуска скриптов
def run_script(script_path):
    """Запускает указанный скрипт и логирование его выполнения."""
    logging.info(f"Проверка существования скрипта: {script_path}")  # Логирование проверки существования

    if not os.path.isfile(script_path):  # Проверка на существование файла
        logging.error(f"Скрипт не найден: {script_path}")  # Логирование ошибки, если файла нет
        return  # Завершение функции, если файла нет

    try:
        logging.info(f"Запуск скрипта: {script_path}")  # Логирование перед запуском
        start_time = time.time()  # Запоминаем время начала выполнения

        # Условие для исключения вывода tiff_compressor
        if script_path == TIFF_COMPRESSOR_PATH:
            result = subprocess.run(["python", script_path], stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL)  # Запуск без вывода
        else:
            result = subprocess.run(["python", script_path], capture_output=True, text=True)  # Запуск с выводом

        end_time = time.time()  # Записываем время окончания выполнения
        execution_time = end_time - start_time  # Вычисляем время выполнения

        # Проверяем результат выполнения
        if result.returncode == 0:  # Код завершения равен 0 (успех)
            logging.info(
                f"Скрипт {script_path} успешно завершён. Время выполнения: {execution_time:.2f} секунд.")  # Лог.успех
            if result.stdout:  # Если есть вывод
                logging.info(f"Вывод: {result.stdout}")  # Логирование вывода
        else:
            logging.error(
                f"Скрипт {script_path} завершился с ошибкой. Код выхода: {result.returncode}. Ошибка: {result.stderr}. "
                f"Время выполнения: {execution_time:.2f} секунд.")  # Логирование ошибки
    except Exception as e:  # Обработка общего исключения
        logging.error(f"Ошибка при запуске {script_path}: {e}")  # Логирование ошибки


# Интервал логирования
log_interval = 60  # Интервал логирования установлен на 60 секунд
last_log_time = time.time()  # Переменная для отслеживания времени последнего логирования

# Добавляем пустую строку в лог перед новым запуском
add_blank_line_to_log()

# Бесконечный цикл для выполнения задач
while True:
    current_time = time.time()  # Текущее время
    if current_time - last_log_time >= log_interval:  # Проверка времени для логирования
        logging.info("Проверка и выполнение запланированных задач.")  # Логирование сообщения
        last_log_time = current_time  # Обновляем время последнего логирования

    schedule.run_pending()  # Выполнение запланированных задач
    time.sleep(1)  # Пауза на 1 секунду

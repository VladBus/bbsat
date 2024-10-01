import schedule
import time
import os
import logging
import subprocess

# Настройка базовой директории для удобства использования абсолютных путей
BASE_DIR = "E:\\Programming_Work\\Pycharm_Work\\bbsat\\"  # Укажите свой путь к проекту

# Настройки
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

# Запланированные задачи
schedule.every().day.at("00:02").do(lambda: run_script(SORT_FILES_PATH))  # Запуск скрипта сортировки
schedule.every().day.at("00:30").do(lambda: run_script(TIFF_COMPRESSOR_PATH))  # Запуск скрипта сжатия
schedule.every().wednesday.at("02:20").do(lambda: run_script(STATISTIC_PATH))  # Запуск скрипта статистики
schedule.every().wednesday.at("02:50").do(lambda: run_script(SEND_MESSAGE_PATH))  # Запуск скрипта отправки сообщений

# Завершение программы в разное время
schedule.every().wednesday.at("03:00").do(lambda: exit(0))  # Завершение работы в среду
schedule.every().day.at("02:25").do(lambda: exit(0))  # Завершение работы в остальные дни


# Функция для запуска скриптов
def run_script(script_path):
    logging.info(f"Проверка существования скрипта: {script_path}")  # Логирование проверку существования

    if not os.path.isfile(script_path):  # Проверка, существует ли файл
        logging.error(f"Скрипт не найден: {script_path}")  # Логирование ошибку, если файл не найден
        return  # Завершение функции, если файла нет

    try:
        logging.info(f"Запуск скрипта: {script_path}")  # Логирование перед запуском скрипта

        # Запись времени начала выполнения скрипта
        start_time = time.time()  # Запоминаем текущее время
        result = subprocess.run(["python", script_path], capture_output=True,
                                text=True)  # Запускаем скрипт и получаем результат

        # Запись времени окончания выполнения скрипта
        end_time = time.time()  # Запоминаем время после выполнения
        execution_time = end_time - start_time  # Вычисляем время выполнения скрипта

        # Проверяем результат выполнения
        if result.returncode == 0:  # Если код завершения равен 0, значит, скрипт выполнен успешно
            logging.info(
                f"Скрипт {script_path} успешно завершён. Время выполнения: {execution_time:.2f} секунд.")  # Лог.успех
            if result.stdout:  # Если есть вывод
                logging.info(f"Вывод: {result.stdout}")  # Логирование вывод скрипта
        else:  # Если код завершения не равен 0, значит, произошла ошибка
            logging.error(
                f"Скрипт {script_path} завершился с ошибкой. Код выхода: {result.returncode}. Ошибка: {result.stderr}. "
                f"Время выполнения: {execution_time:.2f} секунд."  # Логирование ошибку с кодом завершения
            )
    except Exception as e:  # Обработка общего исключения
        logging.error(f"Ошибка при запуске {script_path}: {e}")  # Логирование ошибку запуска


# Бесконечный цикл для выполнения задач
last_log_time = time.time()  # Переменная для отслеживания времени последнего логирования
log_interval = 30  # Интервал логирования в секундах

# Основной цикл, в котором будет выполняться планирование
while True:
    current_time = time.time()  # Текущее время
    if current_time - last_log_time >= log_interval:  # Проверка, прошло ли 30 секунд
        logging.info("Проверка и выполнение запланированных задач.")  # Логирование сообщение о проверке задач
        last_log_time = current_time  # Обновляем время последнего логирования

    schedule.run_pending()  # Выполняем запланированные задачи
    time.sleep(1)  # Пауза на 1 секунду для предотвращения перегрузки процессора

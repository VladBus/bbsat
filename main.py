"""
Модуль для автоматического запуска задач по расписанию:
сортировка файлов, сжатие TIFF и отправка статистики.
"""

import logging
import os
import signal
import subprocess
import sys
import time
from typing import Callable, Optional

import schedule

# Устанавливаем UTF-8 для вывода в консоль (Windows)
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except (AttributeError, UnicodeError):
        pass

# Устанавливаем UTF-8 для логирования по умолчанию
if sys.platform == "win32":
    try:
        # Переопределяем StreamHandler для использования UTF-8
        class UTF8StreamHandler(logging.StreamHandler):  # type: ignore[misc]
            """StreamHandler с принудительной UTF-8 кодировкой."""

            def __init__(self, stream=None):
                super().__init__(stream)
                if self.stream and hasattr(self.stream, "reconfigure"):
                    try:
                        self.stream.reconfigure(encoding="utf-8")
                    except (AttributeError, UnicodeError):
                        pass

        logging.StreamHandler = UTF8StreamHandler  # type: ignore[misc]
    except Exception:  # pylint: disable=broad-exception-caught
        pass

# --- КОНФИГУРАЦИЯ ПУТЕЙ ---
BASE_DIR = r"E:\Programming_Work\VScode_Work\bbsat"
# Новая структура папок согласно твоим изменениям
REPORTS_DIR = r"S:\reports"
LOG_DIR = os.path.join(REPORTS_DIR, "logs")
ARCHIVE_DIR = os.path.join(REPORTS_DIR, "archive_stat")
LOG_FILE = os.path.join(LOG_DIR, "task_log.txt")
PID_FILE = os.path.join(
    LOG_DIR, "bbsat.pid"
)  # Файл для проверки запущенного экземпляра

# Пути к скриптам модулей
CLEANER_PATH = os.path.join(BASE_DIR, "tiff_processing", "tiff_viirs_cleaner.py")
SORT_FILES_PATH = os.path.join(BASE_DIR, "tiff_processing", "sort_files_by_date.py")
TIFF_COMPRESSOR_PATH = os.path.join(BASE_DIR, "tiff_processing", "tiff_compressor.py")
STATISTIC_PATH = os.path.join(BASE_DIR, "week_message", "statistic.py")
SEND_MESSAGE_PATH = os.path.join(BASE_DIR, "week_message", "send_message.py")

# Флаг для корректной остановки планировщика


class SchedulerState:
    """Класс для хранения состояния планировщика."""

    def __init__(self) -> None:
        self.shutdown_requested = False


scheduler_state = SchedulerState()


# --- ПОДГОТОВКА СРЕДЫ ---
def setup_environment() -> None:
    """Создает необходимые директории и настраивает окружение."""
    for folder in [LOG_DIR, ARCHIVE_DIR]:
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
            logging.debug("Создана директория: %s", folder)


def setup_logging() -> None:
    """Настраивает логирование в файл и консоль с UTF-8 кодировкой."""
    # Создаем форматер
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Файловый обработчик с UTF-8 кодировкой (используем codecs для гарантии)
    file_handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Консольный обработчик с UTF-8 кодировкой
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Корневой логер (logger)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


def signal_handler(signum: int, frame: Optional[object]) -> None:  # noqa: N803
    """Обработчик сигналов для корректной остановки."""
    # pylint: disable=unused-argument
    scheduler_state.shutdown_requested = True
    logging.info("Получен сигнал остановки (SIGINT/SIGTERM). Завершение работы...")


# --- ЗАПУСК СКРИПТОВ ---
def run_script(script_path: str) -> bool:
    """
    Безопасный запуск внешних python-скриптов.
    Возвращает True при успехе.
    """
    if not os.path.isfile(script_path):
        logging.error("Файл не найден: %s", script_path)
        return False

    script_name = os.path.basename(script_path)
    python_executable = sys.executable

    try:
        logging.info(">>> СТАРТ: %s", script_name)
        start_t = time.time()

        # Для компрессора подавляем стандартный вывод, чтобы не раздувать лог-файл
        if script_path == TIFF_COMPRESSOR_PATH:
            result = subprocess.run(
                [python_executable, script_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
                timeout=3600,  # Таймаут 1 час для компрессора
            )
        else:
            result = subprocess.run(
                [python_executable, script_path],
                capture_output=True,
                text=True,
                check=False,
                timeout=600,  # Таймаут 10 минут для остальных
            )

        duration = time.time() - start_t

        if result.returncode == 0:
            logging.info(
                "УСПЕХ: %s (время: %.2f сек.)",
                script_name,
                duration,
            )
            # Записываем вывод скрипта (если есть)
            if result.stdout:
                logging.debug("Вывод %s: %s", script_name, result.stdout.strip())
            return True

        logging.error(
            "ОШИБКА в %s (Код: %s): %s",
            script_name,
            result.returncode,
            result.stderr or result.stdout,
        )
        return False

    except subprocess.TimeoutExpired:
        logging.error("ТАЙМАУТ при выполнении %s", script_name)
        return False
    except subprocess.SubprocessError as e:
        logging.error("ОШИБКА ЗАПУСКА %s: %s", script_name, e)
        return False
    except Exception as e:  # pylint: disable=broad-exception-caught
        logging.error("КРИТИЧЕСКИЙ СБОЙ при запуске %s: %s", script_name, e)
        return False


# --- ЗАДАЧИ ПО РАСПИСАНИЮ ---
def create_scheduled_task(script_path: str) -> Callable[[], None]:
    """Создает функцию-обертку для задачи планировщика."""

    def task_wrapper() -> None:
        run_script(script_path)

    return task_wrapper


def setup_schedule() -> None:
    """Настраивает расписание задач."""
    # Каждый день: очистка, сортировка, сжатие и сбор данных
    schedule.every().day.at("00:01").do(create_scheduled_task(CLEANER_PATH))
    schedule.every().day.at("00:05").do(create_scheduled_task(SORT_FILES_PATH))
    schedule.every().day.at("00:30").do(create_scheduled_task(TIFF_COMPRESSOR_PATH))
    schedule.every().day.at("02:25").do(create_scheduled_task(STATISTIC_PATH))

    # Раз в неделю: отправка накопленной статистики
    schedule.every().wednesday.at("02:45").do(create_scheduled_task(SEND_MESSAGE_PATH))

    logging.info(
        "Задачи запланированы: очистка (00:01), сортировка (00:05), "
        "компрессия (00:30), статистика (02:25), отправка (среда 02:45)"
    )


def run_scheduler() -> None:
    """Запускает основной цикл планировщика."""
    logging.info("=== Планировщик BBSAT запущен ===")
    logging.info("Нажмите Ctrl+C для остановки")

    while not scheduler_state.shutdown_requested:
        schedule.run_pending()
        time.sleep(30)

    logging.info("=== Планировщик BBSAT остановлен ===")


def check_another_instance() -> bool:
    """
    Проверяет, запущен ли другой экземпляр планировщика.
    Возвращает True, если уже запущен.
    """
    # Используем logging напрямую, так как logger ещё не инициализирован
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, "r", encoding="utf-8") as f:
                old_pid = f.read().strip()
            # Проверяем, жив ли процесс с этим PID
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {old_pid}", "/FO", "CSV"],
                capture_output=True,
                text=True,
                check=False,
            )
            if old_pid in result.stdout:
                logging.warning("Планировщик уже запущен (PID: %s). Выход.", old_pid)
                return True
        except (OSError, ValueError) as e:
            logging.warning("Ошибка при проверке PID-файла: %s", e)

    # Создаём PID-файл
    try:
        with open(PID_FILE, "w", encoding="utf-8") as f:
            f.write(str(os.getpid()))
        logging.info("PID-файл создан: %s (PID: %d)", PID_FILE, os.getpid())
    except OSError as e:
        logging.warning("Не удалось создать PID-файл: %s", e)

    return False


def cleanup_pid_file() -> None:
    """Удаляет PID-файл при завершении работы."""
    try:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
            logging.info("PID-файл удалён: %s", PID_FILE)
    except OSError as e:
        logging.warning("Не удалось удалить PID-файл: %s", e)


def main() -> int:
    """Точка входа в приложение."""
    setup_environment()
    setup_logging()

    # Проверяем, не запущен ли другой экземпляр (после инициализации логирования)
    if check_another_instance():
        return 1

    # Регистрируем очистку PID-файла при завершении
    import atexit  # pylint: disable=import-outside-toplevel

    atexit.register(cleanup_pid_file)

    # Регистрация обработчиков сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    setup_schedule()
    run_scheduler()

    return 0


if __name__ == "__main__":
    sys.exit(main())

"""
Модуль для умной сортировки спутниковых снимков.
Автоматически определяет дату и тип спутника по имени файла.
"""

import logging
import os
import re
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Константы путей
BASE_ARCHIVE = r"S:\GeoTif"
# Словарь: "Путь к источнику" -> "Имя спутника по умолчанию" (если не нашли в имени)
SOURCE_FOLDERS: Dict[str, str] = {
    r"S:\Products\TERRA": "TERRA",
    r"S:\Products\NOAA": "NOAA",
    r"S:\Products\METOP": "METOP",
    r"S:\Products\VIIRS": "SMART_DETECT",  # Тут будем искать имя в названии
}

# Регулярное выражение для поиска даты (8 цифр подряд: 20260209)
DATE_PATTERN = re.compile(r"(\d{8})")
# Список известных спутников для поиска в именах файлов (папка VIIRS)
KNOWN_SATS = ["NPP", "NOAA20", "NOAA21", "METOP", "TERRA", "AQUA"]

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
)
logger = logging.getLogger(__name__)


def get_dest_path(filename: str, default_sat: str) -> Optional[str]:
    """Определяет путь назначения на основе имени файла."""
    # 1. Ищем дату
    date_match = DATE_PATTERN.search(filename)
    if not date_match:
        logger.debug("Дата не найдена в имени файла: %s", filename)
        return None

    date_str = date_match.group(1)
    try:
        dt = datetime.strptime(date_str, "%Y%m%d")
    except ValueError:
        logger.warning("Некорректная дата %s в файле %s", date_str, filename)
        return None

    # 2. Определяем имя спутника
    sat_name = default_sat
    if default_sat == "SMART_DETECT":
        # Ищем ключевое слово спутника в имени файла (для папки VIIRS)
        sat_name = "OTHER"
        for s in KNOWN_SATS:
            if s in filename.upper():
                sat_name = s
                break
        logger.debug("SMART_DETECT для %s: спутник = %s", filename, sat_name)

    # Строим структуру: S:\GeoTif\2026\02\09-02-2026\NPP
    year = dt.strftime("%Y")
    month = dt.strftime("%m")
    day_folder = dt.strftime("%d-%m-%Y")

    return os.path.join(BASE_ARCHIVE, year, month, day_folder, sat_name)


def move_file(src_file: str, dest_dir: str, filename: str) -> Tuple[bool, str]:
    """Перемещает файл в целевую директорию с обработкой дубликатов."""
    dest_file = os.path.join(dest_dir, filename)

    try:
        # Проверка: если файл с таким именем уже есть, не перезаписываем
        if not os.path.exists(dest_file):
            shutil.move(src_file, dest_file)
            logger.info("Перемещен: %s -> %s", src_file, dest_file)
            return True, "moved"
        else:
            # Если дубликат — удаляем оригинал (файл уже существует в архиве)
            os.remove(src_file)
            logger.info("Дубликат удален (уже существует в архиве): %s", src_file)
            return True, "duplicate_removed"
    except OSError as e:
        logger.error("Ошибка ОС при перемещении %s: %s", filename, e)
        return False, str(e)
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Ошибка при перемещении %s: %s", filename, e)
        return False, str(e)


def process_folder(src_path: str, default_name: str) -> Tuple[int, int]:
    """Обрабатывает одну папку с файлами."""
    if not os.path.exists(src_path):
        logger.warning("Папка не найдена, пропускаю: %s", src_path)
        return 0, 0

    files: List[str] = [
        f for f in os.listdir(src_path) if os.path.isfile(os.path.join(src_path, f))
    ]
    if not files:
        logger.debug("Папка пуста: %s", src_path)
        return 0, 0

    logger.info("Обработка %s (%d файлов)...", src_path, len(files))

    moved_count = 0
    error_count = 0

    for filename in files:
        dest_dir = get_dest_path(filename, default_name)

        if not dest_dir:
            # Если дату не нашли — файл не трогаем (может еще пишется?)
            logger.debug("Пропущен файл (нет даты): %s", filename)
            error_count += 1
            continue

        # Создаем папку если её нет
        if not os.path.exists(dest_dir):
            try:
                os.makedirs(dest_dir, exist_ok=True)
                logger.debug("Создана папка: %s", dest_dir)
            except OSError as e:
                logger.error("Ошибка при создании папки %s: %s", dest_dir, e)
                error_count += 1
                continue

        src_file = os.path.join(src_path, filename)
        success, _ = move_file(src_file, dest_dir, filename)

        if success:
            moved_count += 1
        else:
            error_count += 1

    return moved_count, error_count


def sort_all_data() -> Tuple[int, int]:
    """Основной процесс обхода всех папок."""
    logger.info(
        "--- Запуск сортировки: %s ---",
        datetime.now().strftime("%Y-%m-%d %H:%M"),
    )

    total_moved = 0
    total_errors = 0

    for src_path, default_name in SOURCE_FOLDERS.items():
        moved, errors = process_folder(src_path, default_name)
        total_moved += moved
        total_errors += errors

    logger.info(
        "--- Сортировка завершена. Перемещено: %d, Ошибок: %d ---",
        total_moved,
        total_errors,
    )

    return total_moved, total_errors


if __name__ == "__main__":
    sort_all_data()

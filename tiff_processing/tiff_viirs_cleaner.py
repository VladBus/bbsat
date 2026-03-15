"""
Модуль для очистки всех спутниковых директорий от мелких "битых" файлов.
Файлы меньше 200 КБ перемещаются в локальную корзину.
"""

import logging
import os
import shutil
from datetime import datetime

# --- КОНСТАНТЫ ПУТЕЙ ---
# Базовая директория, где лежат папки спутников
BASE_PRODUCTS_PATH = r"S:\Products"

# Список папок для очистки (согласно твоему скриншоту edited-image.png)
SATELLITE_FOLDERS = ["METOP", "NOAA", "TERRA", "VIIRS"]

# Локальная корзина на диске D
TRASH_BASE = r"D:\temp_trash"

# Порог размера файла в КБ
SIZE_THRESHOLD_KB = 200

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
)
logger = logging.getLogger(__name__)


def ensure_trash_exists() -> str:
    """Создает папку корзины с подпапкой текущего месяца."""
    current_month = datetime.now().strftime("%Y-%m")
    trash_path = os.path.join(TRASH_BASE, current_month)
    if not os.path.exists(trash_path):
        os.makedirs(trash_path, exist_ok=True)
    return trash_path


def get_unique_dest_path(dest_dir: str, filename: str) -> str:
    """Возвращает уникальный путь для файла, добавляя метку времени при коллизии."""
    dest_path = os.path.join(dest_dir, filename)

    if not os.path.exists(dest_path):
        return dest_path

    # Если файл уже существует, добавляем timestamp и индекс
    name, ext = os.path.splitext(filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    counter = 0

    while True:
        if counter == 0:
            new_filename = f"{name}_{timestamp}{ext}"
        else:
            new_filename = f"{name}_{timestamp}_{counter}{ext}"

        dest_path = os.path.join(dest_dir, new_filename)
        if not os.path.exists(dest_path):
            return dest_path
        counter += 1


def clean_folder(folder_path: str, trash_dir: str) -> int:
    """Рекурсивно чистит конкретную папку от файлов < 200 КБ."""
    count = 0
    errors = 0

    if not os.path.exists(folder_path):
        logger.warning("Пропуск: Папка не найдена %s", folder_path)
        return 0

    for root, _, files in os.walk(folder_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            try:
                file_size_kb = os.path.getsize(file_path) / 1024

                if file_size_kb < SIZE_THRESHOLD_KB:
                    dest_path = get_unique_dest_path(trash_dir, filename)
                    shutil.move(file_path, dest_path)
                    logger.info(
                        "Перемещен: %s -> %s (%.1f КБ)",
                        file_path,
                        dest_path,
                        file_size_kb,
                    )
                    count += 1
            except OSError as e:
                logger.error("Ошибка ОС при обработке %s: %s", filename, e)
                errors += 1
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error("Ошибка при обработке %s: %s", filename, e)
                errors += 1

    if errors > 0:
        logger.warning("Всего ошибок при очистке %s: %d", folder_path, errors)

    return count


def main() -> None:
    """Основная функция очистки."""
    logger.info(
        "--- Старт глобальной очистки %s (порог %d КБ) ---",
        BASE_PRODUCTS_PATH,
        SIZE_THRESHOLD_KB,
    )

    current_trash = ensure_trash_exists()
    total_moved = 0

    for sat in SATELLITE_FOLDERS:
        full_path = os.path.join(BASE_PRODUCTS_PATH, sat)
        logger.info("Сканирую %s...", sat)
        moved = clean_folder(full_path, current_trash)
        logger.info("-> Удалено из %s: %d шт.", sat, moved)
        total_moved += moved

    logger.info(
        "--- Очистка завершена. Всего перемещено в корзину: %d ---", total_moved
    )


if __name__ == "__main__":
    main()

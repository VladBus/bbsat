"""
Модуль для очистки всех спутниковых директорий от мелких "битых" файлов.
Файлы меньше 200 КБ перемещаются в локальную корзину.
"""

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


def ensure_trash_exists():
    """Создает папку корзины с подпапкой текущего месяца."""
    current_month = datetime.now().strftime("%Y-%m")
    trash_path = os.path.join(TRASH_BASE, current_month)
    if not os.path.exists(trash_path):
        os.makedirs(trash_path)
    return trash_path


def clean_folder(folder_path, trash_dir):
    """Рекурсивно чистит конкретную папку от файлов < 200 КБ."""
    count = 0
    SIZE_THRESHOLD_KB = 200

    if not os.path.exists(folder_path):
        print(f"Пропуск: Папка не найдена {folder_path}")
        return 0

    for root, _, files in os.walk(folder_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            try:
                file_size_kb = os.path.getsize(file_path) / 1024

                if file_size_kb < SIZE_THRESHOLD_KB:
                    dest_path = os.path.join(trash_dir, filename)

                    # Если файл с таким именем уже есть в корзине, добавим метку
                    if os.path.exists(dest_path):
                        timestamp = datetime.now().strftime("%H%M%S")
                        name, ext = os.path.splitext(filename)
                        dest_path = os.path.join(trash_dir, f"{name}_{timestamp}{ext}")

                    shutil.move(file_path, dest_path)
                    count += 1
            except Exception as e:
                print(f"Ошибка при обработке {filename}: {e}")
    return count


if __name__ == "__main__":
    print(f"--- Старт глобальной очистки S:\\Products (порог 200 КБ) ---")

    current_trash = ensure_trash_exists()
    total_moved = 0

    for sat in SATELLITE_FOLDERS:
        full_path = os.path.join(BASE_PRODUCTS_PATH, sat)
        print(f"Сканирую {sat}...")
        moved = clean_folder(full_path, current_trash)
        print(f"-> Удалено из {sat}: {moved} шт.")
        total_moved += moved

    print(f"--- Очистка завершена. Всего перемещено в корзину: {total_moved} ---")

"""
Модуль для умной сортировки спутниковых снимков.
Автоматически определяет дату и тип спутника по имени файла.
"""

import os
import re
import shutil
from datetime import datetime

# Константы путей
BASE_ARCHIVE = r"S:\GeoTif"
# Словарь: "Путь к источнику" -> "Имя спутника по умолчанию" (если не нашли в имени)
SOURCE_FOLDERS = {
    r"S:\Products\TERRA": "TERRA",
    r"S:\Products\NOAA": "NOAA",
    r"S:\Products\METOP": "METOP",
    r"S:\Products\VIIRS": "SMART_DETECT",  # Тут будем искать имя в названии
}

# Регулярное выражение для поиска даты (8 цифр подряд: 20260209)
DATE_PATTERN = re.compile(r"(\d{8})")
# Список известных спутников для поиска в именах файлов (папка VIIRS)
KNOWN_SATS = ["NPP", "NOAA20", "NOAA21", "METOP", "TERRA", "AQUA"]


def get_dest_path(filename, default_sat):
    """Определяет путь назначения на основе имени файла."""
    # 1. Ищем дату
    date_match = DATE_PATTERN.search(filename)
    if not date_match:
        return None

    date_str = date_match.group(1)
    try:
        dt = datetime.strptime(date_str, "%Y%m%d")
    except ValueError:
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

    # Строим структуру: S:\GeoTif\2026\02\09-02-2026\NPP
    year = dt.strftime("%Y")
    month = dt.strftime("%m")
    day_folder = dt.strftime("%d-%m-%Y")

    return os.path.join(BASE_ARCHIVE, year, month, day_folder, sat_name)


def sort_all_data():
    """Основной процесс обхода всех папок."""
    print(f"--- Запуск сортировки: {datetime.now().strftime('%Y-%m-%d %H:%M')} ---")

    for src_path, default_name in SOURCE_FOLDERS.items():
        if not os.path.exists(src_path):
            print(f"Папка не найдена, пропускаю: {src_path}")
            continue

        files = [
            f for f in os.listdir(src_path) if os.path.isfile(os.path.join(src_path, f))
        ]
        if not files:
            continue

        print(f"Обработка {src_path} ({len(files)} файлов)...")

        for filename in files:
            dest_dir = get_dest_path(filename, default_name)

            if not dest_dir:
                # Если дату не нашли — файл не трогаем (может еще пишется?)
                continue

            # Создаем папку если её нет
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)

            src_file = os.path.join(src_path, filename)
            dest_file = os.path.join(dest_dir, filename)

            try:
                # Проверка: если файл с таким именем уже есть, не перезаписываем
                if not os.path.exists(dest_file):
                    shutil.move(src_file, dest_file)
                else:
                    # Если дубликат — можно добавить префикс или удалить оригинал
                    os.remove(src_file)
            except Exception as e:  # pylint: disable=broad-exception-caught
                print(f"Ошибка при перемещении {filename}: {e}")

    print("--- Сортировка завершена ---")


if __name__ == "__main__":
    sort_all_data()

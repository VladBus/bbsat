"""
Модуль для сортировки спутниковых снимков по структурированным папкам.
Распределяет файлы из входных директорий в архив по схеме: Год/Месяц/День/Спутник.
"""

import os
import shutil
from datetime import datetime, timedelta

# Константы путей (UPPER_CASE)
BASE_FOLDER = r"S:\GeoTif"
TERRA_FOLDER = r"S:\Products\TERRA"
NOAA_FOLDER = r"S:\Products\NOAA"
METOP_FOLDER = r"S:\Products\METOP"

# Текущая дата
NOW_TIME = datetime.today()
NOW_DATE = NOW_TIME.date()


def ensure_folder_exists(path_folder):
    """Проверяет наличие папки, если её нет — создает."""
    if not os.path.exists(path_folder):
        os.makedirs(path_folder)
        print(f"Папка создана: {path_folder}")


def move_files(source_folder, files_list, dest_folder):
    """Перемещает файлы из списка в целевую папку."""
    for filename in files_list:
        source_path = os.path.join(source_folder, filename)
        dest_path = os.path.join(dest_folder, filename)
        try:
            shutil.move(source_path, dest_path)
        except OSError as err:
            print(f"Ошибка при перемещении {filename}: {err}")


def get_date_folder_names(initial_date):
    """Возвращает год, месяц и дату для структуры папок."""
    year = initial_date.strftime("%Y")
    month = initial_date.strftime("%m")
    day_folder = initial_date.strftime("%d-%m-%Y")
    return year, month, day_folder


def filter_and_move_files(sat_folder, ini_date, sat_name, base_dest_folder):
    """
    Фильтрует файлы по дате в названии и перемещает их в архив.
    """
    if not os.path.exists(sat_folder):
        print(f"Исходная папка не найдена: {sat_folder}")
        return

    sat_flist = os.listdir(sat_folder)
    current_date = ini_date

    while sat_flist:
        filtered_list = []
        date_mask = current_date.strftime("%Y%m%d")

        # Фильтрация
        for filename in sat_flist:
            if date_mask in filename:
                filtered_list.append(filename)

        if filtered_list:
            year, month, day = get_date_folder_names(current_date)

            # Формируем путь: S:\GeoTif\2024\05\20-05-2024\METOP
            dest_path = os.path.join(base_dest_folder, year, month, day, sat_name)

            ensure_folder_exists(dest_path)
            move_files(sat_folder, filtered_list, dest_path)

            # Обновляем список (исключаем перемещенные файлы)
            sat_flist = list(set(sat_flist) - set(filtered_list))
            print(f"Перемещено {len(filtered_list)} файлов в {dest_path}")

        # Если в папке еще остались файлы, пробуем дату на день раньше
        if sat_flist:
            current_date -= timedelta(days=1)
            # Предохранитель: если мы ушли слишком далеко в прошлое (например, на год)
            if (ini_date - current_date).days > 365:
                print(f"Прекращение поиска для {sat_name}: файлы старше года.")
                break
        else:
            break


if __name__ == "__main__":
    print(f"Запуск сортировки. Сегодня: {NOW_DATE}")

    # Запуск для каждого типа спутников
    filter_and_move_files(METOP_FOLDER, NOW_DATE, "METOP", BASE_FOLDER)
    filter_and_move_files(NOAA_FOLDER, NOW_DATE, "NOAA", BASE_FOLDER)
    filter_and_move_files(TERRA_FOLDER, NOW_DATE, "TERRA", BASE_FOLDER)

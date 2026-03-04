"""
Модуль для очистки директории от мелких файлов.
Файлы размером меньше 5 МБ перемещаются в папку временного хранения.
"""

import os
import shutil

# Константы (в верхнем регистре согласно PEP 8)
WORKING_FOLDER = r"R:\2023"
TRASH_FOLDER = r"D:\temp"

# Меняем рабочую директорию
if os.path.exists(WORKING_FOLDER):
    os.chdir(WORKING_FOLDER)


def list_files(filepath):
    """Рекурсивно собирает полные пути всех файлов в указанной директории."""
    paths = []
    for root, _, files in os.walk(filepath):  # Заменили dirs на _
        for filename in files:
            paths.append(os.path.join(root, filename))
    return paths


def clean_small_files(f_list):
    """
    Проверяет размер файлов из списка.
    Если файл меньше 5120 КБ (5 МБ), перемещает его в TRASH_FOLDER.
    """
    # Убрали неиспользуемую переменную files2clean
    for file_path in f_list:
        if not os.path.exists(file_path):
            continue

        file_size = os.path.getsize(file_path) / 1024
        # Используем basename вместо split для получения имени файла
        filename = os.path.basename(file_path)

        if file_size < 5120:
            dest_path = os.path.join(TRASH_FOLDER, filename)
            print(f"Moving to trash: {dest_path}")
            shutil.move(file_path, dest_path)


if __name__ == "__main__":
    # Сначала проверяем, существует ли папка с корзиной
    if not os.path.exists(TRASH_FOLDER):
        os.makedirs(TRASH_FOLDER)

    # Получаем список файлов и запускаем очистку
    all_files = list_files(WORKING_FOLDER)
    clean_small_files(all_files)

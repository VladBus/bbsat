"""
Модуль для компрессии GeoTIFF файлов с использованием GDAL.
Проверяет размер полученного файла и удаляет исходники.
"""

import os

# Пути к папкам
PRODUCTS_BBSAT = r"S:\GeoTif"
TRASH_FOLDER = r"S:\trash"
COMMAND = "gdal_translate -of Gtiff -co COMPRESS=LZW {input} {output}"

os.chdir(PRODUCTS_BBSAT)


def list_files(filepath):
    """Рекурсивно ищет все файлы .geotiff.tif в указанной директории."""
    paths = []
    for root, _, files in os.walk(filepath):  # Заменили dirs на _
        for filename in files:  # Переименовали во избежание конфликта имен
            if filename.endswith(".geotiff.tif"):
                paths.append(os.path.join(root, filename))
    return paths


def compressor(file_ini):
    """Сжимает файл с помощью gdal_translate и возвращает путь к новому файлу."""
    # Более надежное получение пути без расширения
    base_path = os.path.splitext(os.path.splitext(file_ini)[0])[0]
    output_file = base_path + ".tif"
    os.system(COMMAND.format(input=file_ini, output=output_file))
    return output_file


def tif_size(tif_file):
    """Возвращает размер файла в килобайтах."""
    return os.path.getsize(tif_file) / 1024


def file_filter(ini_file, compressed_file):
    """Сравнивает размеры файлов и удаляет сжатый, если он подозрительно мал."""
    big_tif_size = tif_size(ini_file)
    small_tif_size = tif_size(compressed_file)

    if small_tif_size <= big_tif_size * 0.2:
        print(
            f"File size {compressed_file} is too small, it can be deleted:\n"
            f"Size: {small_tif_size:.2f} KB"
        )
        os.remove(compressed_file)
    else:
        print(f"File size for {compressed_file}:\n {small_tif_size:.2f} KB")


# Получаем список файлов один раз
FILES_TO_PROCESS = list_files(PRODUCTS_BBSAT)

if __name__ == "__main__":
    for file_path in FILES_TO_PROCESS:
        try:
            light_file = compressor(file_path)
            file_filter(file_path, light_file)
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        finally:
            # Будь осторожен: оригинальный файл удаляется в любом случае
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"File {file_path} is moved to trash (deleted)")

# Пример для проверки (закомментирован для соответствия лимиту длины строки):
# os.system(f"gdal_translate.exe -of Gtiff -co COMPRESS=LZW {file1} {file2}")

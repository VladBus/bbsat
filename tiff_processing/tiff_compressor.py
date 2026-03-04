"""
Модуль для компрессии GeoTIFF файлов с использованием GDAL.
Сжимает файлы в LZW и удаляет исходники только при успехе.
"""

import os

# Пути к папкам
PRODUCTS_BBSAT = r"S:\GeoTif"
COMMAND = 'gdal_translate -of Gtiff -co COMPRESS=LZW "{input}" "{output}"'


def list_files(filepath):
    """Рекурсивно ищет файлы .geotiff.tif, .geotiff и .tiff."""
    paths = []
    # Важно искать файлы, которые еще НЕ сжаты (чтобы не сжимать по кругу .tif)
    valid_extensions = (".geotiff.tif", ".geotiff", ".tiff")
    for root, _, files in os.walk(filepath):
        for filename in files:
            if filename.lower().endswith(valid_extensions):
                paths.append(os.path.join(root, filename))
    return paths


def get_size_kb(file_path):
    """Возвращает размер файла в килобайтах."""
    return os.path.getsize(file_path) / 1024


def compress_file(input_path):
    """Сжимает файл и возвращает путь к результату или None при ошибке."""
    # Получаем путь без расширений (поддерживает сложные точки в именах)
    # Например: image.geotiff.tif -> image
    base_path = input_path
    while any(base_path.lower().endswith(ext) for ext in [".tif", ".geotiff", ".tiff"]):
        base_path = os.path.splitext(base_path)[0]

    output_path = base_path + ".tif"

    # Если имя совпадает с оригиналом (уже .tif), создаем временное имя
    temp_mode = False
    if input_path.lower() == output_path.lower():
        output_path = base_path + "_tmp.tif"
        temp_mode = True

    print(f"Сжатие: {os.path.basename(input_path)} -> {os.path.basename(output_path)}")

    # Запуск GDAL
    result = os.system(COMMAND.format(input=input_path, output=output_path))

    if result == 0 and os.path.exists(output_path):
        return output_path, temp_mode

    print(f"Ошибка GDAL при обработке {input_path}")
    return None, False


def process_all_tiffs():
    """Основной цикл обработки."""
    files = list_files(PRODUCTS_BBSAT)
    if not files:
        print("Нет файлов для компрессии.")
        return

    for file_path in files:
        original_size = get_size_kb(file_path)
        compressed_path, is_temp = compress_file(file_path)

        if not compressed_path:
            continue

        new_size = get_size_kb(compressed_path)

        # Проверка: если файл сжался слишком сильно (пустой) или GDAL выдал мусор
        if new_size <= original_size * 0.05:  # Порог 5% (для LZW это критично мало)
            print(
                f"ВНИМАНИЕ: Файл {compressed_path} подозрительно мал. Удаляю результат."
            )
            os.remove(compressed_path)
        else:
            # Успех: удаляем оригинал
            os.remove(file_path)

            # Если использовали временное имя, переименовываем в финальное
            if is_temp:
                final_path = compressed_path.replace("_tmp.tif", ".tif")
                if os.path.exists(final_path):
                    os.remove(final_path)
                os.rename(compressed_path, final_path)

            print(f"Готово: {original_size:.1f}KB -> {new_size:.1f}KB")


if __name__ == "__main__":
    process_all_tiffs()

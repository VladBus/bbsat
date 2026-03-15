"""
Модуль для компрессии GeoTIFF файлов с использованием GDAL.
Сжимает файлы в LZW и удаляет исходники только при успехе.
"""

import logging
import os
import shutil
import subprocess
from typing import List, Optional, Tuple

# Пути к папкам
PRODUCTS_BBSAT = r"S:\GeoTif"
COMMAND = 'gdal_translate -of Gtiff -co COMPRESS=LZW "{input}" "{output}"'

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
)
logger = logging.getLogger(__name__)


def list_files(filepath: str) -> List[str]:
    """Рекурсивно ищет файлы .geotiff.tif, .geotiff и .tiff."""
    paths: List[str] = []
    # Важно искать файлы, которые еще НЕ сжаты (чтобы не сжимать по кругу .tif)
    valid_extensions = (".geotiff.tif", ".geotiff", ".tiff")
    for root, _, files in os.walk(filepath):
        for filename in files:
            if filename.lower().endswith(valid_extensions):
                paths.append(os.path.join(root, filename))
    return paths


def get_size_kb(file_path: str) -> float:
    """Возвращает размер файла в килобайтах."""
    return os.path.getsize(file_path) / 1024


def get_output_path(input_path: str) -> Tuple[str, bool]:
    """
    Определяет путь для выходного файла.
    Возвращает (путь, is_temp) - путь и флаг временного режима.
    """
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

    return output_path, temp_mode


def compress_file(input_path: str) -> Optional[Tuple[str, bool]]:
    """
    Сжимает файл и возвращает путь к результату или None при ошибке.
    Возвращает (путь_к_сжатому_файлу, is_temp).
    """
    output_path, is_temp = get_output_path(input_path)

    logger.info(
        "Сжатие: %s -> %s",
        os.path.basename(input_path),
        os.path.basename(output_path),
    )

    # Проверка наличия gdal_translate
    if shutil.which("gdal_translate") is None:
        logger.error("GDAL не найден (gdal_translate не в PATH)")
        return None

    try:
        # Запуск GDAL через subprocess для лучшего контроля
        result = subprocess.run(
            COMMAND.format(input=input_path, output=output_path),
            shell=True,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0 and os.path.exists(output_path):
            return output_path, is_temp

        logger.error(
            "Ошибка GDAL при обработке %s: %s",
            input_path,
            result.stderr.strip() if result.stderr else "неизвестная ошибка",
        )
        return None
    except subprocess.SubprocessError as e:
        logger.error("Ошибка запуска GDAL для %s: %s", input_path, e)
        return None
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Неожиданная ошибка при сжатии %s: %s", input_path, e)
        return None


def finalize_file(compressed_path: str, is_temp: bool, original_path: str) -> bool:
    """
    Завершает обработку файла: удаляет оригинал и переименовывает временный файл.
    """
    try:
        # Удаляем оригинал
        os.remove(original_path)
        logger.debug("Удален оригинал: %s", original_path)

        # Если использовали временное имя, переименовываем в финальное
        if is_temp:
            final_path = compressed_path.replace("_tmp.tif", ".tif")
            if os.path.exists(final_path):
                os.remove(final_path)
                logger.debug("Удален существующий финальный файл: %s", final_path)
            os.rename(compressed_path, final_path)
            logger.debug("Переименован %s -> %s", compressed_path, final_path)

        return True
    except OSError as e:
        logger.error("Ошибка при завершении обработки файла: %s", e)
        return False


def process_all_tiffs() -> Tuple[int, int, int]:
    """
    Основной цикл обработки.
    Возвращает (успешно, ошибок, пропущено).
    """
    files = list_files(PRODUCTS_BBSAT)
    if not files:
        logger.info("Нет файлов для компрессии в %s", PRODUCTS_BBSAT)
        return 0, 0, 0

    logger.info("Найдено файлов для компрессии: %d", len(files))

    success_count = 0
    error_count = 0
    skipped_count = 0

    for file_path in files:
        try:
            original_size = get_size_kb(file_path)
        except OSError as e:
            logger.error("Не удалось получить размер файла %s: %s", file_path, e)
            error_count += 1
            continue

        compression_result = compress_file(file_path)

        if not compression_result:
            error_count += 1
            continue

        compressed_path, is_temp = compression_result

        try:
            new_size = get_size_kb(compressed_path)
        except OSError as e:
            logger.error(
                "Не удалось получить размер сжатого файла %s: %s",
                compressed_path,
                e,
            )
            error_count += 1
            continue

        # Проверка: если файл сжался слишком сильно (пустой) или GDAL выдал мусор
        if new_size <= original_size * 0.05:  # Порог 5% (для LZW это критично мало)
            logger.warning(
                "ВНИМАНИЕ: Файл %s подозрительно мал (%.1f КБ -> %.1f КБ). "
                "Удаляю результат.",
                compressed_path,
                original_size,
                new_size,
            )
            try:
                os.remove(compressed_path)
            except OSError:
                pass
            error_count += 1
            continue

        # Успех: завершаем обработку
        if finalize_file(compressed_path, is_temp, file_path):
            logger.info(
                "Готово: %.1f КБ -> %.1f КБ (%.1f%%)",
                original_size,
                new_size,
                (new_size / original_size) * 100 if original_size > 0 else 0,
            )
            success_count += 1
        else:
            error_count += 1

    return success_count, error_count, skipped_count


def main() -> None:
    """Точка входа."""
    logger.info("--- Запуск компрессии GeoTIFF ---")
    success, errors, skipped = process_all_tiffs()
    logger.info(
        "--- Компрессия завершена. Успешно: %d, Ошибок: %d, Пропущено: %d ---",
        success,
        errors,
        skipped,
    )


if __name__ == "__main__":
    main()

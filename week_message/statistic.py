"""
Модуль для сбора статистики по спутниковым данным.
Подсчитывает файлы .tif (GeoTif) и .trk (траектории) за определенный период
и формирует текстовый отчет.
"""

import logging
import os
import re
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import DefaultDict, Dict, List

# Глобальные константы (UPPER_CASE)
TODAY = datetime.today()
END_DATE_PERIOD = TODAY.date() - timedelta(days=1)
START_DATE_PERIOD = END_DATE_PERIOD - timedelta(days=6)
DIRECTORY_PATH_GEOTIF = r"S:\GeoTif"
DIRECTORY_PATH_TRK = r"S:\trk"
MESSAGE_PATH = r"S:\reports\archive_stat"

# Список спутников, которые мы хотим видеть в итоговом FTP-отчете
TARGET_SATS = ["METOP", "TERRA", "NOAA", "NPP", "NOAA20", "NOAA21"]

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
)
logger = logging.getLogger(__name__)


def count_files_by_satellite(
    directory: str, start_dt: date, end_dt: date
) -> Dict[str, int]:
    """Считает количество файлов .tif по спутникам в структуре архива."""
    file_counts: Dict[str, int] = defaultdict(int)  # type: ignore[assignment]

    if not os.path.exists(directory):
        logger.warning("Директория не найдена: %s", directory)
        return dict(file_counts)

    for root, _, _ in os.walk(directory):
        folder_date_str = os.path.basename(root)
        try:
            folder_date = datetime.strptime(folder_date_str, "%d-%m-%Y").date()
        except ValueError:
            continue

        if start_dt <= folder_date <= end_dt:
            # Проверяем подпапки каждого спутника внутри даты
            for satellite in TARGET_SATS:
                satellite_path = os.path.join(root, satellite)
                if os.path.exists(satellite_path):
                    tifs = [
                        f
                        for f in os.listdir(satellite_path)
                        if f.lower().endswith(".tif")
                    ]
                    file_counts[satellite] += len(tifs)

    logger.info(
        "Подсчитано файлов GeoTIF за %s - %s: %s",
        start_dt.strftime("%d.%m.%Y"),
        end_dt.strftime("%d.%m.%Y"),
        dict(file_counts),
    )
    return dict(file_counts)


def count_files_by_station(
    directory: str, start_dt: date, end_dt: date
) -> DefaultDict[str, Dict[str, int]]:
    """Считает количество файлов .trk по спутникам и станциям из имен файлов."""
    file_counts: DefaultDict[str, Dict[str, int]] = defaultdict(
        lambda: defaultdict(int)  # type: ignore[return-value]
    )

    # Универсальная регулярка: Группа 1 (Спутник), Группа 3-5 (Дата), Группа 7 (Станция)
    regex = r"([A-Z0-9_]+)_(\d{5})_(\d{4})(\d{2})(\d{2})_(\d{6})_(BG\d+)\.trk"

    if not os.path.exists(directory):
        logger.warning("Директория не найдена: %s", directory)
        return file_counts

    matched_count = 0
    for _, _, files in os.walk(directory):
        for filename in files:
            match = re.match(regex, filename)
            if match:
                satellite = match.group(1)
                date_str = match.group(3) + match.group(4) + match.group(5)
                try:
                    file_dt = datetime.strptime(date_str, "%Y%m%d").date()
                except ValueError:
                    logger.warning("Некорректная дата в имени файла: %s", filename)
                    continue

                if start_dt <= file_dt <= end_dt:
                    station_id = match.group(7)
                    file_counts[station_id][satellite] += 1
                    matched_count += 1

    logger.info(
        "Подсчитано файлов TRK за %s - %s: найдено %d совпадений",
        start_dt.strftime("%d.%m.%Y"),
        end_dt.strftime("%d.%m.%Y"),
        matched_count,
    )
    return file_counts


def generate_report(
    counts_geotif: Dict[str, int], counts_trk: DefaultDict[str, Dict[str, int]]
) -> str:
    """Формирует итоговый текст отчета."""
    header = (
        f"Обновленные цифры за {START_DATE_PERIOD.strftime('%d.%m.%Y')} г. - "
        f"{END_DATE_PERIOD.strftime('%d.%m.%Y')} г.\n\n"
    )
    body_parts: List[str] = []

    # 1. Данные по станциям (.trk)
    # Сортируем станции по имени (BG1, BG2...)
    for station in sorted(counts_trk.keys()):
        satellite_counts = counts_trk[station]
        # Для отчета: BG2 -> 3.2. Станция BG-2
        st_num = station.replace("BG", "")
        station_header = f"3.{st_num}. Станция BG-{st_num} приняла:\n"
        body_parts.append(station_header)

        for satellite in sorted(satellite_counts.keys()):
            count = satellite_counts[satellite]
            body_parts.append(f"{satellite:10} - {count}\n")
        body_parts.append("\n")

    # 2. Данные по спутникам (.tif) для FTP
    body_parts.append("\nДля отправки по FTP было подготовлено:\n\n")
    for satellite in TARGET_SATS:
        count = counts_geotif.get(satellite, 0)
        body_parts.append(f"{count:>4} tif-файлов спутников {satellite}\n")

    return header + "".join(body_parts)


def save_report(report_text: str, report_path: str) -> bool:
    """Сохраняет отчет в файл."""
    try:
        report_dir = os.path.dirname(report_path)
        if report_dir and not os.path.exists(report_dir):
            os.makedirs(report_dir, exist_ok=True)

        with open(report_path, "w", encoding="utf-8") as out_file:
            out_file.write(report_text)

        logger.info("Отчет успешно создан: %s", report_path)
        return True
    except OSError as e:
        logger.error("Ошибка при записи отчета: %s", e)
        return False


def main() -> bool:
    """Основная функция сбора статистики."""
    logger.info("Сбор статистики...")

    data_trk = count_files_by_station(
        DIRECTORY_PATH_TRK, START_DATE_PERIOD, END_DATE_PERIOD
    )
    data_geotif = count_files_by_satellite(
        DIRECTORY_PATH_GEOTIF, START_DATE_PERIOD, END_DATE_PERIOD
    )

    final_report = generate_report(data_geotif, data_trk)

    # Сохранение в файл
    report_filename = f'Satellite_data_{TODAY.strftime("%d-%m-%Y")}.txt'
    report_path = os.path.join(MESSAGE_PATH, report_filename)

    return save_report(final_report, report_path)


if __name__ == "__main__":
    is_success = main()  # pylint: disable=invalid-name
    sys.exit(0 if is_success else 1)

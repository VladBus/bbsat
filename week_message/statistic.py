"""
Модуль для сбора статистики по спутниковым данным.
Подсчитывает файлы .tif (GeoTif) и .trk (траектории) за определенный период
и формирует текстовый отчет.
"""

import os
import re
from collections import defaultdict
from datetime import datetime, timedelta

# Глобальные константы (UPPER_CASE)
TODAY = datetime.today()
END_DATE_PERIOD = TODAY.date() - timedelta(days=1)
START_DATE_PERIOD = END_DATE_PERIOD - timedelta(days=6)
DIRECTORY_PATH_GEOTIF = r"S:\GeoTif"
DIRECTORY_PATH_TRK = r"S:\trk"
MESSAGE_PATH = r"S:\reports\archive_stat"

# Список спутников, которые мы хотим видеть в итоговом FTP-отчете
TARGET_SATS = ["METOP", "TERRA", "NOAA", "NPP", "NOAA20", "NOAA21"]


def count_files_by_satellite(directory, start_dt, end_dt):
    """Считает количество файлов .tif по спутникам в структуре архива."""
    file_counts = defaultdict(int)

    if not os.path.exists(directory):
        return file_counts

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
    return file_counts


def count_files_by_station(directory, start_dt, end_dt):
    """Считает количество файлов .trk по спутникам и станциям из имен файлов."""
    file_counts = defaultdict(lambda: defaultdict(int))

    # Универсальная регулярка: Группа 1 (Спутник), Группа 3-5 (Дата), Группа 7 (Станция)
    regex = r"([A-Z0-9_]+)_(\d{5})_(\d{4})(\d{2})(\d{2})_(\d{6})_(BG\d+).trk"

    if not os.path.exists(directory):
        return file_counts

    for _, _, files in os.walk(directory):
        for filename in files:
            match = re.match(regex, filename)
            if match:
                satellite = match.group(1)
                date_str = match.group(3) + match.group(4) + match.group(5)
                try:
                    file_dt = datetime.strptime(date_str, "%Y%m%d").date()
                except ValueError:
                    continue

                if start_dt <= file_dt <= end_dt:
                    station_id = match.group(7)
                    file_counts[station_id][satellite] += 1
    return file_counts


def generate_report(counts_geotif, counts_trk):
    """Формирует итоговый текст отчета."""
    header = (
        f"Обновленные цифры за {START_DATE_PERIOD.strftime('%d.%m.%Y')} г. - "
        f"{END_DATE_PERIOD.strftime('%d.%m.%Y')} г.\n\n"
    )
    body = ""

    # 1. Данные по станциям (.trk)
    # Сортируем станции по имени (BG1, BG2...)
    for station in sorted(counts_trk.keys()):
        satellite_counts = counts_trk[station]
        # Для отчета: BG2 -> 3.2. Станция BG-2
        st_num = station.replace("BG", "")
        body += f"3.{st_num}. Станция BG-{st_num} приняла:\n"

        for satellite in sorted(satellite_counts.keys()):
            count = satellite_counts[satellite]
            body += f"{satellite:10} - {count}\n"
        body += "\n"

    # 2. Данные по спутникам (.tif) для FTP
    body += "\nДля отправки по FTP было подготовлено:\n\n"
    for satellite in TARGET_SATS:
        count = counts_geotif.get(satellite, 0)
        body += f"{count:>4} tif-файлов спутников {satellite}\n"

    return header + body


if __name__ == "__main__":
    print("Сбор статистики...")

    DATA_TRK = count_files_by_station(
        DIRECTORY_PATH_TRK, START_DATE_PERIOD, END_DATE_PERIOD
    )
    DATA_GEOTIF = count_files_by_satellite(
        DIRECTORY_PATH_GEOTIF, START_DATE_PERIOD, END_DATE_PERIOD
    )

    FINAL_REPORT = generate_report(DATA_GEOTIF, DATA_TRK)

    # Сохранение в файл
    REPORT_FILENAME = f'Satellite_data_{TODAY.strftime("%d-%m-%Y")}.txt'
    REPORT_PATH = os.path.join(MESSAGE_PATH, REPORT_FILENAME)

    if not os.path.exists(MESSAGE_PATH):
        os.makedirs(MESSAGE_PATH)

    with open(REPORT_PATH, "w", encoding="utf-8") as out_file:
        out_file.write(FINAL_REPORT)

    print(f"Отчет успешно создан: {REPORT_PATH}")

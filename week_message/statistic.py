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
MESSAGE_PATH = r"S:\message"


def count_files_by_satellite(directory, start_dt, end_dt):
    """
    Считает количество файлов .tif по спутникам в папках с заданными датами.
    """
    file_counts = defaultdict(int)

    for root, _, _ in os.walk(directory):  # Убрали неиспользуемые dirs и files
        # Получаем дату из названия папки (последний уровень)
        folder_date_str = os.path.basename(root)
        try:
            folder_date = datetime.strptime(folder_date_str, "%d-%m-%Y").date()
        except ValueError:
            continue

        if start_dt <= folder_date <= end_dt:
            for satellite in ["METOP", "TERRA", "NOAA", "NPP"]:
                satellite_path = os.path.join(root, satellite)
                if os.path.exists(satellite_path):
                    for filename in os.listdir(satellite_path):
                        if filename.endswith(".tif"):
                            file_counts[satellite] += 1
                else:
                    # Инициализируем нулем, если папки нет
                    if satellite not in file_counts:
                        file_counts[satellite] = 0
    return file_counts


def count_files_by_station(directory, start_dt, end_dt):
    """
    Считает количество файлов .trk по спутникам, анализируя имена файлов.
    """
    file_counts = defaultdict(lambda: defaultdict(int))

    satellites_regex = [
        r"(METOP_B)_(\d{5})_(\d{4})(\d{2})(\d{2})_(\d{6})_(BG[1-3]).trk",
        r"(METOP_C)_(\d{5})_(\d{4})(\d{2})(\d{2})_(\d{6})_(BG[1-3]).trk",
        r"(NOAA19)_(\d{5})_(\d{4})(\d{2})(\d{2})_(\d{6})_(BG[1-3]).trk",
        r"(NPP)_(\d{5})_(\d{4})(\d{2})(\d{2})_(\d{6})_(BG[1-3]).trk",
        r"(TERRA)_(\d{5})_(\d{4})(\d{2})(\d{2})_(\d{6})_(BG[1-3]).trk",
    ]

    for root, _, files in os.walk(directory):
        for filename in files:
            for regex in satellites_regex:
                match = re.match(regex, filename)
                if match:
                    satellite = match.group(1)
                    date_str = match.group(3) + match.group(4) + match.group(5)
                    try:
                        file_dt = datetime.strptime(date_str, "%Y%m%d").date()
                    except ValueError:
                        continue

                    if start_dt <= file_dt <= end_dt:
                        station_folder = os.path.basename(root)
                        file_counts[station_folder][satellite] += 1
                    break
    return file_counts


def generate_report(counts_geotif, counts_trk):
    """
    Формирует итоговый текст отчета.
    """
    header = (
        f"Обновленные цифры за {START_DATE_PERIOD.strftime('%d.%m.%Y')} г. - "
        f"{END_DATE_PERIOD.strftime('%d.%m.%Y')} г.\n\n"
    )
    body = ""

    # Данные по станциям (.trk)
    for station, satellite_counts in counts_trk.items():
        st_name_short = station.replace("bg", "")
        st_name_full = station.replace("bg", "BG-")
        body += f"3.{st_name_short}. Станция {st_name_full} приняла:\n"
        for satellite, count in satellite_counts.items():
            body += f"{satellite}    - {count}\n"
        body += "\n"

    # Данные по спутникам (.tif)
    body += "\nДля отправки по FTP было подготовлено:\n\n"
    for satellite in ["METOP", "TERRA", "NOAA", "NPP"]:
        count = counts_geotif.get(satellite, 0)
        body += f"{count} tif-файлов спутников {satellite}\n"

    return header + body


if __name__ == "__main__":
    # Сбор данных
    DATA_TRK = count_files_by_station(
        DIRECTORY_PATH_TRK, START_DATE_PERIOD, END_DATE_PERIOD
    )
    DATA_GEOTIF = count_files_by_satellite(
        DIRECTORY_PATH_GEOTIF, START_DATE_PERIOD, END_DATE_PERIOD
    )

    # Генерация отчета
    FINAL_REPORT = generate_report(DATA_GEOTIF, DATA_TRK)

    # Сохранение
    REPORT_FILENAME = f'Satellite_data_{TODAY.strftime("%d-%m-%Y")}.txt'
    REPORT_PATH = os.path.join(MESSAGE_PATH, REPORT_FILENAME)

    if not os.path.exists(MESSAGE_PATH):
        os.makedirs(MESSAGE_PATH)

    with open(REPORT_PATH, "w", encoding="utf-8") as out_file:
        out_file.write(FINAL_REPORT)
    print(f"Отчет сохранен: {REPORT_PATH}")

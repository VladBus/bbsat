import os
import re
from collections import defaultdict
from datetime import datetime, timedelta

# Определение переменных в глобальной области
today = datetime.today()
end_date = today.date() - timedelta(days=1)
start_date = end_date - timedelta(days=6)
directory_path_geotif = r'S:\GeoTif'
directory_path_trk = r'S:\trk'
message_path = r'S:\message'


def count_files_by_satellite(directory, start_date, end_date):
    """
    Считает количество файлов .tif по спутникам в папках с заданными датами.
    """
    file_counts = defaultdict(int)
    current_year = datetime.now().year

    for root, dirs, files in os.walk(directory):
        # Проверка даты папки
        folder_date_str = os.path.basename(root).split('\\')[-1]  # Получаем дату из последнего уровня папки
        try:
            folder_date = datetime.strptime(folder_date_str, "%d-%m-%Y").date()
        except ValueError:
            continue  # Пропускаем папки, не соответствующие формату даты

        if start_date <= folder_date <= end_date:
            # Проверяем наличие папок со спутниками
            for satellite in ["METOP", "TERRA", "NOAA", "NPP"]:
                satellite_path = os.path.join(root, satellite)
                if os.path.exists(satellite_path):
                    for file in os.listdir(satellite_path):
                        if file.endswith('.tif'):
                            file_counts[satellite] += 1
                else:
                    # Если папки со спутником нет, то количество снимков равно 0
                    file_counts[satellite] = 0

    return file_counts


def count_files_by_station(directory, start_date, end_date):
    """
    Считает количество файлов trk по спутникам в папках с заданными датами.
    """
    file_counts = defaultdict(lambda: defaultdict(int))

    # Регулярные выражения для поиска спутников
    satellites_regex = [
        r"(METOP_B)_(\d{5})_(\d{4})(\d{2})(\d{2})_(\d{6})_(BG[1-3]).trk",
        r"(METOP_C)_(\d{5})_(\d{4})(\d{2})(\d{2})_(\d{6})_(BG[1-3]).trk",
        r"(NOAA19)_(\d{5})_(\d{4})(\d{2})(\d{2})_(\d{6})_(BG[1-3]).trk",
        r"(NPP)_(\d{5})_(\d{4})(\d{2})(\d{2})_(\d{6})_(BG[1-3]).trk",
        r"(TERRA)_(\d{5})_(\d{4})(\d{2})(\d{2})_(\d{6})_(BG[1-3]).trk"
    ]

    for root, dirs, files in os.walk(directory):
        for file in files:
            for regex in satellites_regex:
                match = re.match(regex, file)
                if match:
                    satellite = match.group(1)
                    file_date_str = match.group(3) + match.group(4) + match.group(5)
                    try:
                        file_date = datetime.strptime(file_date_str, "%Y%m%d").date()
                    except ValueError:
                        continue  # Пропускаем файлы, не соответствующие формату даты

                    if start_date <= file_date <= end_date:
                        file_counts[os.path.basename(root)][satellite] += 1
                    break  # Переходим к следующему файлу, если нашли совпадение

    return file_counts


def generate_report(files_by_date, file_counts_geotif, file_counts_trk):
    """
    Формирует отчет о количестве файлов по спутникам и станциям.
    """
    report = f"Обновленные цифры за {start_date.strftime('%d.%m.%Y')} г. - {end_date.strftime('%d.%m.%Y')} г.\n\n"

    # Обработка данных по станциям из файлов trk
    for station, satellite_counts in file_counts_trk.items():
        # Изменяем название станции, удаляя "bg" из начала
        station_name_1 = station.replace('bg', '')
        station_name_2 = station.replace('bg', 'BG-')
        report += f"3.{station_name_1}. Станция {station_name_2} приняла следующие спутники в количестве:\n"
        for satellite, count in satellite_counts.items():
            report += f"{satellite}    - {count}\n"
        report += "\n"

    # Обработка данных по спутникам из файлов GeoTif
    report += "\nДля отправки по FTP было подготовлено:\n\n"
    for satellite in ["METOP", "TERRA", "NOAA", "NPP"]:
        count = file_counts_geotif.get(satellite, 0)  # Получение количества файлов для спутника, или 0, если его нет
        report += f"{count} tif-файлов спутников {satellite}\n"

    return report


# Вызов функций
file_counts_trk = count_files_by_station(directory_path_trk, start_date, end_date)
file_counts_geotif = count_files_by_satellite(directory_path_geotif, start_date, end_date)
report = generate_report(file_counts_trk, file_counts_geotif, file_counts_trk)

# Сохранение отчета в текстовый файл
file_name = f'Satellite_data_{today.strftime("%d-%m-%Y")}.txt'
file_path = os.path.join(message_path, file_name)

with open(file_path, 'w', encoding='utf-8') as file:
    file.write(report)

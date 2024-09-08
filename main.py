import schedule
import time
import os

# Пути к скриптам
sort_files_path = "tiff_processing/SortFilesByDate.py"
tiff_compressor_path = "tiff_processing/tiff_compressor.py"
statistic_path = "week_message/statistic.py"
send_message_path = "week_message/send_message.py"

# Задачи расписания
schedule.every().day.at("01:00").do(lambda: os.system(f"python {sort_files_path}"))
schedule.every().day.at("01:50").do(lambda: os.system(f"python {tiff_compressor_path}"))
schedule.every().wednesday.at("02:45").do(lambda: os.system(f"python {statistic_path}"))
schedule.every().wednesday.at("03:00").do(lambda: os.system(f"python {send_message_path}"))

# Завершение программы через 5 минут после последней задачи
schedule.every().day.at("03:08").do(lambda: exit())

# Бесконечный цикл для выполнения задач
while True:
    schedule.run_pending()
    time.sleep(1)

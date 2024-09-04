import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.encoders import encode_base64
from email.utils import formataddr
from email.header import Header
from datetime import datetime, timedelta
import os
import re

# Определение переменных в глобальной области
today = datetime.today()
end_date = today.date() - timedelta(days=1)
start_date = end_date - timedelta(days=6)
message_path = r'S:\message'
addr_to = 'a.sokolov@aari.ru, vvbusev@aari.ru, anikulina@aari.ru'  # Получатели
# addr_to = 'vvbusev@aari.ru'  # Проверочный адрес, нужен был только во время разработки
addr_from = "vvbusev@aari.ru"  # Отправитель
password = r"AuVF7fJmhH3bX"  # Пароль к почте


def send_email(addr_to, msg_subj, msg_text, files):
    """Отправляет письмо с вложениями."""
    msg = MIMEMultipart()
    msg['From'] = formataddr((str(Header('Владислав Бусев', 'utf-8')), addr_from))
    msg['To'] = addr_to
    msg['Subject'] = msg_subj

    msg.attach(MIMEText(msg_text, 'plain'))

    for filename in files:
        filepath = filename  # Полный путь к файлу
        with open(filepath, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename= {os.path.basename(filename)}")
            msg.attach(part)

    # Отправка письма с обработкой ошибок
    try:
        with smtplib.SMTP_SSL('zmail.aari.ru', 465) as server:
            server.login(addr_from, password)
            server.send_message(msg)
            print("Письмо отправлено успешно!")
    except Exception as e:
        print(f"Ошибка при отправке письма: {e}")


# Использование функции send_email()
subject = f'Спутниковая информация из Баренцбурга'
text = f"""
В приложении к письму спутниковая информация из Баренцбурга 
с {start_date.strftime('%d.%m.%Y')} г. по {end_date.strftime('%d.%m.%Y')} г.

Данное письмо сформировано автоматически.

С уважением
_________________________
Соколов Андрей   ::  Бусев Владислав
Ведущий инженер  ::  Инженер 1 кат.
Центра ледовой и гидрометеорологической информации "Север",
ФГБУ "ААНИИ", Санкт-Петербург

E-mail: a.sokolov@aari.ru 
E-mail: vvbusev@aari.ru
Моб.тел.: +7-921-189-17-33"""

files = []  # Список прикрепляемых файлов

# Поиск файла с соответствующей датой
today_str = today.strftime("%d-%m-%Y")
regex = r"(Satellite_data)_(\d{2})-(\d{2})-(\d{4}).txt"  # регулярное выражение
for filename in os.listdir(message_path):
    match = re.match(regex, filename)
    if match and match.group(2) == today_str.split('-')[0] and match.group(3) == today_str.split('-')[
        1] and match.group(4) == today_str.split('-')[2]:
        files.append(os.path.join(message_path, filename))  # Добавление полного пути

send_email(addr_to, subject, text, files)  # отправка письма

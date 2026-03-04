"""
Модуль для автоматической отправки электронных писем с вложениями.
Отправка выполняется по средам.
"""

import os
import re
import smtplib
from datetime import datetime, timedelta
from email.encoders import encode_base64
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

# Глобальные константы
TODAY = datetime.today()
END_DATE = TODAY.date() - timedelta(days=1)
START_DATE = END_DATE - timedelta(days=6)
MESSAGE_PATH = r"S:\message"

# --- НАСТРОЙКИ ПОЛУЧАТЕЛЕЙ ---
# Здесь перечислены все возможные адреса.
ALL_RECIPIENTS = [
    "a.sokolov@aari.ru",
    "vvbusev@aari.ru",
    # "anikulina@aari.ru",
    # "karan@aari.ru",
    # "sanovikov@aari.ru",
]

ADDR_FROM = "vvbusev@aari.ru"
PASSWORD = r"AuVF7fJmhH3bX"


def send_email(recipient_list, msg_subj, msg_text, attachment_files):
    """Отправляет письмо списку получателей с вложениями."""
    if not attachment_files:
        print("Нет файлов для отправки. Письмо не будет отправлено.")
        return

    msg = MIMEMultipart()
    msg["From"] = formataddr((str(Header("Владислав Бусев", "utf-8")), ADDR_FROM))
    # Объединяем список адресов в одну строку через запятую
    msg["To"] = ", ".join(recipient_list)
    msg["Subject"] = msg_subj

    msg.attach(MIMEText(msg_text, "plain"))

    for filepath in attachment_files:
        if not os.path.exists(filepath):
            continue
        with open(filepath, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {os.path.basename(filepath)}",
            )
            msg.attach(part)

    try:
        with smtplib.SMTP_SSL("zmail.aari.ru", 465) as server:
            server.login(ADDR_FROM, PASSWORD)
            server.send_message(msg)
            print(f"Письмо успешно отправлено на адреса: {', '.join(recipient_list)}")
    except Exception as err:  # pylint: disable=broad-exception-caught
        print(f"Ошибка при отправке письма: {err}")


# Текст письма
SUBJECT = "Спутниковая информация из Баренцбурга"
TEXT = f"""
В приложении к письму спутниковая информация из Баренцбурга 
с {START_DATE.strftime('%d.%m.%Y')} г. по {END_DATE.strftime('%d.%m.%Y')} г.

Данное письмо сформировано автоматически.

С уважением
_________________________
Соколов Андрей   ::   Бусев Владислав
Ведущий инженер  ::   Инженер 1 кат.
Центра ледовой и гидрометеорологической информации "Север",
ФГБУ "ААНИИ", Санкт-Петербург

E-mail: a.sokolov@aari.ru 
E-mail: vvbusev@aari.ru
Моб.тел.: +7-921-189-17-33"""

if __name__ == "__main__":
    # Проверка: если сегодня не среда (2 - это среда, так как 0 - понедельник)
    # Это дополнительная защита, если скрипт запустят случайно не в тот день
    if TODAY.weekday() != 2:
        print(
            f"Сегодня {TODAY.strftime('%A')}. Отправка запланирована только на среду."
        )
        # Если хочешь, чтобы скрипт ВСЕ РАВНО работал при ручном запуске,
        # можешь закомментировать 'exit()'.
        exit()

    FILES_TO_ATTACH = []
    today_str_parts = TODAY.strftime("%d-%m-%Y").split("-")
    REGEX_PATTERN = r"(Satellite_data)_(\d{2})-(\d{2})-(\d{4}).txt"

    if os.path.exists(MESSAGE_PATH):
        for filename in os.listdir(MESSAGE_PATH):
            match = re.match(REGEX_PATTERN, filename)
            if (
                match
                and match.group(2) == today_str_parts[0]
                and match.group(3) == today_str_parts[1]
                and match.group(4) == today_str_parts[2]
            ):
                FILES_TO_ATTACH.append(os.path.join(MESSAGE_PATH, filename))

    # Запуск функции отправки
    send_email(ALL_RECIPIENTS, SUBJECT, TEXT, FILES_TO_ATTACH)

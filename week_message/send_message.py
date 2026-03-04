"""
Модуль для автоматической отправки электронных писем с вложениями.
Поддерживает проверку дня недели и ручной запуск.
"""

import os
import smtplib
import sys
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
MESSAGE_PATH = r"S:\reports\archive_stat"

# --- НАСТРОЙКИ ПОЛУЧАТЕЛЕЙ ---
ALL_RECIPIENTS = [
    "a.sokolov@aari.ru",
    "vvbusev@aari.ru",
]

ADDR_FROM = "vvbusev@aari.ru"
PASSWORD = r"AuVF7fJmhH3bX"
SMTP_SERVER = "zmail.aari.ru"
SMTP_PORT = 465


def send_email(recipient_list, msg_subj, msg_text, attachment_files):
    """Отправляет письмо списку получателей с вложениями."""
    if not attachment_files:
        print("Вложения не найдены. Отмена отправки.")
        return

    msg = MIMEMultipart()
    # Указываем отправителя
    msg["From"] = formataddr((str(Header("Владислав Бусев", "utf-8")), ADDR_FROM))
    msg["To"] = ", ".join(recipient_list)
    # Приводим Header к строке, чтобы Pylance не ругался
    msg["Subject"] = str(Header(msg_subj, "utf-8"))

    msg.attach(MIMEText(msg_text, "plain", "utf-8"))

    for filepath in attachment_files:
        if not os.path.exists(filepath):
            print(f"Файл не найден: {filepath}")
            continue

        try:
            with open(filepath, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                encode_base64(part)
                filename = os.path.basename(filepath)
                part.add_header(
                    "Content-Disposition",
                    f'attachment; filename="{filename}"',
                )
                msg.attach(part)
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Ошибка при обработке вложения {filepath}: {e}")

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(ADDR_FROM, PASSWORD)
            server.send_message(msg)
            print(f"Успех! Письмо отправлено на: {', '.join(recipient_list)}")
    except Exception as err:  # pylint: disable=broad-exception-caught
        print(f"Критическая ошибка SMTP: {err}")


def main_process(force_send=False):
    """Основной процесс поиска отчета и отправки."""

    if not force_send and TODAY.weekday() != 2:
        print(f"Сегодня {TODAY.strftime('%A')}, а не среда. Отправка пропущена.")
        return

    subject = "Спутниковая информация из Баренцбурга"
    text = f"""В приложении к письму спутниковая информация из Баренцбурга
с {START_DATE.strftime('%d.%m.%Y')} г. по {END_DATE.strftime('%d.%m.%Y')} г.

Данное письмо сформировано автоматически.

С уважением,
_________________________
Соколов Андрей  ::  Бусев Владислав
ФГБУ "ААНИИ", Санкт-Петербург"""

    today_str = TODAY.strftime("%d-%m-%Y")
    files_to_attach = []

    if os.path.exists(MESSAGE_PATH):
        for filename in os.listdir(MESSAGE_PATH):
            if "Satellite_data" in filename and today_str in filename:
                files_to_attach.append(os.path.join(MESSAGE_PATH, filename))

    if not files_to_attach:
        print(f"За сегодня ({today_str}) отчетов для отправки не обнаружено.")
        return

    send_email(ALL_RECIPIENTS, subject, text, files_to_attach)


if __name__ == "__main__":
    # Проверка на ручной запуск
    is_manual = len(sys.argv) > 1 or sys.stdin.isatty()
    main_process(force_send=is_manual)

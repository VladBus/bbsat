"""
Модуль для автоматической отправки электронных писем с вложениями.
Поддерживает проверку дня недели и ручной запуск.
"""

import logging
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
from typing import List

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
SMTP_SERVER = "zmail.aari.ru"
SMTP_PORT = 465

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
)
logger = logging.getLogger(__name__)


def get_password() -> str:
    """Получает пароль из переменной окружения для безопасности."""
    password = os.environ.get("BBSAT_EMAIL_PASSWORD")
    if not password:
        # Fallback на жестко заданное значение (только для совместимости)
        password = r"AuVF7fJmhH3bX"
        logger.warning(
            "Переменная окружения BBSAT_EMAIL_PASSWORD не установлена. "
            "Используется пароль по умолчанию."
        )
    return password


def send_email(
    recipient_list: List[str],
    msg_subj: str,
    msg_text: str,
    attachment_files: List[str],
) -> bool:
    """Отправляет письмо списку получателей с вложениями."""
    if not recipient_list:
        logger.error("Список получателей пуст. Отмена отправки.")
        return False

    if not attachment_files:
        logger.warning("Вложения не найдены. Отмена отправки.")
        return False

    msg = MIMEMultipart()
    # Указываем отправителя
    msg["From"] = formataddr((str(Header("Владислав Бусев", "utf-8")), ADDR_FROM))
    msg["To"] = ", ".join(recipient_list)
    # Приводим Header к строке, чтобы Pylance не ругался
    msg["Subject"] = str(Header(msg_subj, "utf-8"))

    msg.attach(MIMEText(msg_text, "plain", "utf-8"))

    attached_count = 0
    for filepath in attachment_files:
        if not os.path.exists(filepath):
            logger.warning("Файл не найден: %s", filepath)
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
                attached_count += 1
                logger.info("Вложение добавлено: %s", filename)
        except OSError as e:
            logger.error("Ошибка ОС при обработке вложения %s: %s", filepath, e)
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Ошибка при обработке вложения %s: %s", filepath, e)

    if attached_count == 0:
        logger.error("Не удалось добавить ни одного вложения. Отмена отправки.")
        return False

    try:
        password = get_password()
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(ADDR_FROM, password)
            server.send_message(msg)
            logger.info("Успех! Письмо отправлено на: %s", ", ".join(recipient_list))
            return True
    except smtplib.SMTPAuthenticationError as e:
        logger.error("Ошибка аутентификации SMTP: %s", e)
        return False
    except smtplib.SMTPException as e:
        logger.error("Ошибка SMTP: %s", e)
        return False
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Критическая ошибка при отправке письма: %s", e)
        return False


def find_attachments() -> List[str]:
    """Ищет файлы для отправки за текущую дату."""
    today_str = TODAY.strftime("%d-%m-%Y")
    files_to_attach = []

    if not os.path.exists(MESSAGE_PATH):
        logger.error("Папка с отчетами не найдена: %s", MESSAGE_PATH)
        return files_to_attach

    for filename in os.listdir(MESSAGE_PATH):
        if "Satellite_data" in filename and today_str in filename:
            files_to_attach.append(os.path.join(MESSAGE_PATH, filename))

    return files_to_attach


def main_process(force_send: bool = False) -> bool:
    """Основной процесс поиска отчета и отправки."""
    if not force_send and TODAY.weekday() != 2:
        logger.info("Сегодня %s, а не среду. Отправка пропущена.", TODAY.strftime("%A"))
        return False

    subject = "Спутниковая информация из Баренцбурга"
    text = f"""В приложении к письму спутниковая информация из Баренцбурга
с {START_DATE.strftime('%d.%m.%Y')} г. по {END_DATE.strftime('%d.%m.%Y')} г.

Данное письмо сформировано автоматически.

С уважением,
_________________________
Соколов Андрей  ::  Бусев Владислав
ФГБУ "ААНИИ", Санкт-Петербург"""

    files_to_attach = find_attachments()

    if not files_to_attach:
        logger.warning(
            "За сегодня (%s) отчетов для отправки не обнаружено.",
            TODAY.strftime("%d-%m-%Y"),
        )
        return False

    return send_email(ALL_RECIPIENTS, subject, text, files_to_attach)


if __name__ == "__main__":
    # Проверка на ручной запуск
    is_manual = len(sys.argv) > 1 or sys.stdin.isatty()
    is_success = main_process(force_send=is_manual)  # pylint: disable=invalid-name
    sys.exit(0 if is_success else 1)

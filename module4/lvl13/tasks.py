from datetime import datetime

from mailer import send_email
from celery_app import celery_app


@celery_app.task
def send_email_task(to: str, subject: str, body: str) -> str:
    send_email(to, subject, body)
    return f"Лист до {to} надіслано"


@celery_app.task
def send_digest() -> str:
    now = f"{datetime.now():%H:%M}"
    send_email("admin@example.com", f"Дайджест за {now}", "Нових замовлень: 0")
    return f"Дайджест за {now} надіслано"

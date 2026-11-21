from datetime import datetime
import os
import socket
import time

from mailer import send_email
from celery_app import celery_app


def who() -> dict:
    return {"worker": socket.gethostname(), "pid": os.getpid(), "done": f"{datetime.now():%H:%M:%S.%f}"[:-3]}


@celery_app.task
def send_email_task(to: str, subject: str, body: str) -> str:
    send_email(to, subject, body)
    return f"Лист до {to} надіслано"


@celery_app.task
def send_digest() -> str:
    now = f"{datetime.now():%H:%M}"
    send_email("admin@example.com", f"Дайджест за {now}", "Нових замовлень: 0")
    return f"Дайджест за {now} надіслано"


@celery_app.task
def send_push(user_id: int) -> dict:
    time.sleep(0.1)
    return {"push": user_id, **who()}


@celery_app.task
def send_alert(text: str) -> dict:
    time.sleep(0.1)
    return {"alert": text, **who()}


@celery_app.task # I/O-bound
def build_report(seconds: float = 10) -> dict:
    time.sleep(seconds)
    return {"report_seconds": seconds, **who()}


@celery_app.task # CPU-bound
def crunch(n: int = 100_000_000) -> dict:
    total = 0
    for i in range(n):
        total += i
    return {"total": total, **who()}


@celery_app.task
def send_promo(code: str) -> dict:
    send_email("client@example.com", "Ваш промокод", f"Код {code} діє 1 годину")
    return {"promo": code, **who()}
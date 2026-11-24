import logging
import time

from celery.exceptions import Ignore, Reject, SoftTimeLimitExceeded
from redis import Redis

from celery_app import celery_app
from config import settings
from mailer import send_email

logger = logging.getLogger(__name__)
redis_client = Redis.from_url(settings.result_backend.rsplit("/", 1)[0] + "/2")


@celery_app.task
def send_email_task(to: str, subject: str, body: str) -> str:
    send_email(to, subject, body)
    return f"Лист до {to} надіслано"


@celery_app.task(bind=True, max_retries=3, retry_jitter=True)
def fetch_rate(self, fail_times: int = 3) -> str:
    try:
        if self.request.retries < fail_times:
            raise ConnectionError("API НБУ не відповідає")
        return f"Курс отримано зі спроби {self.request.retries + 1}"
    except ConnectionError as exc:
        countdown = 2**self.request.retries
        logger.warning("Задача %s: %s, повтор через %s с", self.request.id, exc, countdown)
        raise self.retry(exc=exc, countdown=countdown)
    
    
@celery_app.task(autoretry_for=(ConnectionError,), retry_backoff=True, retry_jitter=False, max_retries=3)
def fetch_always_down() -> str:
    raise ConnectionError("Сервіс лежить")


@celery_app.task(soft_time_limit=3, time_limit=6)
def slow_job(seconds: float) -> str:
    try:
        time.sleep(seconds)
        return f"Готово за {seconds} с"
    except SoftTimeLimitExceeded:
        logger.error("slow_job перевищила 3 с, прибираємо за собою")
        return "Зупинено за таймаутом"
    
    

@celery_app.task(bind=True)
def divide(self, x: int, y: int) -> float:
    try:
        return x / y
    except ZeroDivisionError:
        logger.exception("Задача %s: ділення на нуль", self.request.id)
        raise
    
    
@celery_app.task(bind=True, max_retries=2)
def charge_card(self, order_id: int) -> str:
    try:
        raise ConnectionError("Банк не відповідає")
    except ConnectionError as exc:
        if self.request.retries >= self.max_retries:
            logger.error("Замовлення %s: спроби скінчились, у DLQ", order_id)
            raise Reject(exc, requeue=False) from exc
        raise self.retry(exc=exc, countdown=1)
    
    
@celery_app.task(bind=True)
def process_payment(self, order_id: int) -> str:
    lock_key = f"lock:payment:{order_id}"
    if not redis_client.set(lock_key, self.request.id, nx=True, ex=600):
        logger.warning("Замовлення %s вже обробляється, пропускаємо", order_id)
        raise Ignore()
    try:
        time.sleep(3)
        redis_client.incr(f"paid:{order_id}")
        return f"Замовлення {order_id} оплачено"
    finally:
        redis_client.delete(lock_key)
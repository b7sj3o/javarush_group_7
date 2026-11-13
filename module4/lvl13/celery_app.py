from celery import Celery
from celery.schedules import crontab

from config import settings


celery_app = Celery(
    "tasks", 
    broker=settings.broker_url,
    backend=settings.result_backend,
    include=["tasks"]
)


celery_app.conf.update(
    task_track_started=True,  # без цього статусу STARTED не буде: одразу з PENDING у SUCCESS
    worker_send_task_events=True,  # події для Flower: які задачі зараз виконуються
    timezone="Europe/Kyiv",
    beat_schedule={
        "digest-every-minute": {
            "task": "tasks.send_digest",
            "schedule": crontab(minute="*"),  # щохвилини; щодня о 8:00 було б crontab(hour=8, minute=0)
        },
    },
)

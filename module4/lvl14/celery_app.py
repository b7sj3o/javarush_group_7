from celery import Celery
from celery.schedules import crontab
from kombu import Queue

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
    task_queues=[
        Queue("celery"),
        Queue("notifications", queue_arguments={"x-max-priority": 10}),
        Queue("reports"),
        Queue("cpu"),
    ],
    task_routes={
        "tasks.send_push": {"queue": "notifications"},
        "tasks.send_alert": {"queue": "notifications"},
        "tasks.build_report": {"queue": "reports"},
        "tasks.crunch": {"queue": "cpu"},
    },
    worker_prefetch_multiplier=settings.prefetch_multiplier,
    task_acks_late=settings.acks_late,
    task_reject_on_worker_lost=True
)

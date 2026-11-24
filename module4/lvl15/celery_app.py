from celery import Celery
from kombu import Queue

from config import settings

celery_app = Celery(
    "tasks",
    broker=settings.broker_url,
    backend=settings.result_backend,
    include=["tasks"],
)

celery_app.conf.update(
    task_track_started=True,
    worker_send_task_events=True,
    timezone="Europe/Kyiv",
    task_queues=[
        Queue("celery"),
        Queue("cpu"),
        Queue(
            "payments",
            queue_arguments={"x-dead-letter-exchange": "", "x-dead-letter-routing-key": "payments_dlq"},
        ),
        Queue("payments_dlq"),
    ],
    task_routes={
        "tasks.slow_job": {"queue": "cpu"},
        "tasks.charge_card": {"queue": "payments"},
    },
    worker_prefetch_multiplier=settings.prefetch_multiplier,
    task_acks_late=settings.acks_late,
    task_reject_on_worker_lost=True,
)


@celery_app.on_after_configure.connect
def declare_dlq(sender, **kwargs):
    with sender.connection_for_write() as conn:
        Queue("payments_dlq").bind(conn.default_channel).declare()

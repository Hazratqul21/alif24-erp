from celery import Celery
from app.config import settings

celery_app = Celery(
    "alif24_erp",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Tashkent",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# Register all task modules so workers discover them
celery_app.autodiscover_tasks([
    "app.tasks.notification_tasks",
    "app.tasks.report_tasks",
    "app.tasks.backup_tasks",
])

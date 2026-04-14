import logging
from app.tasks import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="daily_backup_task")
def daily_backup_task():
    logger.info("Kunlik backup boshlandi")


@celery_app.task(name="cleanup_expired_sessions_task")
def cleanup_expired_sessions_task():
    logger.info("Muddati o'tgan sessiyalar tozalanmoqda")

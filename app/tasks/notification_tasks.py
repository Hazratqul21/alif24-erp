import asyncio
import logging
from app.tasks import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="send_sms_task")
def send_sms_task(phone: str, message: str):
    from app.services.sms_service import send_sms
    try:
        asyncio.run(send_sms(phone, message))
        logger.info(f"SMS yuborildi: {phone}")
    except Exception as e:
        logger.error(f"SMS yuborishda xatolik [{phone}]: {e}")


@celery_app.task(name="send_email_task")
def send_email_task(to: str, subject: str, body: str):
    import asyncio
    from app.services.notification_service import send_email_notification
    try:
        asyncio.run(send_email_notification(to, subject, body))
        logger.info(f"Email yuborildi: {to}")
    except Exception as e:
        logger.error(f"Email yuborishda xatolik [{to}]: {e}")


@celery_app.task(name="send_bulk_notification_task")
def send_bulk_notification_task(tenant_id: int, notification_data: dict):
    logger.info(f"Ommaviy bildirishnoma yuborilmoqda [tenant={tenant_id}]")


@celery_app.task(name="attendance_alert_task")
def attendance_alert_task(tenant_id: int, student_id: str, status: str):
    logger.info(f"Davomat ogohlantirish [tenant={tenant_id}, student={student_id}, status={status}]")

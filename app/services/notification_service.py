import logging
from typing import Optional

import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import AppError, NotFoundError, ValidationError
from app.services import sms_service

logger = logging.getLogger(__name__)


async def send_notification(
    db: AsyncSession,
    title: str,
    content: str,
    recipient_ids: list[str],
    channel: str = "in_app",
    sender_id: Optional[str] = None,
    tenant_id: Optional[int] = None,
) -> dict:
    if not recipient_ids:
        raise ValidationError("Kamida bitta qabul qiluvchi kerak")

    if channel not in ("in_app", "sms", "email", "push"):
        raise ValidationError(f"Noto'g'ri kanal: {channel}")

    try:
        result = await db.execute(
            text(
                "INSERT INTO notifications (title, content, channel, sender_id, is_broadcast) "
                "VALUES (:title, :content, :channel, :sender_id, :is_broadcast) "
                "RETURNING id"
            ),
            {
                "title": title,
                "content": content,
                "channel": channel,
                "sender_id": sender_id,
                "is_broadcast": len(recipient_ids) > 1,
            },
        )
        notification_id = result.scalar()

        for rid in recipient_ids:
            await db.execute(
                text(
                    "INSERT INTO notification_recipients (notification_id, recipient_id) "
                    "VALUES (:nid, :rid)"
                ),
                {"nid": notification_id, "rid": rid},
            )

        await db.commit()

        if channel == "sms":
            await _dispatch_sms(db, content, recipient_ids)
        elif channel == "email":
            await _dispatch_email(db, title, content, recipient_ids)

        logger.info(
            f"Notification sent: id={notification_id}, channel={channel}, "
            f"recipients={len(recipient_ids)}"
        )
        return {"notification_id": notification_id, "recipients_count": len(recipient_ids)}

    except (ValidationError, AppError):
        raise
    except Exception as e:
        logger.error(f"Notification send error: {e}")
        raise AppError("Xabarnoma yuborishda xatolik")


async def send_sms_notification(phone: str, message: str) -> dict:
    return await sms_service.send_sms(phone, message)


async def send_email_notification(
    to: str,
    subject: str,
    body: str,
) -> None:
    import aiosmtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning("SMTP not configured, skipping email")
        return

    msg = MIMEMultipart("alternative")
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html", "utf-8"))

    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=True,
        )
        logger.info(f"Email sent to {to}")
    except Exception as e:
        logger.error(f"Email send error to {to}: {e}")
        raise AppError("Email yuborishda xatolik", status_code=502)


async def send_in_app(
    db: AsyncSession,
    notification_id: int,
    recipient_ids: list[str],
) -> None:
    result = await db.execute(
        text("SELECT id FROM notifications WHERE id = :nid"),
        {"nid": notification_id},
    )
    if not result.fetchone():
        raise NotFoundError("Xabarnoma")

    for rid in recipient_ids:
        await db.execute(
            text(
                "INSERT INTO notification_recipients (notification_id, recipient_id, is_read) "
                "VALUES (:nid, :rid, false) "
                "ON CONFLICT (notification_id, recipient_id) DO NOTHING"
            ),
            {"nid": notification_id, "rid": rid},
        )

    await db.commit()
    logger.info(
        f"In-app notification {notification_id} delivered to {len(recipient_ids)} recipients"
    )


async def _dispatch_sms(
    db: AsyncSession,
    content: str,
    recipient_ids: list[str],
) -> None:
    result = await db.execute(
        text("SELECT id, phone FROM users WHERE id = ANY(:ids) AND phone IS NOT NULL"),
        {"ids": recipient_ids},
    )
    for row in result.fetchall():
        try:
            await sms_service.send_sms(row.phone, content)
        except Exception as e:
            logger.error(f"SMS dispatch failed for user {row.id}: {e}")


async def _dispatch_email(
    db: AsyncSession,
    subject: str,
    content: str,
    recipient_ids: list[str],
) -> None:
    result = await db.execute(
        text("SELECT id, email FROM users WHERE id = ANY(:ids) AND email IS NOT NULL"),
        {"ids": recipient_ids},
    )
    for row in result.fetchall():
        try:
            await send_email_notification(row.email, subject, content)
        except Exception as e:
            logger.error(f"Email dispatch failed for user {row.id}: {e}")

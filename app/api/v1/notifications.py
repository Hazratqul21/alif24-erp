from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional

from app.core.dependencies import get_db, get_current_user
from app.core.rbac import require_permission
from app.core.exceptions import NotFoundError

router = APIRouter(tags=["Notifications"])


@router.get("")
async def list_notifications(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    unread_only: bool = False,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    params: dict = {"user_id": current_user["id"], "limit": per_page, "offset": (page - 1) * per_page}
    where = "WHERE n.user_id = :user_id"
    if unread_only:
        where += " AND n.read_at IS NULL"

    total = (await db.execute(text(f"SELECT COUNT(*) FROM notifications n {where}"), params)).scalar()
    rows = await db.execute(text(f"""
        SELECT n.id, n.title, n.message, n.notification_type, n.read_at, n.created_at
        FROM notifications n {where}
        ORDER BY n.created_at DESC LIMIT :limit OFFSET :offset
    """), params)
    return {"items": [dict(r._mapping) for r in rows], "total": total, "page": page}


@router.post("", status_code=201)
@require_permission("notifications", "create")
async def create_notification(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    target_users = data.get("user_ids", [])
    is_broadcast = data.get("broadcast", False)

    if is_broadcast:
        users_q = await db.execute(text("SELECT id FROM users WHERE is_active = true"))
        target_users = [r[0] for r in users_q]

    count = 0
    for uid in target_users:
        await db.execute(text("""
            INSERT INTO notifications (user_id, title, message, notification_type, created_by)
            VALUES (:user_id, :title, :message, :type, :created_by)
        """), {
            "user_id": uid, "title": data["title"], "message": data["message"],
            "type": data.get("notification_type", "info"), "created_by": current_user["id"],
        })
        count += 1

    await db.commit()
    return {"sent": count, "message": f"{count} ta bildirishnoma yuborildi"}


@router.put("/{notification_id}/read")
async def mark_read(
    notification_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        UPDATE notifications SET read_at = NOW()
        WHERE id = :id AND user_id = :user_id AND read_at IS NULL
        RETURNING id
    """), {"id": notification_id, "user_id": current_user["id"]})
    if not result.fetchone():
        raise NotFoundError("Bildirishnoma")
    await db.commit()
    return {"message": "O'qilgan deb belgilandi"}


@router.put("/read-all")
async def mark_all_read(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        UPDATE notifications SET read_at = NOW()
        WHERE user_id = :user_id AND read_at IS NULL
    """), {"user_id": current_user["id"]})
    await db.commit()
    return {"message": "Barcha bildirishnomalar o'qilgan deb belgilandi"}


# --- Message Threads ---

@router.get("/threads")
async def list_threads(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await db.execute(text("""
        SELECT mt.id, mt.subject, mt.created_at,
               (SELECT COUNT(*) FROM thread_messages tm WHERE tm.thread_id = mt.id) as message_count,
               (SELECT MAX(tm.created_at) FROM thread_messages tm WHERE tm.thread_id = mt.id) as last_message_at
        FROM message_threads mt
        JOIN thread_participants tp ON tp.thread_id = mt.id
        WHERE tp.user_id = :user_id
        ORDER BY last_message_at DESC NULLS LAST
    """), {"user_id": current_user["id"]})
    return {"threads": [dict(r._mapping) for r in rows]}


@router.post("/threads", status_code=201)
async def create_thread(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        INSERT INTO message_threads (subject, created_by)
        VALUES (:subject, :created_by)
        RETURNING id
    """), {"subject": data["subject"], "created_by": current_user["id"]})
    thread_id = row.scalar()

    participants = data.get("participant_ids", [])
    participants.append(current_user["id"])
    for pid in set(participants):
        await db.execute(text("""
            INSERT INTO thread_participants (thread_id, user_id) VALUES (:tid, :uid)
            ON CONFLICT DO NOTHING
        """), {"tid": thread_id, "uid": pid})

    if data.get("message"):
        await db.execute(text("""
            INSERT INTO thread_messages (thread_id, sender_id, content) VALUES (:tid, :uid, :content)
        """), {"tid": thread_id, "uid": current_user["id"], "content": data["message"]})

    await db.commit()
    return {"id": thread_id, "message": "Suhbat yaratildi"}


@router.post("/threads/{thread_id}/messages")
async def send_message(
    thread_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    check = await db.execute(text("""
        SELECT 1 FROM thread_participants WHERE thread_id = :tid AND user_id = :uid
    """), {"tid": thread_id, "uid": current_user["id"]})
    if not check.fetchone():
        raise NotFoundError("Suhbat yoki ruxsat yo'q")

    row = await db.execute(text("""
        INSERT INTO thread_messages (thread_id, sender_id, content)
        VALUES (:tid, :uid, :content) RETURNING id
    """), {"tid": thread_id, "uid": current_user["id"], "content": data["content"]})
    await db.commit()
    return {"id": row.scalar(), "message": "Xabar yuborildi"}


@router.get("/threads/{thread_id}/messages")
async def thread_messages(
    thread_id: int,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    check = await db.execute(text("""
        SELECT 1 FROM thread_participants WHERE thread_id = :tid AND user_id = :uid
    """), {"tid": thread_id, "uid": current_user["id"]})
    if not check.fetchone():
        raise NotFoundError("Suhbat yoki ruxsat yo'q")

    rows = await db.execute(text("""
        SELECT tm.id, tm.content, tm.created_at,
               u.first_name || ' ' || u.last_name as sender_name
        FROM thread_messages tm
        JOIN users u ON u.id = tm.sender_id
        WHERE tm.thread_id = :tid
        ORDER BY tm.created_at
        LIMIT :limit OFFSET :offset
    """), {"tid": thread_id, "limit": per_page, "offset": (page - 1) * per_page})
    return {"messages": [dict(r._mapping) for r in rows]}

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import date

from app.core.dependencies import get_db, get_current_user
from app.core.rbac import require_permission
from app.core.exceptions import NotFoundError, ConflictError

router = APIRouter(tags=["Schedules"])

SCHEDULE_SELECT = """
    SELECT sc.id, sc.day_of_week, sc.start_time, sc.end_time,
           sub.name as subject, c.name as class_name,
           u.first_name || ' ' || u.last_name as teacher_name,
           r.name as room
    FROM schedules sc
    JOIN subjects sub ON sub.id = sc.subject_id
    JOIN classes c ON c.id = sc.class_id
    LEFT JOIN teachers t ON t.id = sc.teacher_id
    LEFT JOIN users u ON u.id = t.user_id
    LEFT JOIN rooms r ON r.id = sc.room_id
"""


@router.get("/class/{class_id}")
@require_permission("schedules", "read")
async def class_schedule(
    class_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await db.execute(text(f"""
        {SCHEDULE_SELECT} WHERE sc.class_id = :class_id
        ORDER BY sc.day_of_week, sc.start_time
    """), {"class_id": class_id})
    return {"schedule": [dict(r._mapping) for r in rows]}


@router.get("/teacher/{teacher_id}")
@require_permission("schedules", "read")
async def teacher_schedule(
    teacher_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await db.execute(text(f"""
        {SCHEDULE_SELECT} WHERE sc.teacher_id = :teacher_id
        ORDER BY sc.day_of_week, sc.start_time
    """), {"teacher_id": teacher_id})
    return {"schedule": [dict(r._mapping) for r in rows]}


@router.get("/student/{student_id}")
@require_permission("schedules", "read")
async def student_schedule(
    student_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cls = await db.execute(text("SELECT class_id FROM students WHERE id = :id"), {"id": student_id})
    class_id = cls.scalar()
    if not class_id:
        raise NotFoundError("O'quvchi yoki sinf")

    rows = await db.execute(text(f"""
        {SCHEDULE_SELECT} WHERE sc.class_id = :class_id
        ORDER BY sc.day_of_week, sc.start_time
    """), {"class_id": class_id})
    return {"schedule": [dict(r._mapping) for r in rows]}


@router.get("/today")
@require_permission("schedules", "read")
async def today_schedule(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    dow = date.today().isoweekday()
    rows = await db.execute(text(f"""
        {SCHEDULE_SELECT} WHERE sc.day_of_week = :dow
        ORDER BY sc.start_time, c.name
    """), {"dow": dow})
    return {"date": str(date.today()), "day_of_week": dow, "schedule": [dict(r._mapping) for r in rows]}


@router.post("/", status_code=201)
@require_permission("schedules", "create")
async def create_schedule(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conflict = await db.execute(text("""
        SELECT id FROM schedules
        WHERE day_of_week = :dow AND (
            (teacher_id = :teacher_id OR room_id = :room_id OR class_id = :class_id)
            AND start_time < :end_time AND end_time > :start_time
        )
    """), {
        "dow": data["day_of_week"],
        "teacher_id": data.get("teacher_id"),
        "room_id": data.get("room_id"),
        "class_id": data["class_id"],
        "start_time": data["start_time"],
        "end_time": data["end_time"],
    })
    if conflict.fetchone():
        raise ConflictError("Jadval to'qnashuvi aniqlandi (o'qituvchi, xona yoki sinf band)")

    row = await db.execute(text("""
        INSERT INTO schedules (class_id, subject_id, teacher_id, room_id, day_of_week, start_time, end_time)
        VALUES (:class_id, :subject_id, :teacher_id, :room_id, :day_of_week, :start_time, :end_time)
        RETURNING id
    """), {
        "class_id": data["class_id"],
        "subject_id": data["subject_id"],
        "teacher_id": data.get("teacher_id"),
        "room_id": data.get("room_id"),
        "day_of_week": data["day_of_week"],
        "start_time": data["start_time"],
        "end_time": data["end_time"],
    })
    await db.commit()
    return {"id": row.scalar(), "message": "Dars jadvali yaratildi"}


@router.put("/{schedule_id}")
@require_permission("schedules", "update")
async def update_schedule(
    schedule_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        UPDATE schedules SET
            class_id = COALESCE(:class_id, class_id),
            subject_id = COALESCE(:subject_id, subject_id),
            teacher_id = COALESCE(:teacher_id, teacher_id),
            room_id = COALESCE(:room_id, room_id),
            day_of_week = COALESCE(:day_of_week, day_of_week),
            start_time = COALESCE(:start_time, start_time),
            end_time = COALESCE(:end_time, end_time),
            updated_at = NOW()
        WHERE id = :id RETURNING id
    """), {
        **{k: data.get(k) for k in ("class_id", "subject_id", "teacher_id", "room_id", "day_of_week", "start_time", "end_time")},
        "id": schedule_id,
    })
    if not result.fetchone():
        raise NotFoundError("Dars jadvali")
    await db.commit()
    return {"message": "Dars jadvali yangilandi"}


@router.delete("/{schedule_id}")
@require_permission("schedules", "delete")
async def delete_schedule(
    schedule_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("DELETE FROM schedules WHERE id = :id RETURNING id"), {"id": schedule_id})
    if not result.fetchone():
        raise NotFoundError("Dars jadvali")
    await db.commit()
    return {"message": "Dars jadvali o'chirildi"}

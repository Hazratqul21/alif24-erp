from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional

from app.core.dependencies import get_db, get_current_user
from app.core.rbac import require_permission
from app.core.exceptions import NotFoundError, AppError

router = APIRouter(tags=["Attendance"])


@router.post("/mark")
@require_permission("attendance", "create")
async def mark_attendance(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        INSERT INTO attendance (student_id, class_id, date, status, note, marked_by)
        VALUES (:student_id, :class_id, :date, :status, :note, :marked_by)
        ON CONFLICT (student_id, date) DO UPDATE SET status = :status, note = :note, marked_by = :marked_by
        RETURNING id
    """), {
        "student_id": data["student_id"],
        "class_id": data.get("class_id"),
        "date": data["date"],
        "status": data["status"],
        "note": data.get("note"),
        "marked_by": current_user["id"],
    })
    await db.commit()
    return {"id": row.scalar(), "message": "Davomat belgilandi"}


@router.post("/bulk")
@require_permission("attendance", "create")
async def bulk_attendance(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    class_id = data["class_id"]
    att_date = data["date"]
    records = data["records"]
    count = 0

    for rec in records:
        await db.execute(text("""
            INSERT INTO attendance (student_id, class_id, date, status, note, marked_by)
            VALUES (:student_id, :class_id, :date, :status, :note, :marked_by)
            ON CONFLICT (student_id, date) DO UPDATE SET status = :status, note = :note
        """), {
            "student_id": rec["student_id"],
            "class_id": class_id,
            "date": att_date,
            "status": rec["status"],
            "note": rec.get("note"),
            "marked_by": current_user["id"],
        })
        count += 1

    await db.commit()
    return {"marked": count, "message": f"{count} ta o'quvchi davomati belgilandi"}


@router.post("/qr")
@require_permission("attendance", "create")
async def qr_checkin(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    student = await db.execute(text("""
        SELECT id, class_id FROM students WHERE student_code = :code AND deleted_at IS NULL
    """), {"code": data["qr_code"]})
    row = student.fetchone()
    if not row:
        raise NotFoundError("O'quvchi (QR kod bo'yicha)")

    from datetime import date as d
    att = await db.execute(text("""
        INSERT INTO attendance (student_id, class_id, date, status, check_in_time, marked_by)
        VALUES (:sid, :cid, :date, 'present', NOW(), :marked_by)
        ON CONFLICT (student_id, date) DO UPDATE SET check_in_time = NOW(), status = 'present'
        RETURNING id
    """), {"sid": row[0], "cid": row[1], "date": str(d.today()), "marked_by": current_user["id"]})
    await db.commit()
    return {"id": att.scalar(), "student_id": row[0], "message": "QR orqali davomat belgilandi"}


@router.get("/class/{class_id}/date/{date}")
@require_permission("attendance", "read")
async def class_attendance_by_date(
    class_id: int,
    date: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await db.execute(text("""
        SELECT a.id, a.student_id, u.first_name, u.last_name, a.status, a.note, a.check_in_time
        FROM attendance a
        JOIN students s ON s.id = a.student_id
        JOIN users u ON u.id = s.user_id
        WHERE a.class_id = :class_id AND a.date = :date
        ORDER BY u.last_name
    """), {"class_id": class_id, "date": date})
    return {"attendance": [dict(r._mapping) for r in rows]}


@router.get("/student/{student_id}/monthly")
@require_permission("attendance", "read")
async def student_monthly(
    student_id: int,
    month: int = Query(..., ge=1, le=12),
    year: int = Query(...),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await db.execute(text("""
        SELECT date, status, note, check_in_time
        FROM attendance
        WHERE student_id = :id AND EXTRACT(MONTH FROM date) = :month AND EXTRACT(YEAR FROM date) = :year
        ORDER BY date
    """), {"id": student_id, "month": month, "year": year})

    stats = await db.execute(text("""
        SELECT status, COUNT(*) as cnt
        FROM attendance
        WHERE student_id = :id AND EXTRACT(MONTH FROM date) = :month AND EXTRACT(YEAR FROM date) = :year
        GROUP BY status
    """), {"id": student_id, "month": month, "year": year})

    return {
        "records": [dict(r._mapping) for r in rows],
        "summary": {r[0]: r[1] for r in stats},
    }


@router.get("/reports")
@require_permission("attendance", "read")
async def attendance_reports(
    class_id: Optional[int] = None,
    month: Optional[int] = None,
    year: Optional[int] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conditions = []
    params: dict = {}
    if class_id:
        conditions.append("a.class_id = :class_id")
        params["class_id"] = class_id
    if month:
        conditions.append("EXTRACT(MONTH FROM a.date) = :month")
        params["month"] = month
    if year:
        conditions.append("EXTRACT(YEAR FROM a.date) = :year")
        params["year"] = year

    where = "WHERE " + " AND ".join(conditions) if conditions else ""

    rows = await db.execute(text(f"""
        SELECT c.name as class_name,
               COUNT(*) FILTER (WHERE a.status = 'present') as present,
               COUNT(*) FILTER (WHERE a.status = 'absent') as absent,
               COUNT(*) FILTER (WHERE a.status = 'late') as late,
               COUNT(*) FILTER (WHERE a.status = 'excused') as excused,
               COUNT(*) as total
        FROM attendance a
        JOIN classes c ON c.id = a.class_id
        {where}
        GROUP BY c.name ORDER BY c.name
    """), params)
    return {"report": [dict(r._mapping) for r in rows]}

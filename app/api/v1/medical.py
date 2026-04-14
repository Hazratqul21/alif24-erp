from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional

from app.core.dependencies import get_db, get_current_user
from app.core.rbac import require_role
from app.core.exceptions import NotFoundError

router = APIRouter(tags=["Medical"])


# --- Medical Records ---

@router.get("/records")
@require_role("medical_staff", "director", "administrator")
async def list_records(
    student_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    params: dict = {"limit": per_page, "offset": (page - 1) * per_page}
    where = ""
    if student_id:
        where = "WHERE mr.student_id = :student_id"
        params["student_id"] = student_id

    rows = await db.execute(text(f"""
        SELECT mr.id, mr.student_id, u.first_name, u.last_name, mr.record_type,
               mr.diagnosis, mr.treatment, mr.record_date, mr.created_at
        FROM medical_records mr
        JOIN students s ON s.id = mr.student_id
        JOIN users u ON u.id = s.user_id
        {where} ORDER BY mr.record_date DESC LIMIT :limit OFFSET :offset
    """), params)
    return {"items": [dict(r._mapping) for r in rows]}


@router.post("/records", status_code=201)
@require_role("medical_staff")
async def create_record(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        INSERT INTO medical_records (student_id, record_type, diagnosis, treatment, notes, record_date, created_by)
        VALUES (:student_id, :record_type, :diagnosis, :treatment, :notes, COALESCE(:record_date, CURRENT_DATE), :created_by)
        RETURNING id
    """), {
        "student_id": data["student_id"], "record_type": data.get("record_type", "general"),
        "diagnosis": data.get("diagnosis"), "treatment": data.get("treatment"),
        "notes": data.get("notes"), "record_date": data.get("record_date"),
        "created_by": current_user["id"],
    })
    await db.commit()
    return {"id": row.scalar(), "message": "Tibbiy yozuv yaratildi"}


@router.get("/records/{record_id}")
@require_role("medical_staff", "director", "administrator")
async def get_record(
    record_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        SELECT mr.*, u.first_name, u.last_name
        FROM medical_records mr
        JOIN students s ON s.id = mr.student_id
        JOIN users u ON u.id = s.user_id
        WHERE mr.id = :id
    """), {"id": record_id})
    rec = row.fetchone()
    if not rec:
        raise NotFoundError("Tibbiy yozuv")
    return dict(rec._mapping)


@router.put("/records/{record_id}")
@require_role("medical_staff")
async def update_record(
    record_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        UPDATE medical_records SET diagnosis = COALESCE(:diagnosis, diagnosis),
            treatment = COALESCE(:treatment, treatment),
            notes = COALESCE(:notes, notes),
            record_type = COALESCE(:record_type, record_type),
            updated_at = NOW()
        WHERE id = :id RETURNING id
    """), {**{k: data.get(k) for k in ("diagnosis", "treatment", "notes", "record_type")}, "id": record_id})
    if not result.fetchone():
        raise NotFoundError("Tibbiy yozuv")
    await db.commit()
    return {"message": "Tibbiy yozuv yangilandi"}


@router.delete("/records/{record_id}")
@require_role("medical_staff", "director")
async def delete_record(
    record_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("DELETE FROM medical_records WHERE id = :id RETURNING id"), {"id": record_id})
    if not result.fetchone():
        raise NotFoundError("Tibbiy yozuv")
    await db.commit()
    return {"message": "Tibbiy yozuv o'chirildi"}


# --- Medical Exams ---

@router.get("/exams")
@require_role("medical_staff", "director", "administrator")
async def list_exams(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await db.execute(text("""
        SELECT me.id, me.exam_type, me.exam_date, me.class_id, c.name as class_name,
               me.status, me.notes
        FROM medical_exams me
        LEFT JOIN classes c ON c.id = me.class_id
        ORDER BY me.exam_date DESC LIMIT :limit OFFSET :offset
    """), {"limit": per_page, "offset": (page - 1) * per_page})
    return {"items": [dict(r._mapping) for r in rows]}


@router.post("/exams", status_code=201)
@require_role("medical_staff")
async def create_exam(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        INSERT INTO medical_exams (exam_type, exam_date, class_id, status, notes, created_by)
        VALUES (:exam_type, :exam_date, :class_id, :status, :notes, :created_by)
        RETURNING id
    """), {
        "exam_type": data["exam_type"], "exam_date": data["exam_date"],
        "class_id": data.get("class_id"), "status": data.get("status", "scheduled"),
        "notes": data.get("notes"), "created_by": current_user["id"],
    })
    await db.commit()
    return {"id": row.scalar(), "message": "Tibbiy ko'rik yaratildi"}


@router.put("/exams/{exam_id}")
@require_role("medical_staff")
async def update_exam(
    exam_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        UPDATE medical_exams SET exam_type = COALESCE(:exam_type, exam_type),
            exam_date = COALESCE(:exam_date, exam_date),
            status = COALESCE(:status, status),
            notes = COALESCE(:notes, notes), updated_at = NOW()
        WHERE id = :id RETURNING id
    """), {**{k: data.get(k) for k in ("exam_type", "exam_date", "status", "notes")}, "id": exam_id})
    if not result.fetchone():
        raise NotFoundError("Tibbiy ko'rik")
    await db.commit()
    return {"message": "Tibbiy ko'rik yangilandi"}


@router.delete("/exams/{exam_id}")
@require_role("medical_staff", "director")
async def delete_exam(
    exam_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("DELETE FROM medical_exams WHERE id = :id RETURNING id"), {"id": exam_id})
    if not result.fetchone():
        raise NotFoundError("Tibbiy ko'rik")
    await db.commit()
    return {"message": "Tibbiy ko'rik o'chirildi"}


# --- Quarantine ---

@router.get("/quarantine")
@require_role("medical_staff", "director", "administrator")
async def list_quarantine(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await db.execute(text("""
        SELECT q.id, q.student_id, u.first_name, u.last_name, q.reason, q.start_date,
               q.end_date, q.status, q.notes
        FROM quarantine q
        JOIN students s ON s.id = q.student_id
        JOIN users u ON u.id = s.user_id
        ORDER BY q.start_date DESC
    """))
    return {"items": [dict(r._mapping) for r in rows]}


@router.post("/quarantine", status_code=201)
@require_role("medical_staff")
async def create_quarantine(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        INSERT INTO quarantine (student_id, reason, start_date, end_date, status, notes, created_by)
        VALUES (:student_id, :reason, :start_date, :end_date, :status, :notes, :created_by)
        RETURNING id
    """), {
        "student_id": data["student_id"], "reason": data["reason"],
        "start_date": data["start_date"], "end_date": data.get("end_date"),
        "status": data.get("status", "active"), "notes": data.get("notes"),
        "created_by": current_user["id"],
    })
    await db.commit()
    return {"id": row.scalar(), "message": "Karantin yozuvi yaratildi"}


@router.put("/quarantine/{quarantine_id}")
@require_role("medical_staff")
async def update_quarantine(
    quarantine_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        UPDATE quarantine SET reason = COALESCE(:reason, reason),
            end_date = COALESCE(:end_date, end_date),
            status = COALESCE(:status, status),
            notes = COALESCE(:notes, notes), updated_at = NOW()
        WHERE id = :id RETURNING id
    """), {**{k: data.get(k) for k in ("reason", "end_date", "status", "notes")}, "id": quarantine_id})
    if not result.fetchone():
        raise NotFoundError("Karantin yozuvi")
    await db.commit()
    return {"message": "Karantin yozuvi yangilandi"}


@router.delete("/quarantine/{quarantine_id}")
@require_role("medical_staff", "director")
async def delete_quarantine(
    quarantine_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("DELETE FROM quarantine WHERE id = :id RETURNING id"), {"id": quarantine_id})
    if not result.fetchone():
        raise NotFoundError("Karantin yozuvi")
    await db.commit()
    return {"message": "Karantin yozuvi o'chirildi"}

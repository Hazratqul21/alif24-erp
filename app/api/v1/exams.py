from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional

from app.core.dependencies import get_db, get_current_user
from app.core.rbac import require_permission
from app.core.exceptions import NotFoundError

router = APIRouter(tags=["Exams"])


@router.get("")
@require_permission("exams", "view")
async def list_exams(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    class_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    params: dict = {"limit": per_page, "offset": (page - 1) * per_page}
    conditions = []
    if class_id:
        conditions.append("e.class_id = :class_id")
        params["class_id"] = class_id
    if subject_id:
        conditions.append("e.subject_id = :subject_id")
        params["subject_id"] = subject_id

    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    total = (await db.execute(text(f"SELECT COUNT(*) FROM exams e {where}"), params)).scalar()
    rows = await db.execute(text(f"""
        SELECT e.id, e.title, e.exam_type, e.exam_date, e.duration_minutes,
               e.max_score, sub.name as subject, c.name as class_name, e.status, e.created_at
        FROM exams e
        JOIN subjects sub ON sub.id = e.subject_id
        JOIN classes c ON c.id = e.class_id
        {where} ORDER BY e.exam_date DESC LIMIT :limit OFFSET :offset
    """), params)
    return {"items": [dict(r._mapping) for r in rows], "total": total, "page": page}


@router.post("", status_code=201)
@require_permission("exams", "create")
async def create_exam(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        INSERT INTO exams (title, exam_type, class_id, subject_id, teacher_id,
                           exam_date, duration_minutes, max_score, status, description)
        VALUES (:title, :exam_type, :class_id, :subject_id, :teacher_id,
                :exam_date, :duration_minutes, :max_score, :status, :description)
        RETURNING id
    """), {
        "title": data["title"], "exam_type": data.get("exam_type", "midterm"),
        "class_id": data["class_id"], "subject_id": data["subject_id"],
        "teacher_id": data.get("teacher_id"), "exam_date": data["exam_date"],
        "duration_minutes": data.get("duration_minutes", 60),
        "max_score": data.get("max_score", 100),
        "status": data.get("status", "scheduled"),
        "description": data.get("description"),
    })
    await db.commit()
    return {"id": row.scalar(), "message": "Imtihon yaratildi"}


@router.get("/{exam_id}")
@require_permission("exams", "view")
async def get_exam(
    exam_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        SELECT e.*, sub.name as subject, c.name as class_name,
               u.first_name || ' ' || u.last_name as teacher
        FROM exams e
        JOIN subjects sub ON sub.id = e.subject_id
        JOIN classes c ON c.id = e.class_id
        LEFT JOIN teachers t ON t.id = e.teacher_id
        LEFT JOIN users u ON u.id = t.user_id
        WHERE e.id = :id
    """), {"id": exam_id})
    exam = row.fetchone()
    if not exam:
        raise NotFoundError("Imtihon")
    return dict(exam._mapping)


@router.put("/{exam_id}")
@require_permission("exams", "update")
async def update_exam(
    exam_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        UPDATE exams SET title = COALESCE(:title, title),
            exam_type = COALESCE(:exam_type, exam_type),
            exam_date = COALESCE(:exam_date, exam_date),
            duration_minutes = COALESCE(:duration_minutes, duration_minutes),
            max_score = COALESCE(:max_score, max_score),
            status = COALESCE(:status, status),
            description = COALESCE(:description, description),
            updated_at = NOW()
        WHERE id = :id RETURNING id
    """), {**{k: data.get(k) for k in ("title", "exam_type", "exam_date", "duration_minutes", "max_score", "status", "description")}, "id": exam_id})
    if not result.fetchone():
        raise NotFoundError("Imtihon")
    await db.commit()
    return {"message": "Imtihon yangilandi"}


@router.delete("/{exam_id}")
@require_permission("exams", "delete")
async def delete_exam(
    exam_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("DELETE FROM exams WHERE id = :id RETURNING id"), {"id": exam_id})
    if not result.fetchone():
        raise NotFoundError("Imtihon")
    await db.commit()
    return {"message": "Imtihon o'chirildi"}


@router.post("/{exam_id}/submit", status_code=201)
@require_permission("exams", "create")
async def submit_exam(
    exam_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    check = await db.execute(text("SELECT id FROM exams WHERE id = :id"), {"id": exam_id})
    if not check.fetchone():
        raise NotFoundError("Imtihon")

    row = await db.execute(text("""
        INSERT INTO exam_submissions (exam_id, student_id, answers, score, submitted_at)
        VALUES (:exam_id, :student_id, :answers::jsonb, :score, NOW())
        ON CONFLICT (exam_id, student_id) DO UPDATE SET answers = :answers::jsonb, score = :score, submitted_at = NOW()
        RETURNING id
    """), {
        "exam_id": exam_id, "student_id": data["student_id"],
        "answers": str(data.get("answers", "{}")), "score": data.get("score"),
    })
    await db.commit()
    return {"id": row.scalar(), "message": "Imtihon javobi topshirildi"}


@router.get("/{exam_id}/results")
@require_permission("exams", "view")
async def exam_results(
    exam_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    check = await db.execute(text("SELECT id, title, max_score FROM exams WHERE id = :id"), {"id": exam_id})
    exam = check.fetchone()
    if not exam:
        raise NotFoundError("Imtihon")

    rows = await db.execute(text("""
        SELECT es.id, es.student_id, u.first_name, u.last_name, es.score,
               es.submitted_at,
               RANK() OVER (ORDER BY es.score DESC) as rank
        FROM exam_submissions es
        JOIN students s ON s.id = es.student_id
        JOIN users u ON u.id = s.user_id
        WHERE es.exam_id = :exam_id
        ORDER BY es.score DESC
    """), {"exam_id": exam_id})
    return {
        "exam": {"id": exam[0], "title": exam[1], "max_score": exam[2]},
        "results": [dict(r._mapping) for r in rows],
    }

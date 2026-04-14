from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional

from app.core.dependencies import get_db, get_current_user
from app.core.rbac import require_permission
from app.core.exceptions import NotFoundError

router = APIRouter(tags=["Homework"])


@router.get("/")
@require_permission("homework", "read")
async def list_homework(
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
        conditions.append("h.class_id = :class_id")
        params["class_id"] = class_id
    if subject_id:
        conditions.append("h.subject_id = :subject_id")
        params["subject_id"] = subject_id

    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    total = (await db.execute(text(f"SELECT COUNT(*) FROM homework h {where}"), params)).scalar()
    rows = await db.execute(text(f"""
        SELECT h.id, h.title, h.description, h.due_date,
               sub.name as subject, c.name as class_name,
               u.first_name || ' ' || u.last_name as teacher,
               h.created_at
        FROM homework h
        JOIN subjects sub ON sub.id = h.subject_id
        JOIN classes c ON c.id = h.class_id
        LEFT JOIN teachers t ON t.id = h.teacher_id
        LEFT JOIN users u ON u.id = t.user_id
        {where} ORDER BY h.due_date DESC LIMIT :limit OFFSET :offset
    """), params)
    return {"items": [dict(r._mapping) for r in rows], "total": total, "page": page}


@router.post("/", status_code=201)
@require_permission("homework", "create")
async def create_homework(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        INSERT INTO homework (title, description, class_id, subject_id, teacher_id, due_date, max_score)
        VALUES (:title, :description, :class_id, :subject_id, :teacher_id, :due_date, :max_score)
        RETURNING id
    """), {
        "title": data["title"], "description": data.get("description"),
        "class_id": data["class_id"], "subject_id": data["subject_id"],
        "teacher_id": data.get("teacher_id"), "due_date": data["due_date"],
        "max_score": data.get("max_score", 100),
    })
    await db.commit()
    return {"id": row.scalar(), "message": "Uy vazifasi yaratildi"}


@router.get("/{hw_id}")
@require_permission("homework", "read")
async def get_homework(
    hw_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        SELECT h.*, sub.name as subject, c.name as class_name,
               u.first_name || ' ' || u.last_name as teacher
        FROM homework h
        JOIN subjects sub ON sub.id = h.subject_id
        JOIN classes c ON c.id = h.class_id
        LEFT JOIN teachers t ON t.id = h.teacher_id
        LEFT JOIN users u ON u.id = t.user_id
        WHERE h.id = :id
    """), {"id": hw_id})
    hw = row.fetchone()
    if not hw:
        raise NotFoundError("Uy vazifasi")

    submissions = await db.execute(text("""
        SELECT hs.id, hs.student_id, su.first_name, su.last_name,
               hs.submitted_at, hs.score, hs.feedback
        FROM homework_submissions hs
        JOIN students s ON s.id = hs.student_id
        JOIN users su ON su.id = s.user_id
        WHERE hs.homework_id = :id
        ORDER BY hs.submitted_at
    """), {"id": hw_id})
    return {**dict(hw._mapping), "submissions": [dict(r._mapping) for r in submissions]}


@router.put("/{hw_id}")
@require_permission("homework", "update")
async def update_homework(
    hw_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        UPDATE homework SET title = COALESCE(:title, title),
            description = COALESCE(:description, description),
            due_date = COALESCE(:due_date, due_date),
            max_score = COALESCE(:max_score, max_score),
            updated_at = NOW()
        WHERE id = :id RETURNING id
    """), {**{k: data.get(k) for k in ("title", "description", "due_date", "max_score")}, "id": hw_id})
    if not result.fetchone():
        raise NotFoundError("Uy vazifasi")
    await db.commit()
    return {"message": "Uy vazifasi yangilandi"}


@router.delete("/{hw_id}")
@require_permission("homework", "delete")
async def delete_homework(
    hw_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("DELETE FROM homework WHERE id = :id RETURNING id"), {"id": hw_id})
    if not result.fetchone():
        raise NotFoundError("Uy vazifasi")
    await db.commit()
    return {"message": "Uy vazifasi o'chirildi"}


@router.post("/{hw_id}/submit", status_code=201)
@require_permission("homework", "create")
async def submit_homework(
    hw_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    check = await db.execute(text("SELECT id FROM homework WHERE id = :id"), {"id": hw_id})
    if not check.fetchone():
        raise NotFoundError("Uy vazifasi")

    row = await db.execute(text("""
        INSERT INTO homework_submissions (homework_id, student_id, content, file_path, submitted_at)
        VALUES (:hw_id, :student_id, :content, :file_path, NOW())
        ON CONFLICT (homework_id, student_id) DO UPDATE SET content = :content, file_path = :file_path, submitted_at = NOW()
        RETURNING id
    """), {
        "hw_id": hw_id, "student_id": data["student_id"],
        "content": data.get("content"), "file_path": data.get("file_path"),
    })
    await db.commit()
    return {"id": row.scalar(), "message": "Uy vazifasi topshirildi"}


@router.put("/submissions/{submission_id}/grade")
@require_permission("homework", "update")
async def grade_submission(
    submission_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        UPDATE homework_submissions SET score = :score, feedback = :feedback, graded_by = :graded_by, graded_at = NOW()
        WHERE id = :id RETURNING id
    """), {
        "score": data["score"], "feedback": data.get("feedback"),
        "graded_by": current_user["id"], "id": submission_id,
    })
    if not result.fetchone():
        raise NotFoundError("Topshiriq")
    await db.commit()
    return {"message": "Baho qo'yildi"}

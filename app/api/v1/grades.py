from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional

from app.core.dependencies import get_db, get_current_user
from app.core.rbac import require_permission
from app.core.exceptions import NotFoundError

router = APIRouter(tags=["Grades"])


@router.post(""), status_code=201)
@require_permission("grades", "create")
async def enter_grade(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        INSERT INTO grades (student_id, subject_id, teacher_id, score, grade_type, comment, graded_at)
        VALUES (:student_id, :subject_id, :teacher_id, :score, :grade_type, :comment, NOW())
        RETURNING id
    """), {
        "student_id": data["student_id"],
        "subject_id": data["subject_id"],
        "teacher_id": data.get("teacher_id"),
        "score": data["score"],
        "grade_type": data.get("grade_type", "assignment"),
        "comment": data.get("comment"),
    })
    await db.commit()
    return {"id": row.scalar(), "message": "Baho qo'yildi"}


@router.post("/bulk")
@require_permission("grades", "create")
async def bulk_grades(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    count = 0
    for g in data["grades"]:
        await db.execute(text("""
            INSERT INTO grades (student_id, subject_id, teacher_id, score, grade_type, comment, graded_at)
            VALUES (:student_id, :subject_id, :teacher_id, :score, :grade_type, :comment, NOW())
        """), {
            "student_id": g["student_id"],
            "subject_id": data.get("subject_id", g.get("subject_id")),
            "teacher_id": data.get("teacher_id", g.get("teacher_id")),
            "score": g["score"],
            "grade_type": data.get("grade_type", "assignment"),
            "comment": g.get("comment"),
        })
        count += 1
    await db.commit()
    return {"count": count, "message": f"{count} ta baho qo'yildi"}


@router.get("/mine")
async def my_grades(
    subject_id: Optional[int] = None,
    grade_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get grades for currently logged-in student."""
    student = await db.execute(
        text("SELECT id FROM students WHERE user_id = :uid AND status != 'deleted'"),
        {"uid": str(current_user["id"])},
    )
    s = student.fetchone()
    if not s:
        return {"grades": []}

    conditions = ["g.student_id = :student_id"]
    params: dict = {"student_id": s[0]}
    if subject_id:
        conditions.append("g.subject_id = :subject_id")
        params["subject_id"] = subject_id
    if grade_type:
        conditions.append("g.grade_type = :grade_type")
        params["grade_type"] = grade_type

    where = " AND ".join(conditions)
    rows = await db.execute(text(f"""
        SELECT g.id, g.score, g.grade_type, g.comment, g.graded_at,
               sub.name as subject, u.first_name || ' ' || u.last_name as teacher
        FROM grades g
        JOIN subjects sub ON sub.id = g.subject_id
        LEFT JOIN teachers t ON t.id = g.teacher_id
        LEFT JOIN users u ON u.id = t.user_id
        WHERE {where}
        ORDER BY g.graded_at DESC
    """), params)
    return {"grades": [dict(r._mapping) for r in rows]}


@router.get("/student/{student_id}")
@require_permission("grades", "read")
async def student_grades(
    student_id: int,
    subject_id: Optional[int] = None,
    grade_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conditions = ["g.student_id = :student_id"]
    params: dict = {"student_id": student_id}
    if subject_id:
        conditions.append("g.subject_id = :subject_id")
        params["subject_id"] = subject_id
    if grade_type:
        conditions.append("g.grade_type = :grade_type")
        params["grade_type"] = grade_type

    where = " AND ".join(conditions)
    rows = await db.execute(text(f"""
        SELECT g.id, g.score, g.grade_type, g.comment, g.graded_at,
               sub.name as subject, u.first_name || ' ' || u.last_name as teacher
        FROM grades g
        JOIN subjects sub ON sub.id = g.subject_id
        LEFT JOIN teachers t ON t.id = g.teacher_id
        LEFT JOIN users u ON u.id = t.user_id
        WHERE {where}
        ORDER BY g.graded_at DESC
    """), params)
    return {"grades": [dict(r._mapping) for r in rows]}


@router.get("/class/{class_id}/subject/{subject_id}")
@require_permission("grades", "read")
async def class_subject_grades(
    class_id: int,
    subject_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await db.execute(text("""
        SELECT s.id as student_id, u.first_name, u.last_name,
               ROUND(AVG(g.score), 1) as avg_score,
               COUNT(g.id) as grade_count,
               MAX(g.score) as max_score, MIN(g.score) as min_score
        FROM students s
        JOIN users u ON u.id = s.user_id
        LEFT JOIN grades g ON g.student_id = s.id AND g.subject_id = :subject_id
        WHERE s.current_class_id = :class_id AND s.status != 'deleted'
        GROUP BY s.id, u.first_name, u.last_name
        ORDER BY u.last_name
    """), {"class_id": class_id, "subject_id": subject_id})
    return {"grades": [dict(r._mapping) for r in rows]}


@router.get("/reports/ranking")
@require_permission("grades", "read")
async def ranking(
    class_id: Optional[int] = None,
    limit: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    where = ""
    params: dict = {"limit": limit}
    if class_id:
        where = "WHERE s.current_class_id = :class_id"
        params["class_id"] = class_id

    rows = await db.execute(text(f"""
        SELECT s.id, u.first_name, u.last_name, c.name as class_name,
               ROUND(AVG(g.score), 2) as avg_score,
               RANK() OVER (ORDER BY AVG(g.score) DESC) as rank
        FROM students s
        JOIN users u ON u.id = s.user_id
        LEFT JOIN classes c ON c.id = s.current_class_id
        JOIN grades g ON g.student_id = s.id
        {where}
        GROUP BY s.id, u.first_name, u.last_name, c.name
        ORDER BY avg_score DESC
        LIMIT :limit
    """), params)
    return {"ranking": [dict(r._mapping) for r in rows]}


@router.get("/report-cards/student/{student_id}")
@require_permission("grades", "read")
async def student_report_card(
    student_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    student = await db.execute(text("""
        SELECT s.id, u.first_name, u.last_name, c.name as class_name
        FROM students s JOIN users u ON u.id = s.user_id
        LEFT JOIN classes c ON c.id = s.current_class_id
        WHERE s.id = :id
    """), {"id": student_id})
    info = student.fetchone()
    if not info:
        raise NotFoundError("O'quvchi")

    subjects = await db.execute(text("""
        SELECT sub.name as subject,
               ROUND(AVG(g.score), 1) as avg_score,
               COUNT(g.id) as grade_count,
               ROUND(AVG(CASE WHEN g.grade_type = 'exam' THEN g.score END), 1) as exam_avg,
               ROUND(AVG(CASE WHEN g.grade_type = 'assignment' THEN g.score END), 1) as assignment_avg
        FROM grades g
        JOIN subjects sub ON sub.id = g.subject_id
        WHERE g.student_id = :id
        GROUP BY sub.name ORDER BY sub.name
    """), {"id": student_id})

    return {
        "student": dict(info._mapping),
        "subjects": [dict(r._mapping) for r in subjects],
    }


@router.post("/report-cards/generate")
@require_permission("grades", "create")
async def generate_report_cards(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    class_id = data.get("class_id")
    student_ids = data.get("student_ids", [])

    if class_id and not student_ids:
        rows = await db.execute(text("""
            SELECT id FROM students WHERE current_class_id = :cid AND status != 'deleted'
        """), {"cid": class_id})
        student_ids = [r[0] for r in rows]

    if not student_ids:
        return {"message": "O'quvchilar topilmadi", "count": 0}

    return {
        "message": f"{len(student_ids)} ta tabeldlar generatsiya qilish uchun navbatga qo'yildi",
        "student_ids": student_ids,
        "status": "queued",
    }

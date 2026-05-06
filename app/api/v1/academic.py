from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional

from app.core.dependencies import get_db, get_current_user
from app.core.rbac import require_permission
from app.core.exceptions import NotFoundError

router = APIRouter(tags=["Academic"])

# --- Academic Years ---

@router.get("/years")
@require_permission("academic", "view")
async def list_years(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await db.execute(text("""
        SELECT id, name, start_date, end_date, is_current, created_at
        FROM academic_years ORDER BY start_date DESC
    """))
    return {"items": [dict(r._mapping) for r in rows]}


@router.post("/years", status_code=201)
@require_permission("academic", "create")
async def create_year(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        INSERT INTO academic_years (name, start_date, end_date, is_current)
        VALUES (:name, :start_date, :end_date, :is_current) RETURNING id
    """), {
        "name": data["name"],
        "start_date": data["start_date"],
        "end_date": data["end_date"],
        "is_current": data.get("is_current", False),
    })
    await db.commit()
    return {"id": row.scalar(), "message": "O'quv yili yaratildi"}


@router.get("/years/{year_id}")
@require_permission("academic", "view")
async def get_year(
    year_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("SELECT * FROM academic_years WHERE id = :id"), {"id": year_id})
    year = row.fetchone()
    if not year:
        raise NotFoundError("O'quv yili")
    return dict(year._mapping)


@router.put("/years/{year_id}")
@require_permission("academic", "update")
async def update_year(
    year_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        UPDATE academic_years SET name = COALESCE(:name, name),
            start_date = COALESCE(:start_date, start_date),
            end_date = COALESCE(:end_date, end_date),
            is_current = COALESCE(:is_current, is_current),
            updated_at = NOW()
        WHERE id = :id RETURNING id
    """), {**{k: data.get(k) for k in ("name", "start_date", "end_date", "is_current")}, "id": year_id})
    if not result.fetchone():
        raise NotFoundError("O'quv yili")
    await db.commit()
    return {"message": "O'quv yili yangilandi"}


@router.delete("/years/{year_id}")
@require_permission("academic", "delete")
async def delete_year(
    year_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("DELETE FROM academic_years WHERE id = :id RETURNING id"), {"id": year_id})
    if not result.fetchone():
        raise NotFoundError("O'quv yili")
    await db.commit()
    return {"message": "O'quv yili o'chirildi"}


# --- Classes ---

@router.get("/classes")
@require_permission("academic", "view")
async def list_classes(
    year_id: Optional[int] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    where = ""
    params = {}
    if year_id:
        where = "WHERE c.academic_year_id = :year_id"
        params["year_id"] = year_id

    rows = await db.execute(text(f"""
        SELECT c.id, c.name, c.grade_level, c.section,
               u.first_name || ' ' || u.last_name as teacher_name,
               c.academic_year_id, c.capacity,
               (SELECT COUNT(*) FROM students s WHERE s.class_id = c.id AND s.deleted_at IS NULL) as student_count
        FROM classes c
        LEFT JOIN teachers t ON t.id = c.class_teacher_id
        LEFT JOIN users u ON u.id = t.user_id
        {where} ORDER BY c.grade_level, c.section
    """), params)
    return {"items": [dict(r._mapping) for r in rows]}


@router.post("/classes", status_code=201)
@require_permission("academic", "create")
async def create_class(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        INSERT INTO classes (name, grade_level, section, class_teacher_id, academic_year_id, capacity)
        VALUES (:name, :grade_level, :section, :class_teacher_id, :academic_year_id, :capacity)
        RETURNING id
    """), {
        "name": data["name"],
        "grade_level": data.get("grade_level"),
        "section": data.get("section"),
        "class_teacher_id": data.get("class_teacher_id"),
        "academic_year_id": data.get("academic_year_id"),
        "capacity": data.get("capacity", 30),
    })
    await db.commit()
    return {"id": row.scalar(), "message": "Sinf yaratildi"}


@router.get("/classes/{class_id}")
@require_permission("academic", "view")
async def get_class(
    class_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        SELECT c.*, u.first_name || ' ' || u.last_name as teacher_name
        FROM classes c
        LEFT JOIN teachers t ON t.id = c.class_teacher_id
        LEFT JOIN users u ON u.id = t.user_id
        WHERE c.id = :id
    """), {"id": class_id})
    cls = row.fetchone()
    if not cls:
        raise NotFoundError("Sinf")
    return dict(cls._mapping)


@router.put("/classes/{class_id}")
@require_permission("academic", "update")
async def update_class(
    class_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        UPDATE classes SET name = COALESCE(:name, name),
            grade_level = COALESCE(:grade_level, grade_level),
            section = COALESCE(:section, section),
            class_teacher_id = COALESCE(:class_teacher_id, class_teacher_id),
            capacity = COALESCE(:capacity, capacity),
            updated_at = NOW()
        WHERE id = :id RETURNING id
    """), {**{k: data.get(k) for k in ("name", "grade_level", "section", "class_teacher_id", "capacity")}, "id": class_id})
    if not result.fetchone():
        raise NotFoundError("Sinf")
    await db.commit()
    return {"message": "Sinf yangilandi"}


@router.delete("/classes/{class_id}")
@require_permission("academic", "delete")
async def delete_class(
    class_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("DELETE FROM classes WHERE id = :id RETURNING id"), {"id": class_id})
    if not result.fetchone():
        raise NotFoundError("Sinf")
    await db.commit()
    return {"message": "Sinf o'chirildi"}


# --- Subjects ---

@router.get("/subjects")
@require_permission("academic", "view")
async def list_subjects(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await db.execute(text("SELECT id, name, code, description, created_at FROM subjects ORDER BY name"))
    return {"items": [dict(r._mapping) for r in rows]}


@router.post("/subjects", status_code=201)
@require_permission("academic", "create")
async def create_subject(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        INSERT INTO subjects (name, code, description) VALUES (:name, :code, :description)
        RETURNING id
    """), {"name": data["name"], "code": data.get("code"), "description": data.get("description")})
    await db.commit()
    return {"id": row.scalar(), "message": "Fan yaratildi"}


@router.put("/subjects/{subject_id}")
@require_permission("academic", "update")
async def update_subject(
    subject_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        UPDATE subjects SET name = COALESCE(:name, name),
            code = COALESCE(:code, code),
            description = COALESCE(:description, description),
            updated_at = NOW()
        WHERE id = :id RETURNING id
    """), {**{k: data.get(k) for k in ("name", "code", "description")}, "id": subject_id})
    if not result.fetchone():
        raise NotFoundError("Fan")
    await db.commit()
    return {"message": "Fan yangilandi"}


@router.delete("/subjects/{subject_id}")
@require_permission("academic", "delete")
async def delete_subject(
    subject_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("DELETE FROM subjects WHERE id = :id RETURNING id"), {"id": subject_id})
    if not result.fetchone():
        raise NotFoundError("Fan")
    await db.commit()
    return {"message": "Fan o'chirildi"}


# --- Class Students ---

@router.get("/classes/{class_id}/students")
@require_permission("academic", "view")
async def class_students(
    class_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await db.execute(text("""
        SELECT s.id, s.student_code, u.first_name, u.last_name, u.phone
        FROM students s JOIN users u ON u.id = s.user_id
        WHERE s.class_id = :class_id AND s.deleted_at IS NULL
        ORDER BY u.last_name, u.first_name
    """), {"class_id": class_id})
    return {"students": [dict(r._mapping) for r in rows]}

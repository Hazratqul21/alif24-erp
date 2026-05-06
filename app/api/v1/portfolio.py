from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional

from app.core.dependencies import get_db, get_current_user
from app.core.rbac import require_permission
from app.core.exceptions import NotFoundError

router = APIRouter(tags=["Portfolio"])


# --- Student Portfolio ---

@router.get("/students")
@require_permission("portfolio", "view")
async def list_student_portfolios(
    student_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    params: dict = {"limit": per_page, "offset": (page - 1) * per_page}
    where = ""
    if student_id:
        where = "WHERE sp.student_id = :student_id"
        params["student_id"] = student_id

    rows = await db.execute(text(f"""
        SELECT sp.id, sp.student_id, u.first_name, u.last_name,
               sp.title, sp.category, sp.description, sp.file_path,
               sp.achievement_date, sp.created_at
        FROM student_portfolio sp
        JOIN students s ON s.id = sp.student_id
        JOIN users u ON u.id = s.user_id
        {where} ORDER BY sp.achievement_date DESC LIMIT :limit OFFSET :offset
    """), params)
    return {"items": [dict(r._mapping) for r in rows]}


@router.post("/students", status_code=201)
@require_permission("portfolio", "create")
async def create_student_portfolio(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        INSERT INTO student_portfolio (student_id, title, category, description, file_path, achievement_date, created_by)
        VALUES (:student_id, :title, :category, :description, :file_path, :achievement_date, :created_by)
        RETURNING id
    """), {
        "student_id": data["student_id"], "title": data["title"],
        "category": data.get("category", "general"),
        "description": data.get("description"), "file_path": data.get("file_path"),
        "achievement_date": data.get("achievement_date"),
        "created_by": current_user["id"],
    })
    await db.commit()
    return {"id": row.scalar(), "message": "Portfolio elementi qo'shildi"}


@router.get("/students/{item_id}")
@require_permission("portfolio", "view")
async def get_student_portfolio(
    item_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        SELECT sp.*, u.first_name, u.last_name
        FROM student_portfolio sp
        JOIN students s ON s.id = sp.student_id
        JOIN users u ON u.id = s.user_id
        WHERE sp.id = :id
    """), {"id": item_id})
    item = row.fetchone()
    if not item:
        raise NotFoundError("Portfolio elementi")
    return dict(item._mapping)


@router.put("/students/{item_id}")
@require_permission("portfolio", "update")
async def update_student_portfolio(
    item_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        UPDATE student_portfolio SET title = COALESCE(:title, title),
            category = COALESCE(:category, category),
            description = COALESCE(:description, description),
            file_path = COALESCE(:file_path, file_path),
            updated_at = NOW()
        WHERE id = :id RETURNING id
    """), {**{k: data.get(k) for k in ("title", "category", "description", "file_path")}, "id": item_id})
    if not result.fetchone():
        raise NotFoundError("Portfolio elementi")
    await db.commit()
    return {"message": "Portfolio elementi yangilandi"}


@router.delete("/students/{item_id}")
@require_permission("portfolio", "delete")
async def delete_student_portfolio(
    item_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("DELETE FROM student_portfolio WHERE id = :id RETURNING id"), {"id": item_id})
    if not result.fetchone():
        raise NotFoundError("Portfolio elementi")
    await db.commit()
    return {"message": "Portfolio elementi o'chirildi"}


# --- Teacher Development ---

@router.get("/teachers")
@require_permission("portfolio", "view")
async def list_teacher_development(
    teacher_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    params: dict = {"limit": per_page, "offset": (page - 1) * per_page}
    where = ""
    if teacher_id:
        where = "WHERE td.teacher_id = :teacher_id"
        params["teacher_id"] = teacher_id

    rows = await db.execute(text(f"""
        SELECT td.id, td.teacher_id, u.first_name, u.last_name,
               td.title, td.category, td.description, td.file_path,
               td.completion_date, td.certificate_number, td.created_at
        FROM teacher_development td
        JOIN teachers t ON t.id = td.teacher_id
        JOIN users u ON u.id = t.user_id
        {where} ORDER BY td.completion_date DESC LIMIT :limit OFFSET :offset
    """), params)
    return {"items": [dict(r._mapping) for r in rows]}


@router.post("/teachers", status_code=201)
@require_permission("portfolio", "create")
async def create_teacher_development(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        INSERT INTO teacher_development (teacher_id, title, category, description, file_path,
                                         completion_date, certificate_number, hours, created_by)
        VALUES (:teacher_id, :title, :category, :description, :file_path,
                :completion_date, :certificate_number, :hours, :created_by)
        RETURNING id
    """), {
        "teacher_id": data["teacher_id"], "title": data["title"],
        "category": data.get("category", "training"),
        "description": data.get("description"), "file_path": data.get("file_path"),
        "completion_date": data.get("completion_date"),
        "certificate_number": data.get("certificate_number"),
        "hours": data.get("hours"), "created_by": current_user["id"],
    })
    await db.commit()
    return {"id": row.scalar(), "message": "Rivojlanish yozuvi qo'shildi"}


@router.get("/teachers/{item_id}")
@require_permission("portfolio", "view")
async def get_teacher_development(
    item_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        SELECT td.*, u.first_name, u.last_name
        FROM teacher_development td
        JOIN teachers t ON t.id = td.teacher_id
        JOIN users u ON u.id = t.user_id
        WHERE td.id = :id
    """), {"id": item_id})
    item = row.fetchone()
    if not item:
        raise NotFoundError("Rivojlanish yozuvi")
    return dict(item._mapping)


@router.put("/teachers/{item_id}")
@require_permission("portfolio", "update")
async def update_teacher_development(
    item_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        UPDATE teacher_development SET title = COALESCE(:title, title),
            category = COALESCE(:category, category),
            description = COALESCE(:description, description),
            file_path = COALESCE(:file_path, file_path),
            updated_at = NOW()
        WHERE id = :id RETURNING id
    """), {**{k: data.get(k) for k in ("title", "category", "description", "file_path")}, "id": item_id})
    if not result.fetchone():
        raise NotFoundError("Rivojlanish yozuvi")
    await db.commit()
    return {"message": "Rivojlanish yozuvi yangilandi"}


@router.delete("/teachers/{item_id}")
@require_permission("portfolio", "delete")
async def delete_teacher_development(
    item_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("DELETE FROM teacher_development WHERE id = :id RETURNING id"), {"id": item_id})
    if not result.fetchone():
        raise NotFoundError("Rivojlanish yozuvi")
    await db.commit()
    return {"message": "Rivojlanish yozuvi o'chirildi"}

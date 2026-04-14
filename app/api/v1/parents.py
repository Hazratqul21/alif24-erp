from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional

from app.core.dependencies import get_db, get_current_user
from app.core.rbac import require_permission
from app.core.exceptions import NotFoundError

router = APIRouter(tags=["Parents"])


@router.get("/")
@require_permission("parents", "read")
async def list_parents(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    params: dict = {"limit": per_page, "offset": (page - 1) * per_page}
    where = "WHERE p.deleted_at IS NULL"
    if search:
        where += " AND (u.first_name ILIKE :search OR u.last_name ILIKE :search OR u.phone ILIKE :search)"
        params["search"] = f"%{search}%"

    total = (await db.execute(text(f"SELECT COUNT(*) FROM parents p JOIN users u ON u.id = p.user_id {where}"), params)).scalar()
    rows = await db.execute(text(f"""
        SELECT p.id, u.first_name, u.last_name, u.email, u.phone, p.occupation, p.created_at
        FROM parents p JOIN users u ON u.id = p.user_id
        {where} ORDER BY u.last_name LIMIT :limit OFFSET :offset
    """), params)
    return {"items": [dict(r._mapping) for r in rows], "total": total, "page": page, "per_page": per_page}


@router.post("/", status_code=201)
@require_permission("parents", "create")
async def create_parent(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_res = await db.execute(text("""
        INSERT INTO users (email, phone, first_name, last_name, password_hash, is_active)
        VALUES (:email, :phone, :first_name, :last_name, :password_hash, true)
        RETURNING id
    """), {
        "email": data.get("email"),
        "phone": data["phone"],
        "first_name": data["first_name"],
        "last_name": data["last_name"],
        "password_hash": data.get("password_hash", "changeme_hashed"),
    })
    user_id = user_res.scalar()

    parent_res = await db.execute(text("""
        INSERT INTO parents (user_id, occupation, address)
        VALUES (:user_id, :occupation, :address) RETURNING id
    """), {"user_id": user_id, "occupation": data.get("occupation"), "address": data.get("address")})
    parent_id = parent_res.scalar()

    await db.execute(text("""
        INSERT INTO user_roles (user_id, role_id)
        SELECT :uid, id FROM roles WHERE name = 'parent'
    """), {"uid": user_id})

    await db.commit()
    return {"id": parent_id, "user_id": user_id, "message": "Ota-ona muvaffaqiyatli yaratildi"}


@router.get("/{parent_id}")
@require_permission("parents", "read")
async def get_parent(
    parent_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        SELECT p.id, u.first_name, u.last_name, u.email, u.phone, p.occupation, p.address
        FROM parents p JOIN users u ON u.id = p.user_id
        WHERE p.id = :id AND p.deleted_at IS NULL
    """), {"id": parent_id})
    parent = row.fetchone()
    if not parent:
        raise NotFoundError("Ota-ona")

    children_q = await db.execute(text("""
        SELECT s.id, su.first_name, su.last_name, c.name as class_name
        FROM parent_students ps
        JOIN students s ON s.id = ps.student_id
        JOIN users su ON su.id = s.user_id
        LEFT JOIN classes c ON c.id = s.class_id
        WHERE ps.parent_id = :pid
    """), {"pid": parent_id})

    return {**dict(parent._mapping), "children": [dict(r._mapping) for r in children_q]}


@router.get("/{parent_id}/children")
@require_permission("parents", "read")
async def list_children(
    parent_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await db.execute(text("""
        SELECT s.id, su.first_name, su.last_name, s.student_code, c.name as class_name
        FROM parent_students ps
        JOIN students s ON s.id = ps.student_id
        JOIN users su ON su.id = s.user_id
        LEFT JOIN classes c ON c.id = s.class_id
        WHERE ps.parent_id = :pid
    """), {"pid": parent_id})
    return {"children": [dict(r._mapping) for r in rows]}


@router.post("/{parent_id}/children")
@require_permission("parents", "update")
async def link_child(
    parent_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    check = await db.execute(text("SELECT id FROM parents WHERE id = :id AND deleted_at IS NULL"), {"id": parent_id})
    if not check.fetchone():
        raise NotFoundError("Ota-ona")

    student_check = await db.execute(text("SELECT id FROM students WHERE id = :id AND deleted_at IS NULL"), {"id": data["student_id"]})
    if not student_check.fetchone():
        raise NotFoundError("O'quvchi")

    await db.execute(text("""
        INSERT INTO parent_students (parent_id, student_id, relationship)
        VALUES (:pid, :sid, :rel) ON CONFLICT DO NOTHING
    """), {"pid": parent_id, "sid": data["student_id"], "rel": data.get("relationship", "parent")})
    await db.commit()
    return {"message": "Farzand bog'landi"}

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.dependencies import get_db, get_current_user
from app.core.rbac import check_permission
from app.core.exceptions import (
    NotFoundError,
    ForbiddenError,
    ConflictError,
    ValidationError,
)

from pydantic import BaseModel
from typing import Optional

router = APIRouter(tags=["Roles & Permissions"])


class RoleCreate(BaseModel):
    name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    level: int = 0


class RoleUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    level: Optional[int] = None


class RoleResponse(BaseModel):
    id: int
    name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    level: int = 0
    is_system: bool = False

    model_config = {"from_attributes": True}


class PermissionResponse(BaseModel):
    id: int
    name: str
    module: str
    action: str
    description: Optional[str] = None

    model_config = {"from_attributes": True}


class AssignPermissionsRequest(BaseModel):
    permission_ids: list[int]


class RolePermissionResponse(BaseModel):
    permission_id: int
    name: str
    module: str
    action: str
    allowed: bool = True

    model_config = {"from_attributes": True}


# ─── Roles ───────────────────────────────────────────────


@router.get("/roles", response_model=list[RoleResponse])
async def list_roles(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await db.execute(
        text("SELECT id, name, display_name, description, level, is_system FROM roles ORDER BY level")
    )
    rows = result.fetchall()

    return [
        RoleResponse(
            id=row[0],
            name=row[1],
            display_name=row[2],
            description=row[3],
            level=row[4],
            is_system=row[5],
        )
        for row in rows
    ]


@router.post("/roles", response_model=RoleResponse, status_code=201)
async def create_role(
    body: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    admin_roles = {"super_admin", "director", "administrator"}
    if not set(current_user.get("roles", [])).intersection(admin_roles):
        raise ForbiddenError("Rol yaratish uchun administrator huquqi kerak")

    dup = await db.execute(
        text("SELECT id FROM roles WHERE name = :name"),
        {"name": body.name},
    )
    if dup.fetchone():
        raise ConflictError("Bu nomdagi rol allaqachon mavjud")

    result = await db.execute(
        text("""
            INSERT INTO roles (name, display_name, description, level, is_system, created_at)
            VALUES (:name, :dn, :desc, :level, false, NOW())
            RETURNING id, name, display_name, description, level, is_system
        """),
        {
            "name": body.name,
            "dn": body.display_name or body.name,
            "desc": body.description,
            "level": body.level,
        },
    )
    row = result.fetchone()
    await db.commit()

    return RoleResponse(
        id=row[0],
        name=row[1],
        display_name=row[2],
        description=row[3],
        level=row[4],
        is_system=row[5],
    )


@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    body: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    admin_roles = {"super_admin", "director", "administrator"}
    if not set(current_user.get("roles", [])).intersection(admin_roles):
        raise ForbiddenError("Rolni tahrirlash uchun administrator huquqi kerak")

    result = await db.execute(
        text("SELECT id, is_system FROM roles WHERE id = :rid"),
        {"rid": role_id},
    )
    role_row = result.fetchone()
    if not role_row:
        raise NotFoundError("Rol")

    if role_row[1]:
        raise ValidationError("Tizim rollarini o'zgartirish mumkin emas")

    updates = body.model_dump(exclude_unset=True)
    if not updates:
        raise ValidationError("Hech qanday o'zgartirish ko'rsatilmagan")

    set_parts = []
    params = {"rid": role_id}
    for key, val in updates.items():
        set_parts.append(f"{key} = :{key}")
        params[key] = val

    set_clause = ", ".join(set_parts)

    await db.execute(
        text(f"UPDATE roles SET {set_clause} WHERE id = :rid"),
        params,
    )
    await db.commit()

    result = await db.execute(
        text("SELECT id, name, display_name, description, level, is_system FROM roles WHERE id = :rid"),
        {"rid": role_id},
    )
    row = result.fetchone()

    return RoleResponse(
        id=row[0],
        name=row[1],
        display_name=row[2],
        description=row[3],
        level=row[4],
        is_system=row[5],
    )


# ─── Permissions ─────────────────────────────────────────


@router.get("/permissions", response_model=list[PermissionResponse])
async def list_permissions(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await db.execute(
        text("SELECT id, name, module, action, description FROM permissions ORDER BY module, action")
    )
    rows = result.fetchall()

    return [
        PermissionResponse(
            id=row[0],
            name=row[1],
            module=row[2],
            action=row[3],
            description=row[4],
        )
        for row in rows
    ]


@router.post("/roles/{role_id}/permissions")
async def assign_permissions(
    role_id: int,
    body: AssignPermissionsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    admin_roles = {"super_admin", "director", "administrator"}
    if not set(current_user.get("roles", [])).intersection(admin_roles):
        raise ForbiddenError("Ruxsat belgilash uchun administrator huquqi kerak")

    role_check = await db.execute(
        text("SELECT id FROM roles WHERE id = :rid"),
        {"rid": role_id},
    )
    if not role_check.fetchone():
        raise NotFoundError("Rol")

    await db.execute(
        text("DELETE FROM role_permissions WHERE role_id = :rid"),
        {"rid": role_id},
    )

    assigned = 0
    for perm_id in body.permission_ids:
        perm_check = await db.execute(
            text("SELECT id FROM permissions WHERE id = :pid"),
            {"pid": perm_id},
        )
        if perm_check.fetchone():
            await db.execute(
                text("""
                    INSERT INTO role_permissions (role_id, permission_id, allowed)
                    VALUES (:rid, :pid, true)
                    ON CONFLICT DO NOTHING
                """),
                {"rid": role_id, "pid": perm_id},
            )
            assigned += 1

    await db.commit()

    return {"detail": f"{assigned} ta ruxsat muvaffaqiyatli belgilandi"}


@router.get("/roles/{role_id}/permissions", response_model=list[RolePermissionResponse])
async def get_role_permissions(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    role_check = await db.execute(
        text("SELECT id FROM roles WHERE id = :rid"),
        {"rid": role_id},
    )
    if not role_check.fetchone():
        raise NotFoundError("Rol")

    result = await db.execute(
        text("""
            SELECT p.id, p.name, p.module, p.action, rp.allowed
            FROM permissions p
            JOIN role_permissions rp ON rp.permission_id = p.id
            WHERE rp.role_id = :rid
            ORDER BY p.module, p.action
        """),
        {"rid": role_id},
    )
    rows = result.fetchall()

    return [
        RolePermissionResponse(
            permission_id=row[0],
            name=row[1],
            module=row[2],
            action=row[3],
            allowed=row[4],
        )
        for row in rows
    ]

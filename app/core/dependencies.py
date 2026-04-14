from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional

from app.core.database import AsyncSessionLocal, Alif24SessionLocal
from app.core.exceptions import UnauthorizedError, TenantNotFoundError
from app.core.auth import decode_access_token


async def get_db(request: Request) -> AsyncSession:
    async with AsyncSessionLocal() as session:
        schema = getattr(request.state, "schema_name", "public")
        if schema != "public":
            await session.execute(text(f"SET search_path TO {schema}, public"))
        try:
            yield session
        finally:
            await session.close()


async def get_public_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        await session.execute(text("SET search_path TO public"))
        try:
            yield session
        finally:
            await session.close()


async def get_alif24_db() -> Optional[AsyncSession]:
    if Alif24SessionLocal is None:
        yield None
        return
    async with Alif24SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_tenant(request: Request) -> dict:
    tenant = getattr(request.state, "tenant", None)
    if tenant is None:
        raise TenantNotFoundError()
    return tenant


def get_tenant_id(request: Request) -> int:
    tenant = get_tenant(request)
    return tenant["id"]


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict:
    token = None

    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]

    if not token:
        token = request.cookies.get("access_token")

    if not token:
        raise UnauthorizedError()

    payload = decode_access_token(token)
    if payload is None:
        raise UnauthorizedError("Token yaroqsiz yoki muddati tugagan")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedError()

    # Super Admin (token sub = "sa_<id>")
    if str(user_id).startswith("sa_"):
        sa_id = int(str(user_id).replace("sa_", ""))
        sa_result = await db.execute(
            text("SELECT id, email, first_name, last_name, is_active FROM public.super_admins WHERE id = :uid"),
            {"uid": sa_id},
        )
        sa_row = sa_result.fetchone()
        if not sa_row:
            raise UnauthorizedError("Super Admin topilmadi")
        if not sa_row[4]:
            raise UnauthorizedError("Hisob faol emas")

        return {
            "id": user_id,
            "email": sa_row[1],
            "phone": None,
            "first_name": sa_row[2] or "Super",
            "last_name": sa_row[3] or "Admin",
            "is_active": sa_row[4],
            "roles": ["superadmin"],
            "permissions": [{"module": "*", "action": "*"}],
            "tenant_id": None,
        }

    # Tenant user
    result = await db.execute(
        text("SELECT id, email, phone, first_name, last_name, is_active FROM users WHERE id = :uid"),
        {"uid": user_id},
    )
    user_row = result.fetchone()
    if not user_row:
        raise UnauthorizedError("Foydalanuvchi topilmadi")

    if not user_row[5]:
        raise UnauthorizedError("Hisob faol emas")

    roles_result = await db.execute(
        text("""
            SELECT r.name FROM roles r
            JOIN user_roles ur ON ur.role_id = r.id
            WHERE ur.user_id = :uid
        """),
        {"uid": user_id},
    )
    roles = [row[0] for row in roles_result]

    permissions_result = await db.execute(
        text("""
            SELECT DISTINCT p.module, p.action FROM permissions p
            JOIN role_permissions rp ON rp.permission_id = p.id
            JOIN user_roles ur ON ur.role_id = rp.role_id
            WHERE ur.user_id = :uid AND rp.allowed = true
        """),
        {"uid": user_id},
    )
    permissions = [{"module": row[0], "action": row[1]} for row in permissions_result]

    return {
        "id": user_row[0],
        "email": user_row[1],
        "phone": user_row[2],
        "first_name": user_row[3],
        "last_name": user_row[4],
        "is_active": user_row[5],
        "roles": roles,
        "permissions": permissions,
        "tenant_id": getattr(request.state, "tenant_id", None),
    }


async def get_optional_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Optional[dict]:
    try:
        return await get_current_user(request, db)
    except UnauthorizedError:
        return None

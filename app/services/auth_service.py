import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, or_, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import hash_password, verify_password
from app.core.database import generate_uuid
from app.core.exceptions import (
    ConflictError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)

logger = logging.getLogger(__name__)


async def authenticate_user(
    db: AsyncSession,
    email_or_phone: str,
    password: str,
) -> Optional[dict]:
    result = await db.execute(
        text(
            "SELECT id, email, phone, password_hash, first_name, last_name, "
            "middle_name, is_active, totp_enabled, totp_secret, deleted_at "
            "FROM users "
            "WHERE (email = :login OR phone = :login) AND deleted_at IS NULL"
        ),
        {"login": email_or_phone},
    )
    row = result.fetchone()

    if row is None:
        return None

    user = dict(row._mapping)

    if not user["is_active"]:
        raise UnauthorizedError("Foydalanuvchi bloklangan")

    if not verify_password(password, user["password_hash"]):
        return None

    await db.execute(
        text("UPDATE users SET last_login = :now WHERE id = :uid"),
        {"now": datetime.now(timezone.utc), "uid": user["id"]},
    )
    await db.commit()

    user.pop("password_hash", None)
    return user


async def get_user_by_id(db: AsyncSession, user_id: str) -> dict:
    result = await db.execute(
        text(
            "SELECT u.id, u.email, u.phone, u.first_name, u.last_name, "
            "u.middle_name, u.birth_date, u.gender, u.avatar, u.is_active, "
            "u.totp_enabled, u.last_login, u.created_at, u.deleted_at "
            "FROM users u WHERE u.id = :uid AND u.deleted_at IS NULL"
        ),
        {"uid": user_id},
    )
    row = result.fetchone()
    if row is None:
        raise NotFoundError("Foydalanuvchi")

    user = dict(row._mapping)

    roles_result = await db.execute(
        text(
            "SELECT r.name, r.display_name "
            "FROM user_roles ur "
            "JOIN roles r ON r.id = ur.role_id "
            "WHERE ur.user_id = :uid"
        ),
        {"uid": user_id},
    )
    user["roles"] = [dict(r._mapping) for r in roles_result.fetchall()]

    return user


async def create_user(db: AsyncSession, data: dict) -> dict:
    if data.get("email"):
        dup = await db.execute(
            text(
                "SELECT id FROM users WHERE email = :email AND deleted_at IS NULL"
            ),
            {"email": data["email"]},
        )
        if dup.fetchone():
            raise ConflictError("Bu email allaqachon ro'yxatdan o'tgan")

    if data.get("phone"):
        dup = await db.execute(
            text(
                "SELECT id FROM users WHERE phone = :phone AND deleted_at IS NULL"
            ),
            {"phone": data["phone"]},
        )
        if dup.fetchone():
            raise ConflictError("Bu telefon raqam allaqachon ro'yxatdan o'tgan")

    if not data.get("password"):
        raise ValidationError("Parol majburiy")

    user_id = generate_uuid()
    password_hash = hash_password(data["password"])

    await db.execute(
        text(
            "INSERT INTO users "
            "(id, email, phone, password_hash, first_name, last_name, "
            "middle_name, birth_date, gender, is_active) "
            "VALUES (:id, :email, :phone, :password_hash, :first_name, "
            ":last_name, :middle_name, :birth_date, :gender, true)"
        ),
        {
            "id": user_id,
            "email": data.get("email"),
            "phone": data.get("phone"),
            "password_hash": password_hash,
            "first_name": data.get("first_name", ""),
            "last_name": data.get("last_name", ""),
            "middle_name": data.get("middle_name"),
            "birth_date": data.get("birth_date"),
            "gender": data.get("gender"),
        },
    )

    if data.get("role_id"):
        await db.execute(
            text(
                "INSERT INTO user_roles (user_id, role_id) "
                "VALUES (:user_id, :role_id)"
            ),
            {"user_id": user_id, "role_id": data["role_id"]},
        )

    await db.commit()

    return await get_user_by_id(db, user_id)


async def update_password(
    db: AsyncSession,
    user_id: str,
    new_password: str,
) -> None:
    result = await db.execute(
        text("SELECT id FROM users WHERE id = :uid AND deleted_at IS NULL"),
        {"uid": user_id},
    )
    if not result.fetchone():
        raise NotFoundError("Foydalanuvchi")

    password_hash = hash_password(new_password)
    await db.execute(
        text("UPDATE users SET password_hash = :hash WHERE id = :uid"),
        {"hash": password_hash, "uid": user_id},
    )
    await db.commit()
    logger.info(f"Password updated for user {user_id}")

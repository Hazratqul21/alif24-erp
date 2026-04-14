"""
Super Admin yaratish skripti.
Ishlatish: docker exec erp-backend python scripts/create_superadmin.py
"""
import asyncio
import os
import sys

sys.path.insert(0, "/app")

from sqlalchemy import text
from app.core.database import AsyncSessionLocal, engine, init_public_schema
from app.core.auth import hash_password


async def create_superadmin():
    email = os.getenv("SUPER_ADMIN_EMAIL", "admin@alif24.uz")
    password = os.getenv("SUPER_ADMIN_PASSWORD", "changeme")

    await init_public_schema()

    async with AsyncSessionLocal() as db:
        await db.execute(text("SET search_path TO public"))

        existing = await db.execute(
            text("SELECT id FROM super_admins WHERE email = :email"),
            {"email": email},
        )
        if existing.fetchone():
            print(f"Super Admin allaqachon mavjud: {email}")
            return

        password_hash = hash_password(password)

        await db.execute(
            text("""
                INSERT INTO super_admins (email, password_hash, first_name, last_name, is_active)
                VALUES (:email, :password_hash, 'Super', 'Admin', true)
            """),
            {"email": email, "password_hash": password_hash},
        )
        await db.commit()

        print(f"Super Admin yaratildi!")
        print(f"  Email: {email}")
        print(f"  Parol: {password}")


if __name__ == "__main__":
    asyncio.run(create_superadmin())

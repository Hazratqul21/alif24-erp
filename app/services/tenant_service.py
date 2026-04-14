import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, func, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import hash_password
from app.core.database import (
    create_tenant_schema,
    create_tenant_tables,
    generate_uuid,
)
from app.core.exceptions import (
    ConflictError,
    NotFoundError,
    TenantNotFoundError,
    ValidationError,
)
from app.models.public.tenant import Tenant
from app.models.tenant.role import (
    DEFAULT_PERMISSIONS,
    DEFAULT_ROLES,
    Permission,
    Role,
    UserRole,
)
from app.models.tenant.user import User

logger = logging.getLogger(__name__)


async def create_tenant(db: AsyncSession, data: dict) -> Tenant:
    existing = await db.execute(
        select(Tenant).where(Tenant.subdomain == data["subdomain"])
    )
    if existing.scalar_one_or_none():
        raise ConflictError("Bu subdomain allaqachon band")

    tenant = Tenant(
        subdomain=data["subdomain"],
        name=data["name"],
        logo=data.get("logo"),
        address=data.get("address"),
        phone=data.get("phone"),
        email=data.get("email"),
        plan_id=data.get("plan_id"),
        max_users=data.get("max_users", 100),
        max_students=data.get("max_students", 500),
        subscription_end=data.get("subscription_end"),
    )
    db.add(tenant)
    await db.flush()

    await create_tenant_schema(db, tenant.id)
    await create_tenant_tables(tenant.id)

    try:
        await _seed_roles_and_permissions(db, tenant.id)
    except Exception as e:
        logger.error(f"Tenant {tenant.id} role seed error: {e}")
        raise

    director_data = data.get("director")
    if director_data:
        try:
            await _create_director_user(db, tenant.id, director_data)
        except Exception as e:
            logger.error(f"Tenant {tenant.id} director creation error: {e}")
            raise

    await db.commit()
    await db.refresh(tenant)
    logger.info(f"Tenant created: id={tenant.id}, subdomain={tenant.subdomain}")
    return tenant


async def get_tenant(db: AsyncSession, tenant_id: int) -> Tenant:
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise TenantNotFoundError()
    return tenant


async def update_tenant(db: AsyncSession, tenant_id: int, data: dict) -> Tenant:
    tenant = await get_tenant(db, tenant_id)

    if "subdomain" in data and data["subdomain"] != tenant.subdomain:
        dup = await db.execute(
            select(Tenant).where(
                Tenant.subdomain == data["subdomain"],
                Tenant.id != tenant_id,
            )
        )
        if dup.scalar_one_or_none():
            raise ConflictError("Bu subdomain allaqachon band")

    updatable = [
        "name", "subdomain", "logo", "address", "phone",
        "email", "plan_id", "max_users", "max_students",
        "subscription_end",
    ]
    for field in updatable:
        if field in data:
            setattr(tenant, field, data[field])

    await db.commit()
    await db.refresh(tenant)
    return tenant


async def block_tenant(db: AsyncSession, tenant_id: int) -> Tenant:
    tenant = await get_tenant(db, tenant_id)
    tenant.is_active = False
    await db.commit()
    await db.refresh(tenant)
    logger.info(f"Tenant blocked: id={tenant_id}")
    return tenant


async def unblock_tenant(db: AsyncSession, tenant_id: int) -> Tenant:
    tenant = await get_tenant(db, tenant_id)
    tenant.is_active = True
    await db.commit()
    await db.refresh(tenant)
    logger.info(f"Tenant unblocked: id={tenant_id}")
    return tenant


async def delete_tenant(db: AsyncSession, tenant_id: int) -> Tenant:
    tenant = await get_tenant(db, tenant_id)
    tenant.is_active = False
    await db.commit()
    await db.refresh(tenant)
    logger.info(f"Tenant soft-deleted: id={tenant_id}")
    return tenant


async def list_tenants(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 20,
    search: Optional[str] = None,
) -> dict:
    query = select(Tenant)
    count_query = select(func.count(Tenant.id))

    if search:
        like_pattern = f"%{search}%"
        filter_cond = Tenant.name.ilike(like_pattern) | Tenant.subdomain.ilike(
            like_pattern
        )
        query = query.where(filter_cond)
        count_query = count_query.where(filter_cond)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    offset = (page - 1) * per_page
    query = query.order_by(Tenant.created_at.desc()).offset(offset).limit(per_page)

    result = await db.execute(query)
    tenants = result.scalars().all()

    return {
        "items": tenants,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page if per_page else 0,
    }


async def _seed_roles_and_permissions(db: AsyncSession, tenant_id: int) -> None:
    schema = f"tenant_{tenant_id}"

    for role_data in DEFAULT_ROLES:
        await db.execute(
            text(
                f"INSERT INTO {schema}.roles (name, display_name, level, is_system) "
                f"VALUES (:name, :display_name, :level, :is_system) "
                f"ON CONFLICT (name) DO NOTHING"
            ),
            role_data,
        )

    for perm_data in DEFAULT_PERMISSIONS:
        await db.execute(
            text(
                f"INSERT INTO {schema}.permissions (name, module, action) "
                f"VALUES (:name, :module, :action) "
                f"ON CONFLICT (name) DO NOTHING"
            ),
            perm_data,
        )

    await db.flush()


async def _create_director_user(
    db: AsyncSession, tenant_id: int, director_data: dict
) -> None:
    schema = f"tenant_{tenant_id}"
    user_id = generate_uuid()

    if not director_data.get("password"):
        raise ValidationError("Direktor paroli majburiy")

    password_hash = hash_password(director_data["password"])

    await db.execute(
        text(
            f"INSERT INTO {schema}.users "
            f"(id, email, phone, password_hash, first_name, last_name, is_active) "
            f"VALUES (:id, :email, :phone, :password_hash, :first_name, :last_name, true)"
        ),
        {
            "id": user_id,
            "email": director_data.get("email"),
            "phone": director_data.get("phone"),
            "password_hash": password_hash,
            "first_name": director_data.get("first_name", ""),
            "last_name": director_data.get("last_name", ""),
        },
    )

    role_result = await db.execute(
        text(f"SELECT id FROM {schema}.roles WHERE name = 'director'")
    )
    role_row = role_result.fetchone()
    if role_row:
        await db.execute(
            text(
                f"INSERT INTO {schema}.user_roles (user_id, role_id) "
                f"VALUES (:user_id, :role_id)"
            ),
            {"user_id": user_id, "role_id": role_row[0]},
        )

    await db.flush()

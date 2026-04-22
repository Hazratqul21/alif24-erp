from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional

from app.core.dependencies import get_public_db, get_current_user
from app.core.rbac import require_role
from app.core.exceptions import NotFoundError, AppError

router = APIRouter(tags=["SuperAdmin - Tenants"])


@router.get("")
@require_role("super_admin")
async def list_tenants(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_public_db),
):
    params: dict = {"limit": per_page, "offset": (page - 1) * per_page}
    conditions = ["t.deleted_at IS NULL"]
    if search:
        conditions.append("(t.name ILIKE :search OR t.domain ILIKE :search)")
        params["search"] = f"%{search}%"
    if is_active is not None:
        conditions.append("t.is_active = :is_active")
        params["is_active"] = is_active

    where = "WHERE " + " AND ".join(conditions)
    total = (await db.execute(text(f"SELECT COUNT(*) FROM tenants t {where}"), params)).scalar()

    rows = await db.execute(text(f"""
        SELECT t.id, t.name, t.domain, t.schema_name, t.is_active, t.is_blocked,
               t.plan_id, t.subscription_end, t.created_at
        FROM tenants t {where}
        ORDER BY t.created_at DESC LIMIT :limit OFFSET :offset
    """), params)
    items = [dict(r._mapping) for r in rows]

    # user_count: get per-schema counts safely (skip schemas that don't exist yet)
    for item in items:
        schema = item.get("schema_name")
        if not schema or not schema.replace("_", "").isalnum():
            item["user_count"] = 0
            continue
        try:
            cnt = (await db.execute(text(f"SELECT COUNT(*) FROM {schema}.users"))).scalar()
            item["user_count"] = cnt or 0
        except Exception:
            item["user_count"] = 0

    return {"items": items, "total": total, "page": page, "per_page": per_page}


@router.post("", status_code=201)
@require_role("super_admin")
async def create_tenant(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_public_db),
):
    schema_name = data.get("schema_name", f"tenant_{data['name'].lower().replace(' ', '_')}")

    row = await db.execute(text("""
        INSERT INTO tenants (name, domain, schema_name, is_active, plan_id, subscription_end,
                             admin_email, admin_phone, address, region)
        VALUES (:name, :domain, :schema_name, true, :plan_id, :subscription_end,
                :admin_email, :admin_phone, :address, :region)
        RETURNING id
    """), {
        "name": data["name"], "domain": data.get("domain"),
        "schema_name": schema_name, "plan_id": data.get("plan_id"),
        "subscription_end": data.get("subscription_end"),
        "admin_email": data.get("admin_email"), "admin_phone": data.get("admin_phone"),
        "address": data.get("address"), "region": data.get("region"),
    })
    tenant_id = row.scalar()

    await db.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
    await db.commit()

    return {"id": tenant_id, "schema_name": schema_name, "message": "Tenant yaratildi va schema tayyorlandi"}


@router.get("/{tenant_id}")
@require_role("super_admin")
async def get_tenant(
    tenant_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_public_db),
):
    row = await db.execute(text("SELECT * FROM tenants WHERE id = :id"), {"id": tenant_id})
    tenant = row.fetchone()
    if not tenant:
        raise NotFoundError("Tenant")
    return dict(tenant._mapping)


@router.put("/{tenant_id}")
@require_role("super_admin")
async def update_tenant(
    tenant_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_public_db),
):
    result = await db.execute(text("""
        UPDATE tenants SET name = COALESCE(:name, name),
            domain = COALESCE(:domain, domain),
            plan_id = COALESCE(:plan_id, plan_id),
            subscription_end = COALESCE(:subscription_end, subscription_end),
            admin_email = COALESCE(:admin_email, admin_email),
            admin_phone = COALESCE(:admin_phone, admin_phone),
            address = COALESCE(:address, address),
            region = COALESCE(:region, region),
            updated_at = NOW()
        WHERE id = :id RETURNING id
    """), {
        **{k: data.get(k) for k in ("name", "domain", "plan_id", "subscription_end",
                                      "admin_email", "admin_phone", "address", "region")},
        "id": tenant_id,
    })
    if not result.fetchone():
        raise NotFoundError("Tenant")
    await db.commit()
    return {"message": "Tenant yangilandi"}


@router.put("/{tenant_id}/block")
@require_role("super_admin")
async def block_tenant(
    tenant_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_public_db),
):
    result = await db.execute(text("""
        UPDATE tenants SET is_blocked = true, is_active = false, updated_at = NOW()
        WHERE id = :id RETURNING id
    """), {"id": tenant_id})
    if not result.fetchone():
        raise NotFoundError("Tenant")
    await db.commit()
    return {"message": "Tenant bloklandi"}


@router.put("/{tenant_id}/unblock")
@require_role("super_admin")
async def unblock_tenant(
    tenant_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_public_db),
):
    result = await db.execute(text("""
        UPDATE tenants SET is_blocked = false, is_active = true, updated_at = NOW()
        WHERE id = :id RETURNING id
    """), {"id": tenant_id})
    if not result.fetchone():
        raise NotFoundError("Tenant")
    await db.commit()
    return {"message": "Tenant blokdan chiqarildi"}


@router.delete("/{tenant_id}")
@require_role("super_admin")
async def delete_tenant(
    tenant_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_public_db),
):
    result = await db.execute(text("""
        UPDATE tenants SET is_active = false, deleted_at = NOW()
        WHERE id = :id AND deleted_at IS NULL RETURNING id
    """), {"id": tenant_id})
    if not result.fetchone():
        raise NotFoundError("Tenant")
    await db.commit()
    return {"message": "Tenant o'chirildi"}

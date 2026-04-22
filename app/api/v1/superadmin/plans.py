from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.dependencies import get_public_db, get_current_user
from app.core.rbac import require_role
from app.core.exceptions import NotFoundError

router = APIRouter(tags=["SuperAdmin - Plans"])


@router.get("")
@require_role("super_admin")
async def list_plans(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_public_db),
):
    rows = await db.execute(text("""
        SELECT sp.id, sp.name, sp.description, sp.price_monthly, sp.price_yearly,
               sp.max_students, sp.max_teachers,
               sp.is_active, sp.created_at,
               (SELECT COUNT(*) FROM tenants t WHERE t.plan_id = sp.id) as tenant_count
        FROM plans sp
        ORDER BY sp.price_monthly
    """))
    return {"items": [dict(r._mapping) for r in rows]}


@router.post("", status_code=201)
@require_role("super_admin")
async def create_plan(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_public_db),
):
    row = await db.execute(text("""
        INSERT INTO plans (name, description, price_monthly, price_yearly,
                           max_students, max_teachers, is_active)
        VALUES (:name, :description, :price_monthly, :price_yearly,
                :max_students, :max_teachers, :is_active)
        RETURNING id
    """), {
        "name": data["name"], "description": data.get("description"),
        "price_monthly": data["price_monthly"], "price_yearly": data.get("price_yearly"),
        "max_students": data.get("max_students"), "max_teachers": data.get("max_teachers"),
        "is_active": data.get("is_active", True),
    })
    await db.commit()
    return {"id": row.scalar(), "message": "Obuna rejasi yaratildi"}


@router.get("/{plan_id}")
@require_role("super_admin")
async def get_plan(
    plan_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_public_db),
):
    row = await db.execute(text("SELECT * FROM plans WHERE id = :id"), {"id": plan_id})
    plan = row.fetchone()
    if not plan:
        raise NotFoundError("Obuna rejasi")
    return dict(plan._mapping)


@router.put("/{plan_id}")
@require_role("super_admin")
async def update_plan(
    plan_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_public_db),
):
    result = await db.execute(text("""
        UPDATE plans SET name = COALESCE(:name, name),
            description = COALESCE(:description, description),
            price_monthly = COALESCE(:price_monthly, price_monthly),
            price_yearly = COALESCE(:price_yearly, price_yearly),
            max_students = COALESCE(:max_students, max_students),
            max_teachers = COALESCE(:max_teachers, max_teachers),
            is_active = COALESCE(:is_active, is_active)
        WHERE id = :id RETURNING id
    """), {
        **{k: data.get(k) for k in ("name", "description", "price_monthly", "price_yearly",
                                      "max_students", "max_teachers", "is_active")},
        "id": plan_id,
    })
    if not result.fetchone():
        raise NotFoundError("Obuna rejasi")
    await db.commit()
    return {"message": "Obuna rejasi yangilandi"}


@router.delete("/{plan_id}")
@require_role("super_admin")
async def delete_plan(
    plan_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_public_db),
):
    result = await db.execute(text("""
        UPDATE plans SET is_active = false WHERE id = :id RETURNING id
    """), {"id": plan_id})
    if not result.fetchone():
        raise NotFoundError("Obuna rejasi")
    await db.commit()
    return {"message": "Obuna rejasi o'chirildi"}

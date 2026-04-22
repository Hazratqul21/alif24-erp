from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.dependencies import get_public_db, get_current_user
from app.core.rbac import require_role
from app.core.exceptions import NotFoundError

router = APIRouter(tags=["SuperAdmin - Monitoring"])


@router.get("/stats")
@require_role("super_admin")
async def system_stats(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_public_db),
):
    stats = await db.execute(text("""
        SELECT
            (SELECT COUNT(*) FROM tenants WHERE deleted_at IS NULL) as total_tenants,
            (SELECT COUNT(*) FROM tenants WHERE is_active = true AND deleted_at IS NULL) as active_tenants,
            (SELECT COUNT(*) FROM tenants WHERE is_blocked = true) as blocked_tenants,
            (SELECT COUNT(*) FROM tenants WHERE subscription_end < CURRENT_DATE AND deleted_at IS NULL) as expired_tenants,
            (SELECT COUNT(*) FROM plans WHERE is_active = true) as active_plans
    """))
    row = stats.fetchone()

    plan_distribution = await db.execute(text("""
        SELECT sp.name as plan_name, COUNT(t.id) as tenant_count
        FROM plans sp
        LEFT JOIN tenants t ON t.plan_id = sp.id AND t.deleted_at IS NULL
        GROUP BY sp.name ORDER BY tenant_count DESC
    """))

    recent_tenants = await db.execute(text("""
        SELECT id, name, domain, created_at, is_active
        FROM tenants WHERE deleted_at IS NULL
        ORDER BY created_at DESC LIMIT 10
    """))

    return {
        "overview": dict(row._mapping),
        "plan_distribution": [dict(r._mapping) for r in plan_distribution],
        "recent_tenants": [dict(r._mapping) for r in recent_tenants],
    }


@router.get("/tenants/{tenant_id}/usage")
@require_role("super_admin")
async def tenant_usage(
    tenant_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_public_db),
):
    tenant = await db.execute(text("""
        SELECT id, name, schema_name, plan_id, subscription_end
        FROM tenants WHERE id = :id
    """), {"id": tenant_id})
    t = tenant.fetchone()
    if not t:
        raise NotFoundError("Tenant")

    schema = t[2]

    usage = await db.execute(text(f"""
        SELECT
            (SELECT COUNT(*) FROM {schema}.users WHERE is_active = true) as active_users,
            (SELECT COUNT(*) FROM {schema}.students WHERE deleted_at IS NULL) as total_students,
            (SELECT COUNT(*) FROM {schema}.teachers WHERE deleted_at IS NULL) as total_teachers,
            (SELECT COUNT(*) FROM {schema}.classes) as total_classes,
            (SELECT COUNT(*) FROM {schema}.grades) as total_grades,
            (SELECT COUNT(*) FROM {schema}.attendance) as total_attendance_records,
            (SELECT pg_size_pretty(pg_total_relation_size('{schema}.users'))) as users_table_size
    """))

    plan_limits = await db.execute(text("""
        SELECT sp.max_students, sp.max_teachers
        FROM plans sp WHERE sp.id = :plan_id
    """), {"plan_id": t[3]})
    limits = plan_limits.fetchone()

    return {
        "tenant": {"id": t[0], "name": t[1], "subscription_end": t[4]},
        "usage": dict(usage.fetchone()._mapping),
        "plan_limits": dict(limits._mapping) if limits else None,
    }

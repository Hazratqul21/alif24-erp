from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional

from app.core.dependencies import get_public_db, get_current_user
from app.core.rbac import require_role

router = APIRouter(prefix="/superadmin/audit", tags=["SuperAdmin - Audit"])


@router.get("/logs")
@require_role("super_admin")
async def cross_tenant_audit(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    tenant_id: Optional[int] = None,
    action: Optional[str] = None,
    module: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_public_db),
):
    params: dict = {"limit": per_page, "offset": (page - 1) * per_page}
    conditions = []

    if tenant_id:
        conditions.append("al.tenant_id = :tenant_id")
        params["tenant_id"] = tenant_id
    if action:
        conditions.append("al.action = :action")
        params["action"] = action
    if module:
        conditions.append("al.module = :module")
        params["module"] = module
    if date_from:
        conditions.append("al.created_at >= :date_from")
        params["date_from"] = date_from
    if date_to:
        conditions.append("al.created_at <= :date_to::date + INTERVAL '1 day'")
        params["date_to"] = date_to

    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    total = (await db.execute(text(f"SELECT COUNT(*) FROM global_audit_logs al {where}"), params)).scalar()

    rows = await db.execute(text(f"""
        SELECT al.id, al.tenant_id, t.name as tenant_name,
               al.user_id, al.action, al.module, al.resource_id,
               al.details, al.ip_address, al.created_at
        FROM global_audit_logs al
        LEFT JOIN tenants t ON t.id = al.tenant_id
        {where}
        ORDER BY al.created_at DESC LIMIT :limit OFFSET :offset
    """), params)
    return {"items": [dict(r._mapping) for r in rows], "total": total, "page": page}

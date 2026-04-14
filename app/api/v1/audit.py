from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional

from app.core.dependencies import get_db, get_current_user
from app.core.rbac import require_role

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("/logs")
@require_role("director", "administrator", "super_admin")
async def search_audit_logs(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    module: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    params: dict = {"limit": per_page, "offset": (page - 1) * per_page}
    conditions = []

    if user_id:
        conditions.append("al.user_id = :user_id")
        params["user_id"] = user_id
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
    total = (await db.execute(text(f"SELECT COUNT(*) FROM audit_logs al {where}"), params)).scalar()

    rows = await db.execute(text(f"""
        SELECT al.id, al.user_id, u.first_name || ' ' || u.last_name as user_name,
               al.action, al.module, al.resource_id, al.details,
               al.ip_address, al.created_at
        FROM audit_logs al
        LEFT JOIN users u ON u.id = al.user_id
        {where}
        ORDER BY al.created_at DESC LIMIT :limit OFFSET :offset
    """), params)
    return {"items": [dict(r._mapping) for r in rows], "total": total, "page": page}


@router.get("/system-logs")
@require_role("director", "super_admin")
async def system_logs(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    level: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    params: dict = {"limit": per_page, "offset": (page - 1) * per_page}
    conditions = []

    if level:
        conditions.append("sl.level = :level")
        params["level"] = level
    if date_from:
        conditions.append("sl.created_at >= :date_from")
        params["date_from"] = date_from
    if date_to:
        conditions.append("sl.created_at <= :date_to::date + INTERVAL '1 day'")
        params["date_to"] = date_to

    where = "WHERE " + " AND ".join(conditions) if conditions else ""

    rows = await db.execute(text(f"""
        SELECT sl.id, sl.level, sl.message, sl.source, sl.details, sl.created_at
        FROM system_logs sl
        {where}
        ORDER BY sl.created_at DESC LIMIT :limit OFFSET :offset
    """), params)
    return {"items": [dict(r._mapping) for r in rows]}

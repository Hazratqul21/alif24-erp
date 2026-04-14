from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional

from app.core.dependencies import get_db, get_current_user
from app.core.rbac import require_permission
from app.core.exceptions import NotFoundError

router = APIRouter(prefix="/discipline", tags=["Discipline"])


@router.get("/")
@require_permission("discipline", "read")
async def list_incidents(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    severity: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    params: dict = {"limit": per_page, "offset": (page - 1) * per_page}
    conditions = []
    if severity:
        conditions.append("di.severity = :severity")
        params["severity"] = severity

    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    rows = await db.execute(text(f"""
        SELECT di.id, di.student_id, u.first_name, u.last_name, di.incident_type,
               di.description, di.severity, di.action_taken, di.incident_date, di.created_at
        FROM discipline_incidents di
        JOIN students s ON s.id = di.student_id
        JOIN users u ON u.id = s.user_id
        {where} ORDER BY di.incident_date DESC LIMIT :limit OFFSET :offset
    """), params)
    return {"items": [dict(r._mapping) for r in rows]}


@router.post("/", status_code=201)
@require_permission("discipline", "create")
async def create_incident(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        INSERT INTO discipline_incidents
            (student_id, incident_type, description, severity, action_taken, incident_date, reported_by)
        VALUES (:student_id, :incident_type, :description, :severity, :action_taken,
                COALESCE(:incident_date, CURRENT_DATE), :reported_by)
        RETURNING id
    """), {
        "student_id": data["student_id"], "incident_type": data["incident_type"],
        "description": data.get("description"), "severity": data.get("severity", "low"),
        "action_taken": data.get("action_taken"), "incident_date": data.get("incident_date"),
        "reported_by": current_user["id"],
    })
    await db.commit()
    return {"id": row.scalar(), "message": "Intizom hodisasi qayd etildi"}


@router.get("/{incident_id}")
@require_permission("discipline", "read")
async def get_incident(
    incident_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        SELECT di.*, u.first_name, u.last_name
        FROM discipline_incidents di
        JOIN students s ON s.id = di.student_id
        JOIN users u ON u.id = s.user_id
        WHERE di.id = :id
    """), {"id": incident_id})
    incident = row.fetchone()
    if not incident:
        raise NotFoundError("Intizom hodisasi")
    return dict(incident._mapping)


@router.put("/{incident_id}")
@require_permission("discipline", "update")
async def update_incident(
    incident_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        UPDATE discipline_incidents SET
            description = COALESCE(:description, description),
            severity = COALESCE(:severity, severity),
            action_taken = COALESCE(:action_taken, action_taken),
            updated_at = NOW()
        WHERE id = :id RETURNING id
    """), {**{k: data.get(k) for k in ("description", "severity", "action_taken")}, "id": incident_id})
    if not result.fetchone():
        raise NotFoundError("Intizom hodisasi")
    await db.commit()
    return {"message": "Intizom hodisasi yangilandi"}


@router.delete("/{incident_id}")
@require_permission("discipline", "delete")
async def delete_incident(
    incident_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("DELETE FROM discipline_incidents WHERE id = :id RETURNING id"), {"id": incident_id})
    if not result.fetchone():
        raise NotFoundError("Intizom hodisasi")
    await db.commit()
    return {"message": "Intizom hodisasi o'chirildi"}


@router.get("/student/{student_id}")
@require_permission("discipline", "read")
async def student_discipline(
    student_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await db.execute(text("""
        SELECT di.id, di.incident_type, di.description, di.severity,
               di.action_taken, di.incident_date
        FROM discipline_incidents di
        WHERE di.student_id = :id
        ORDER BY di.incident_date DESC
    """), {"id": student_id})
    return {"incidents": [dict(r._mapping) for r in rows]}

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional

from app.core.dependencies import get_db, get_current_user
from app.core.rbac import require_permission
from app.core.exceptions import NotFoundError

router = APIRouter(tags=["Competitions"])


@router.get("/")
@require_permission("competitions", "read")
async def list_competitions(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    params: dict = {"limit": per_page, "offset": (page - 1) * per_page}
    conditions = []
    if status:
        conditions.append("c.status = :status")
        params["status"] = status

    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    total = (await db.execute(text(f"SELECT COUNT(*) FROM competitions c {where}"), params)).scalar()
    rows = await db.execute(text(f"""
        SELECT c.id, c.name, c.description, c.competition_type, c.start_date, c.end_date,
               c.location, c.status, c.max_participants, c.created_at
        FROM competitions c {where}
        ORDER BY c.start_date DESC LIMIT :limit OFFSET :offset
    """), params)
    return {"items": [dict(r._mapping) for r in rows], "total": total, "page": page}


@router.post("/", status_code=201)
@require_permission("competitions", "create")
async def create_competition(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        INSERT INTO competitions (name, description, competition_type, start_date, end_date,
                                  location, status, max_participants, created_by)
        VALUES (:name, :description, :type, :start_date, :end_date,
                :location, :status, :max_participants, :created_by)
        RETURNING id
    """), {
        "name": data["name"], "description": data.get("description"),
        "type": data.get("competition_type", "academic"),
        "start_date": data["start_date"], "end_date": data.get("end_date"),
        "location": data.get("location"), "status": data.get("status", "upcoming"),
        "max_participants": data.get("max_participants"),
        "created_by": current_user["id"],
    })
    await db.commit()
    return {"id": row.scalar(), "message": "Musobaqa yaratildi"}


@router.get("/{comp_id}")
@require_permission("competitions", "read")
async def get_competition(
    comp_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("SELECT * FROM competitions WHERE id = :id"), {"id": comp_id})
    comp = row.fetchone()
    if not comp:
        raise NotFoundError("Musobaqa")

    participants = await db.execute(text("""
        SELECT cp.id, cp.student_id, u.first_name, u.last_name, cp.result, cp.placement
        FROM competition_participants cp
        JOIN students s ON s.id = cp.student_id
        JOIN users u ON u.id = s.user_id
        WHERE cp.competition_id = :id
    """), {"id": comp_id})
    return {**dict(comp._mapping), "participants": [dict(r._mapping) for r in participants]}


@router.put("/{comp_id}")
@require_permission("competitions", "update")
async def update_competition(
    comp_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        UPDATE competitions SET name = COALESCE(:name, name),
            description = COALESCE(:description, description),
            start_date = COALESCE(:start_date, start_date),
            end_date = COALESCE(:end_date, end_date),
            location = COALESCE(:location, location),
            status = COALESCE(:status, status),
            updated_at = NOW()
        WHERE id = :id RETURNING id
    """), {**{k: data.get(k) for k in ("name", "description", "start_date", "end_date", "location", "status")}, "id": comp_id})
    if not result.fetchone():
        raise NotFoundError("Musobaqa")
    await db.commit()
    return {"message": "Musobaqa yangilandi"}


@router.delete("/{comp_id}")
@require_permission("competitions", "delete")
async def delete_competition(
    comp_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("DELETE FROM competitions WHERE id = :id RETURNING id"), {"id": comp_id})
    if not result.fetchone():
        raise NotFoundError("Musobaqa")
    await db.commit()
    return {"message": "Musobaqa o'chirildi"}


@router.post("/{comp_id}/register", status_code=201)
@require_permission("competitions", "create")
async def register_student(
    comp_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    check = await db.execute(text("SELECT id, max_participants FROM competitions WHERE id = :id"), {"id": comp_id})
    comp = check.fetchone()
    if not comp:
        raise NotFoundError("Musobaqa")

    if comp[1]:
        count = (await db.execute(text(
            "SELECT COUNT(*) FROM competition_participants WHERE competition_id = :id"
        ), {"id": comp_id})).scalar()
        if count >= comp[1]:
            from app.core.exceptions import AppError
            raise AppError("Musobaqa ishtirokchilari soni chegaraga yetdi")

    row = await db.execute(text("""
        INSERT INTO competition_participants (competition_id, student_id, registered_by)
        VALUES (:comp_id, :student_id, :registered_by)
        ON CONFLICT DO NOTHING RETURNING id
    """), {"comp_id": comp_id, "student_id": data["student_id"], "registered_by": current_user["id"]})
    await db.commit()
    return {"id": row.scalar(), "message": "O'quvchi musobaqaga ro'yxatdan o'tkazildi"}


@router.put("/{comp_id}/results")
@require_permission("competitions", "update")
async def update_results(
    comp_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    results = data.get("results", [])
    count = 0
    for r in results:
        await db.execute(text("""
            UPDATE competition_participants SET result = :result, placement = :placement
            WHERE competition_id = :comp_id AND student_id = :student_id
        """), {
            "comp_id": comp_id, "student_id": r["student_id"],
            "result": r.get("result"), "placement": r.get("placement"),
        })
        count += 1
    await db.commit()
    return {"updated": count, "message": f"{count} ta natija yangilandi"}


# --- Events ---

@router.get("/events")
@require_permission("competitions", "read")
async def list_events(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await db.execute(text("""
        SELECT id, name, description, event_type, event_date, location, status, created_at
        FROM school_events
        ORDER BY event_date DESC LIMIT :limit OFFSET :offset
    """), {"limit": per_page, "offset": (page - 1) * per_page})
    return {"items": [dict(r._mapping) for r in rows]}


@router.post("/events", status_code=201)
@require_permission("competitions", "create")
async def create_event(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        INSERT INTO school_events (name, description, event_type, event_date, location, status, created_by)
        VALUES (:name, :description, :event_type, :event_date, :location, :status, :created_by)
        RETURNING id
    """), {
        "name": data["name"], "description": data.get("description"),
        "event_type": data.get("event_type"), "event_date": data["event_date"],
        "location": data.get("location"), "status": data.get("status", "upcoming"),
        "created_by": current_user["id"],
    })
    await db.commit()
    return {"id": row.scalar(), "message": "Tadbir yaratildi"}


@router.put("/events/{event_id}")
@require_permission("competitions", "update")
async def update_event(
    event_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        UPDATE school_events SET name = COALESCE(:name, name),
            description = COALESCE(:description, description),
            event_date = COALESCE(:event_date, event_date),
            location = COALESCE(:location, location),
            status = COALESCE(:status, status), updated_at = NOW()
        WHERE id = :id RETURNING id
    """), {**{k: data.get(k) for k in ("name", "description", "event_date", "location", "status")}, "id": event_id})
    if not result.fetchone():
        raise NotFoundError("Tadbir")
    await db.commit()
    return {"message": "Tadbir yangilandi"}


@router.delete("/events/{event_id}")
@require_permission("competitions", "delete")
async def delete_event(
    event_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("DELETE FROM school_events WHERE id = :id RETURNING id"), {"id": event_id})
    if not result.fetchone():
        raise NotFoundError("Tadbir")
    await db.commit()
    return {"message": "Tadbir o'chirildi"}


@router.post("/events/{event_id}/register", status_code=201)
@require_permission("competitions", "create")
async def register_for_event(
    event_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    check = await db.execute(text("SELECT id FROM school_events WHERE id = :id"), {"id": event_id})
    if not check.fetchone():
        raise NotFoundError("Tadbir")

    row = await db.execute(text("""
        INSERT INTO event_participants (event_id, student_id, registered_by)
        VALUES (:event_id, :student_id, :registered_by)
        ON CONFLICT DO NOTHING RETURNING id
    """), {"event_id": event_id, "student_id": data["student_id"], "registered_by": current_user["id"]})
    await db.commit()
    return {"id": row.scalar(), "message": "Tadbirga ro'yxatdan o'tkazildi"}

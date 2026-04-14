from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional

from app.core.dependencies import get_db, get_current_user
from app.core.rbac import require_permission
from app.core.exceptions import NotFoundError

router = APIRouter(tags=["Transport"])


# --- Buses ---

@router.get("/buses")
@require_permission("transport", "read")
async def list_buses(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await db.execute(text("""
        SELECT id, bus_number, plate_number, capacity, driver_name, driver_phone,
               is_active, created_at
        FROM buses ORDER BY bus_number
    """))
    return {"items": [dict(r._mapping) for r in rows]}


@router.post("/buses", status_code=201)
@require_permission("transport", "create")
async def create_bus(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        INSERT INTO buses (bus_number, plate_number, capacity, driver_name, driver_phone, is_active)
        VALUES (:bus_number, :plate_number, :capacity, :driver_name, :driver_phone, :is_active)
        RETURNING id
    """), {
        "bus_number": data["bus_number"], "plate_number": data["plate_number"],
        "capacity": data.get("capacity", 40), "driver_name": data.get("driver_name"),
        "driver_phone": data.get("driver_phone"), "is_active": data.get("is_active", True),
    })
    await db.commit()
    return {"id": row.scalar(), "message": "Avtobus qo'shildi"}


@router.put("/buses/{bus_id}")
@require_permission("transport", "update")
async def update_bus(
    bus_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        UPDATE buses SET bus_number = COALESCE(:bus_number, bus_number),
            plate_number = COALESCE(:plate_number, plate_number),
            capacity = COALESCE(:capacity, capacity),
            driver_name = COALESCE(:driver_name, driver_name),
            driver_phone = COALESCE(:driver_phone, driver_phone),
            is_active = COALESCE(:is_active, is_active),
            updated_at = NOW()
        WHERE id = :id RETURNING id
    """), {**{k: data.get(k) for k in ("bus_number", "plate_number", "capacity", "driver_name", "driver_phone", "is_active")}, "id": bus_id})
    if not result.fetchone():
        raise NotFoundError("Avtobus")
    await db.commit()
    return {"message": "Avtobus ma'lumotlari yangilandi"}


@router.delete("/buses/{bus_id}")
@require_permission("transport", "delete")
async def delete_bus(
    bus_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("DELETE FROM buses WHERE id = :id RETURNING id"), {"id": bus_id})
    if not result.fetchone():
        raise NotFoundError("Avtobus")
    await db.commit()
    return {"message": "Avtobus o'chirildi"}


# --- Stops ---

@router.get("/stops")
@require_permission("transport", "read")
async def list_stops(
    bus_id: Optional[int] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    where = ""
    params: dict = {}
    if bus_id:
        where = "WHERE bs.bus_id = :bus_id"
        params["bus_id"] = bus_id

    rows = await db.execute(text(f"""
        SELECT bs.id, bs.bus_id, b.bus_number, bs.stop_name, bs.latitude, bs.longitude,
               bs.stop_order, bs.pickup_time
        FROM bus_stops bs
        JOIN buses b ON b.id = bs.bus_id
        {where} ORDER BY bs.bus_id, bs.stop_order
    """), params)
    return {"items": [dict(r._mapping) for r in rows]}


@router.post("/stops", status_code=201)
@require_permission("transport", "create")
async def create_stop(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        INSERT INTO bus_stops (bus_id, stop_name, latitude, longitude, stop_order, pickup_time)
        VALUES (:bus_id, :stop_name, :latitude, :longitude, :stop_order, :pickup_time)
        RETURNING id
    """), {
        "bus_id": data["bus_id"], "stop_name": data["stop_name"],
        "latitude": data.get("latitude"), "longitude": data.get("longitude"),
        "stop_order": data.get("stop_order", 0), "pickup_time": data.get("pickup_time"),
    })
    await db.commit()
    return {"id": row.scalar(), "message": "Bekat qo'shildi"}


@router.put("/stops/{stop_id}")
@require_permission("transport", "update")
async def update_stop(
    stop_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        UPDATE bus_stops SET stop_name = COALESCE(:stop_name, stop_name),
            latitude = COALESCE(:latitude, latitude),
            longitude = COALESCE(:longitude, longitude),
            stop_order = COALESCE(:stop_order, stop_order),
            pickup_time = COALESCE(:pickup_time, pickup_time)
        WHERE id = :id RETURNING id
    """), {**{k: data.get(k) for k in ("stop_name", "latitude", "longitude", "stop_order", "pickup_time")}, "id": stop_id})
    if not result.fetchone():
        raise NotFoundError("Bekat")
    await db.commit()
    return {"message": "Bekat yangilandi"}


@router.delete("/stops/{stop_id}")
@require_permission("transport", "delete")
async def delete_stop(
    stop_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("DELETE FROM bus_stops WHERE id = :id RETURNING id"), {"id": stop_id})
    if not result.fetchone():
        raise NotFoundError("Bekat")
    await db.commit()
    return {"message": "Bekat o'chirildi"}


# --- Subscriptions ---

@router.get("/subscriptions")
@require_permission("transport", "read")
async def list_subscriptions(
    bus_id: Optional[int] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    where = ""
    params: dict = {}
    if bus_id:
        where = "WHERE ts.bus_id = :bus_id"
        params["bus_id"] = bus_id

    rows = await db.execute(text(f"""
        SELECT ts.id, ts.student_id, u.first_name, u.last_name, ts.bus_id,
               b.bus_number, bs.stop_name, ts.start_date, ts.end_date, ts.is_active
        FROM transport_subscriptions ts
        JOIN students s ON s.id = ts.student_id
        JOIN users u ON u.id = s.user_id
        JOIN buses b ON b.id = ts.bus_id
        LEFT JOIN bus_stops bs ON bs.id = ts.stop_id
        {where} ORDER BY u.last_name
    """), params)
    return {"items": [dict(r._mapping) for r in rows]}


@router.post("/subscriptions", status_code=201)
@require_permission("transport", "create")
async def create_subscription(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        INSERT INTO transport_subscriptions (student_id, bus_id, stop_id, start_date, end_date, is_active)
        VALUES (:student_id, :bus_id, :stop_id, :start_date, :end_date, true)
        RETURNING id
    """), {
        "student_id": data["student_id"], "bus_id": data["bus_id"],
        "stop_id": data.get("stop_id"), "start_date": data["start_date"],
        "end_date": data.get("end_date"),
    })
    await db.commit()
    return {"id": row.scalar(), "message": "Transport obunasi yaratildi"}


@router.put("/subscriptions/{sub_id}")
@require_permission("transport", "update")
async def update_subscription(
    sub_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        UPDATE transport_subscriptions SET bus_id = COALESCE(:bus_id, bus_id),
            stop_id = COALESCE(:stop_id, stop_id),
            end_date = COALESCE(:end_date, end_date),
            is_active = COALESCE(:is_active, is_active)
        WHERE id = :id RETURNING id
    """), {**{k: data.get(k) for k in ("bus_id", "stop_id", "end_date", "is_active")}, "id": sub_id})
    if not result.fetchone():
        raise NotFoundError("Transport obunasi")
    await db.commit()
    return {"message": "Transport obunasi yangilandi"}


@router.delete("/subscriptions/{sub_id}")
@require_permission("transport", "delete")
async def delete_subscription(
    sub_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("DELETE FROM transport_subscriptions WHERE id = :id RETURNING id"), {"id": sub_id})
    if not result.fetchone():
        raise NotFoundError("Transport obunasi")
    await db.commit()
    return {"message": "Transport obunasi o'chirildi"}


# --- GPS Tracking ---

@router.post("/tracking")
@require_permission("transport", "create")
async def record_position(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await db.execute(text("""
        INSERT INTO bus_tracking (bus_id, latitude, longitude, speed, recorded_at)
        VALUES (:bus_id, :latitude, :longitude, :speed, NOW())
    """), {
        "bus_id": data["bus_id"], "latitude": data["latitude"],
        "longitude": data["longitude"], "speed": data.get("speed"),
    })
    await db.commit()
    return {"message": "Joylashuv qayd etildi"}


@router.get("/tracking/{bus_id}/latest")
@require_permission("transport", "read")
async def latest_position(
    bus_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        SELECT bt.id, bt.latitude, bt.longitude, bt.speed, bt.recorded_at,
               b.bus_number, b.driver_name
        FROM bus_tracking bt
        JOIN buses b ON b.id = bt.bus_id
        WHERE bt.bus_id = :bus_id
        ORDER BY bt.recorded_at DESC LIMIT 1
    """), {"bus_id": bus_id})
    pos = row.fetchone()
    if not pos:
        raise NotFoundError("Avtobus joylashuvi")
    return dict(pos._mapping)

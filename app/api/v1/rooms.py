from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional

from app.core.dependencies import get_db, get_current_user
from app.core.rbac import require_permission
from app.core.exceptions import NotFoundError, ConflictError

router = APIRouter(tags=["Rooms"])


@router.get("")
@require_permission("rooms", "read")
async def list_rooms(
    room_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    where = ""
    params: dict = {}
    if room_type:
        where = "WHERE r.room_type = :room_type"
        params["room_type"] = room_type

    rows = await db.execute(text(f"""
        SELECT r.id, r.name, r.room_type, r.capacity, r.floor, r.building,
               r.equipment, r.is_available, r.created_at
        FROM rooms r {where} ORDER BY r.building, r.floor, r.name
    """), params)
    return {"items": [dict(r._mapping) for r in rows]}


@router.post("", status_code=201)
@require_permission("rooms", "create")
async def create_room(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        INSERT INTO rooms (name, room_type, capacity, floor, building, equipment, is_available)
        VALUES (:name, :room_type, :capacity, :floor, :building, :equipment, :is_available)
        RETURNING id
    """), {
        "name": data["name"], "room_type": data.get("room_type", "classroom"),
        "capacity": data.get("capacity"), "floor": data.get("floor"),
        "building": data.get("building"), "equipment": data.get("equipment"),
        "is_available": data.get("is_available", True),
    })
    await db.commit()
    return {"id": row.scalar(), "message": "Xona yaratildi"}


@router.get("/{room_id}")
@require_permission("rooms", "read")
async def get_room(
    room_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("SELECT * FROM rooms WHERE id = :id"), {"id": room_id})
    room = row.fetchone()
    if not room:
        raise NotFoundError("Xona")
    return dict(room._mapping)


@router.put("/{room_id}")
@require_permission("rooms", "update")
async def update_room(
    room_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        UPDATE rooms SET name = COALESCE(:name, name),
            room_type = COALESCE(:room_type, room_type),
            capacity = COALESCE(:capacity, capacity),
            floor = COALESCE(:floor, floor),
            building = COALESCE(:building, building),
            equipment = COALESCE(:equipment, equipment),
            is_available = COALESCE(:is_available, is_available),
            updated_at = NOW()
        WHERE id = :id RETURNING id
    """), {**{k: data.get(k) for k in ("name", "room_type", "capacity", "floor", "building", "equipment", "is_available")}, "id": room_id})
    if not result.fetchone():
        raise NotFoundError("Xona")
    await db.commit()
    return {"message": "Xona yangilandi"}


@router.delete("/{room_id}")
@require_permission("rooms", "delete")
async def delete_room(
    room_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("DELETE FROM rooms WHERE id = :id RETURNING id"), {"id": room_id})
    if not result.fetchone():
        raise NotFoundError("Xona")
    await db.commit()
    return {"message": "Xona o'chirildi"}


# --- Bookings ---

@router.post("/bookings", status_code=201)
@require_permission("rooms", "create")
async def book_room(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conflict = await db.execute(text("""
        SELECT id FROM room_bookings
        WHERE room_id = :room_id AND booking_date = :booking_date
            AND start_time < :end_time AND end_time > :start_time
            AND status != 'cancelled'
    """), {
        "room_id": data["room_id"], "booking_date": data["booking_date"],
        "start_time": data["start_time"], "end_time": data["end_time"],
    })
    if conflict.fetchone():
        raise ConflictError("Xona shu vaqtda band")

    row = await db.execute(text("""
        INSERT INTO room_bookings (room_id, booking_date, start_time, end_time, purpose, booked_by, status)
        VALUES (:room_id, :booking_date, :start_time, :end_time, :purpose, :booked_by, 'confirmed')
        RETURNING id
    """), {
        "room_id": data["room_id"], "booking_date": data["booking_date"],
        "start_time": data["start_time"], "end_time": data["end_time"],
        "purpose": data.get("purpose"), "booked_by": current_user["id"],
    })
    await db.commit()
    return {"id": row.scalar(), "message": "Xona band qilindi"}


@router.get("/bookings/date/{date}")
@require_permission("rooms", "read")
async def bookings_by_date(
    date: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await db.execute(text("""
        SELECT rb.id, rb.room_id, r.name as room_name, rb.start_time, rb.end_time,
               rb.purpose, rb.status, u.first_name || ' ' || u.last_name as booked_by
        FROM room_bookings rb
        JOIN rooms r ON r.id = rb.room_id
        LEFT JOIN users u ON u.id = rb.booked_by
        WHERE rb.booking_date = :date AND rb.status != 'cancelled'
        ORDER BY r.name, rb.start_time
    """), {"date": date})
    return {"bookings": [dict(r._mapping) for r in rows]}


@router.delete("/bookings/{booking_id}")
@require_permission("rooms", "delete")
async def cancel_booking(
    booking_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        UPDATE room_bookings SET status = 'cancelled' WHERE id = :id RETURNING id
    """), {"id": booking_id})
    if not result.fetchone():
        raise NotFoundError("Bron")
    await db.commit()
    return {"message": "Bron bekor qilindi"}

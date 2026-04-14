from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional

from app.core.dependencies import get_db, get_current_user
from app.core.rbac import require_permission
from app.core.exceptions import NotFoundError

router = APIRouter(tags=["Holidays"])


@router.get("/")
@require_permission("holidays", "read")
async def list_holidays(
    year: Optional[int] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    where = ""
    params: dict = {}
    if year:
        where = "WHERE EXTRACT(YEAR FROM h.date) = :year"
        params["year"] = year

    rows = await db.execute(text(f"""
        SELECT h.id, h.name, h.date, h.end_date, h.holiday_type, h.description, h.is_recurring
        FROM holidays h {where}
        ORDER BY h.date
    """), params)
    return {"items": [dict(r._mapping) for r in rows]}


@router.post("/", status_code=201)
@require_permission("holidays", "create")
async def create_holiday(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        INSERT INTO holidays (name, date, end_date, holiday_type, description, is_recurring)
        VALUES (:name, :date, :end_date, :holiday_type, :description, :is_recurring)
        RETURNING id
    """), {
        "name": data["name"], "date": data["date"],
        "end_date": data.get("end_date"), "holiday_type": data.get("holiday_type", "national"),
        "description": data.get("description"),
        "is_recurring": data.get("is_recurring", False),
    })
    await db.commit()
    return {"id": row.scalar(), "message": "Bayram/dam olish kuni yaratildi"}


@router.get("/{holiday_id}")
@require_permission("holidays", "read")
async def get_holiday(
    holiday_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("SELECT * FROM holidays WHERE id = :id"), {"id": holiday_id})
    holiday = row.fetchone()
    if not holiday:
        raise NotFoundError("Bayram/dam olish kuni")
    return dict(holiday._mapping)


@router.put("/{holiday_id}")
@require_permission("holidays", "update")
async def update_holiday(
    holiday_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        UPDATE holidays SET name = COALESCE(:name, name),
            date = COALESCE(:date, date),
            end_date = COALESCE(:end_date, end_date),
            holiday_type = COALESCE(:holiday_type, holiday_type),
            description = COALESCE(:description, description),
            is_recurring = COALESCE(:is_recurring, is_recurring)
        WHERE id = :id RETURNING id
    """), {**{k: data.get(k) for k in ("name", "date", "end_date", "holiday_type", "description", "is_recurring")}, "id": holiday_id})
    if not result.fetchone():
        raise NotFoundError("Bayram/dam olish kuni")
    await db.commit()
    return {"message": "Bayram/dam olish kuni yangilandi"}


@router.delete("/{holiday_id}")
@require_permission("holidays", "delete")
async def delete_holiday(
    holiday_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("DELETE FROM holidays WHERE id = :id RETURNING id"), {"id": holiday_id})
    if not result.fetchone():
        raise NotFoundError("Bayram/dam olish kuni")
    await db.commit()
    return {"message": "Bayram/dam olish kuni o'chirildi"}

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional

from app.core.dependencies import get_db, get_current_user
from app.core.rbac import require_permission
from app.core.exceptions import NotFoundError

router = APIRouter(tags=["Canteen"])


# --- Menu Items ---

@router.get("/menu-items")
@require_permission("canteen", "view")
async def list_menu_items(
    category: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    where = ""
    params: dict = {}
    if category:
        where = "WHERE category = :category"
        params["category"] = category

    rows = await db.execute(text(f"""
        SELECT id, name, description, price, category, is_available, allergens
        FROM menu_items {where} ORDER BY category, name
    """), params)
    return {"items": [dict(r._mapping) for r in rows]}


@router.post("/menu-items", status_code=201)
@require_permission("canteen", "create")
async def create_menu_item(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        INSERT INTO menu_items (name, description, price, category, is_available, allergens)
        VALUES (:name, :description, :price, :category, :is_available, :allergens)
        RETURNING id
    """), {
        "name": data["name"], "description": data.get("description"),
        "price": data["price"], "category": data.get("category"),
        "is_available": data.get("is_available", True),
        "allergens": data.get("allergens"),
    })
    await db.commit()
    return {"id": row.scalar(), "message": "Menyu elementi yaratildi"}


@router.put("/menu-items/{item_id}")
@require_permission("canteen", "update")
async def update_menu_item(
    item_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        UPDATE menu_items SET name = COALESCE(:name, name),
            description = COALESCE(:description, description),
            price = COALESCE(:price, price),
            category = COALESCE(:category, category),
            is_available = COALESCE(:is_available, is_available)
        WHERE id = :id RETURNING id
    """), {**{k: data.get(k) for k in ("name", "description", "price", "category", "is_available")}, "id": item_id})
    if not result.fetchone():
        raise NotFoundError("Menyu elementi")
    await db.commit()
    return {"message": "Menyu elementi yangilandi"}


@router.delete("/menu-items/{item_id}")
@require_permission("canteen", "delete")
async def delete_menu_item(
    item_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("DELETE FROM menu_items WHERE id = :id RETURNING id"), {"id": item_id})
    if not result.fetchone():
        raise NotFoundError("Menyu elementi")
    await db.commit()
    return {"message": "Menyu elementi o'chirildi"}


# --- Daily Menu ---

@router.get("/daily-menu")
@require_permission("canteen", "view")
async def list_daily_menu(
    date: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    where = ""
    params: dict = {}
    if date:
        where = "WHERE dm.menu_date = :date"
        params["date"] = date

    rows = await db.execute(text(f"""
        SELECT dm.id, dm.menu_date, dm.meal_type, mi.name, mi.price, mi.category
        FROM daily_menu dm
        JOIN menu_items mi ON mi.id = dm.menu_item_id
        {where} ORDER BY dm.menu_date DESC, dm.meal_type
    """), params)
    return {"items": [dict(r._mapping) for r in rows]}


@router.post("/daily-menu", status_code=201)
@require_permission("canteen", "create")
async def create_daily_menu(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        INSERT INTO daily_menu (menu_date, meal_type, menu_item_id)
        VALUES (:menu_date, :meal_type, :menu_item_id)
        RETURNING id
    """), {
        "menu_date": data["menu_date"],
        "meal_type": data["meal_type"],
        "menu_item_id": data["menu_item_id"],
    })
    await db.commit()
    return {"id": row.scalar(), "message": "Kunlik menyu yaratildi"}


@router.put("/daily-menu/{menu_id}")
@require_permission("canteen", "update")
async def update_daily_menu(
    menu_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        UPDATE daily_menu SET meal_type = COALESCE(:meal_type, meal_type),
            menu_item_id = COALESCE(:menu_item_id, menu_item_id)
        WHERE id = :id RETURNING id
    """), {**{k: data.get(k) for k in ("meal_type", "menu_item_id")}, "id": menu_id})
    if not result.fetchone():
        raise NotFoundError("Kunlik menyu")
    await db.commit()
    return {"message": "Kunlik menyu yangilandi"}


@router.delete("/daily-menu/{menu_id}")
@require_permission("canteen", "delete")
async def delete_daily_menu(
    menu_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("DELETE FROM daily_menu WHERE id = :id RETURNING id"), {"id": menu_id})
    if not result.fetchone():
        raise NotFoundError("Kunlik menyu")
    await db.commit()
    return {"message": "Kunlik menyu o'chirildi"}


# --- Orders ---

@router.post("/orders", status_code=201)
@require_permission("canteen", "create")
async def place_order(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        INSERT INTO canteen_orders (student_id, menu_item_id, quantity, total_price, order_date, status)
        VALUES (:student_id, :menu_item_id, :quantity, :total_price, CURRENT_DATE, 'pending')
        RETURNING id
    """), {
        "student_id": data["student_id"],
        "menu_item_id": data["menu_item_id"],
        "quantity": data.get("quantity", 1),
        "total_price": data["total_price"],
    })
    await db.commit()
    return {"id": row.scalar(), "message": "Buyurtma qabul qilindi"}


@router.get("/orders/student/{student_id}")
@require_permission("canteen", "view")
async def student_orders(
    student_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await db.execute(text("""
        SELECT co.id, mi.name, co.quantity, co.total_price, co.order_date, co.status
        FROM canteen_orders co
        JOIN menu_items mi ON mi.id = co.menu_item_id
        WHERE co.student_id = :id
        ORDER BY co.order_date DESC
    """), {"id": student_id})
    return {"orders": [dict(r._mapping) for r in rows]}


# --- Dietary Restrictions ---

@router.get("/dietary-restrictions")
@require_permission("canteen", "view")
async def list_restrictions(
    student_id: Optional[int] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    where = ""
    params: dict = {}
    if student_id:
        where = "WHERE dr.student_id = :student_id"
        params["student_id"] = student_id

    rows = await db.execute(text(f"""
        SELECT dr.id, dr.student_id, u.first_name, u.last_name,
               dr.restriction_type, dr.description, dr.severity
        FROM dietary_restrictions dr
        JOIN students s ON s.id = dr.student_id
        JOIN users u ON u.id = s.user_id
        {where} ORDER BY u.last_name
    """), params)
    return {"items": [dict(r._mapping) for r in rows]}


@router.post("/dietary-restrictions", status_code=201)
@require_permission("canteen", "create")
async def create_restriction(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        INSERT INTO dietary_restrictions (student_id, restriction_type, description, severity)
        VALUES (:student_id, :restriction_type, :description, :severity)
        RETURNING id
    """), {
        "student_id": data["student_id"],
        "restriction_type": data["restriction_type"],
        "description": data.get("description"),
        "severity": data.get("severity", "moderate"),
    })
    await db.commit()
    return {"id": row.scalar(), "message": "Ovqatlanish cheklovi qo'shildi"}


@router.put("/dietary-restrictions/{restriction_id}")
@require_permission("canteen", "update")
async def update_restriction(
    restriction_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        UPDATE dietary_restrictions SET restriction_type = COALESCE(:restriction_type, restriction_type),
            description = COALESCE(:description, description),
            severity = COALESCE(:severity, severity)
        WHERE id = :id RETURNING id
    """), {**{k: data.get(k) for k in ("restriction_type", "description", "severity")}, "id": restriction_id})
    if not result.fetchone():
        raise NotFoundError("Ovqatlanish cheklovi")
    await db.commit()
    return {"message": "Ovqatlanish cheklovi yangilandi"}


@router.delete("/dietary-restrictions/{restriction_id}")
@require_permission("canteen", "delete")
async def delete_restriction(
    restriction_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("DELETE FROM dietary_restrictions WHERE id = :id RETURNING id"), {"id": restriction_id})
    if not result.fetchone():
        raise NotFoundError("Ovqatlanish cheklovi")
    await db.commit()
    return {"message": "Ovqatlanish cheklovi o'chirildi"}

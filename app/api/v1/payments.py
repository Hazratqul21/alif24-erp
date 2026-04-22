from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional

from app.core.dependencies import get_db, get_current_user
from app.core.rbac import require_permission
from app.core.exceptions import NotFoundError, AppError

router = APIRouter(tags=["Payments"])


@router.get("/student/{student_id}")
@require_permission("payments", "read")
async def student_payments(
    student_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await db.execute(text("""
        SELECT p.id, p.amount, p.payment_type, p.status, p.payment_date,
               p.description, p.payment_method, p.transaction_id
        FROM payments p WHERE p.student_id = :id
        ORDER BY p.payment_date DESC
    """), {"id": student_id})
    return {"payments": [dict(r._mapping) for r in rows]}


@router.get("/debts")
@require_permission("payments", "read")
async def outstanding_debts(
    class_id: Optional[int] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    where = ""
    params: dict = {}
    if class_id:
        where = "AND s.current_class_id = :class_id"
        params["class_id"] = class_id

    rows = await db.execute(text(f"""
        SELECT s.id as student_id, u.first_name, u.last_name, c.name as class_name,
               f.name as fee_name, f.amount as fee_amount,
               COALESCE(SUM(p.amount) FILTER (WHERE p.status = 'paid'), 0) as paid,
               f.amount - COALESCE(SUM(p.amount) FILTER (WHERE p.status = 'paid'), 0) as debt
        FROM students s
        JOIN users u ON u.id = s.user_id
        LEFT JOIN classes c ON c.id = s.current_class_id
        CROSS JOIN fees f
        LEFT JOIN payments p ON p.student_id = s.id
        WHERE s.status != 'deleted' {where}
        GROUP BY s.id, u.first_name, u.last_name, c.name, f.name, f.amount
        HAVING f.amount - COALESCE(SUM(p.amount) FILTER (WHERE p.status = 'paid'), 0) > 0
        ORDER BY debt DESC
    """), params)
    return {"debts": [dict(r._mapping) for r in rows]}


@router.post("/online")
@require_permission("payments", "create")
async def initiate_online_payment(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        INSERT INTO payments (student_id, amount, payment_type, payment_method, status, description)
        VALUES (:student_id, :amount, 'tuition', :method, 'pending', :description)
        RETURNING id
    """), {
        "student_id": str(data["student_id"]),
        "amount": data["amount"],
        "method": data.get("method", "online"),
        "description": data.get("description"),
    })
    payment_id = row.scalar()
    await db.commit()

    return {
        "payment_id": payment_id,
        "redirect_url": f"/pay/{data.get('method', 'payme')}/{payment_id}",
        "message": "To'lov boshlandi",
    }


@router.post("/callback/payme")
async def payme_callback(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    body = await request.json()
    method = body.get("method")
    params = body.get("params", {})

    if method == "CheckPerformTransaction":
        payment_id = params.get("account", {}).get("payment_id")
        check = await db.execute(text("SELECT id, amount, status FROM payments WHERE id = :id"), {"id": payment_id})
        p = check.fetchone()
        if not p:
            return {"error": {"code": -31050, "message": {"uz": "To'lov topilmadi"}}}
        if p[2] == "paid":
            return {"error": {"code": -31051, "message": {"uz": "To'lov allaqachon amalga oshirilgan"}}}
        return {"result": {"allow": True}}

    elif method == "PerformTransaction":
        payment_id = params.get("account", {}).get("payment_id")
        await db.execute(text("""
            UPDATE payments SET status = 'paid', payment_date = CURRENT_DATE,
                transaction_id = :tid WHERE id = :id
        """), {"id": payment_id, "tid": params.get("id")})
        await db.commit()
        return {"result": {"state": 2}}

    return {"error": {"code": -32601, "message": {"uz": "Metod topilmadi"}}}


@router.post("/callback/click")
async def click_callback(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    body = await request.json()
    action = body.get("action")
    payment_id = body.get("merchant_trans_id")

    if action == 0:
        check = await db.execute(text("SELECT id, amount, status FROM payments WHERE id = :id"), {"id": payment_id})
        p = check.fetchone()
        if not p:
            return {"error": -5, "error_note": "To'lov topilmadi"}
        return {"error": 0, "error_note": "Success"}

    elif action == 1:
        await db.execute(text("""
            UPDATE payments SET status = 'paid', payment_date = CURRENT_DATE,
                transaction_id = :tid WHERE id = :id
        """), {"id": payment_id, "tid": body.get("click_trans_id")})
        await db.commit()
        return {"error": 0, "error_note": "Success"}

    return {"error": -3, "error_note": "Noto'g'ri amal"}


@router.get("/invoices/{invoice_id}/pdf")
@require_permission("payments", "read")
async def download_invoice(
    invoice_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        SELECT p.id, p.amount, p.status, p.payment_date, p.description,
               u.first_name, u.last_name, s.student_id as student_code
        FROM payments p
        JOIN students s ON s.id = p.student_id
        JOIN users u ON u.id = s.user_id
        WHERE p.id = :id
    """), {"id": invoice_id})
    invoice = row.fetchone()
    if not invoice:
        raise NotFoundError("Hisob-faktura")

    return {
        "invoice": dict(invoice._mapping),
        "pdf_url": f"/static/invoices/{invoice_id}.pdf",
        "message": "Hisob-faktura tayyor",
    }


@router.post("/reminder")
@require_permission("payments", "create")
async def send_reminder(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    student_ids = data.get("student_ids", [])
    if not student_ids:
        rows = await db.execute(text("""
            SELECT DISTINCT s.id FROM students s
            JOIN fees f ON true
            LEFT JOIN payments p ON p.student_id = s.id AND p.fee_id = f.id AND p.status = 'paid'
            WHERE s.deleted_at IS NULL
            GROUP BY s.id, f.id, f.amount
            HAVING f.amount - COALESCE(SUM(p.amount), 0) > 0
        """))
        student_ids = [r[0] for r in rows]

    return {"sent_to": len(student_ids), "message": f"{len(student_ids)} ta ota-onaga eslatma yuborildi"}


# --- Payment Plans ---

@router.get("/plans")
@require_permission("payments", "read")
async def list_plans(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await db.execute(text("SELECT * FROM payment_plans ORDER BY created_at DESC"))
    return {"items": [dict(r._mapping) for r in rows]}


@router.post("/plans", status_code=201)
@require_permission("payments", "create")
async def create_plan(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        INSERT INTO payment_plans (name, description, installments, total_amount)
        VALUES (:name, :description, :installments, :total_amount)
        RETURNING id
    """), {
        "name": data["name"],
        "description": data.get("description"),
        "installments": data.get("installments", 1),
        "total_amount": data["total_amount"],
    })
    await db.commit()
    return {"id": row.scalar(), "message": "To'lov rejasi yaratildi"}


@router.put("/plans/{plan_id}")
@require_permission("payments", "update")
async def update_plan(
    plan_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        UPDATE payment_plans SET name = COALESCE(:name, name),
            description = COALESCE(:description, description),
            installments = COALESCE(:installments, installments),
            total_amount = COALESCE(:total_amount, total_amount)
        WHERE id = :id RETURNING id
    """), {**{k: data.get(k) for k in ("name", "description", "installments", "total_amount")}, "id": plan_id})
    if not result.fetchone():
        raise NotFoundError("To'lov rejasi")
    await db.commit()
    return {"message": "To'lov rejasi yangilandi"}


@router.delete("/plans/{plan_id}")
@require_permission("payments", "delete")
async def delete_plan(
    plan_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("DELETE FROM payment_plans WHERE id = :id RETURNING id"), {"id": plan_id})
    if not result.fetchone():
        raise NotFoundError("To'lov rejasi")
    await db.commit()
    return {"message": "To'lov rejasi o'chirildi"}


# --- Fees ---

@router.get("/fees")
@require_permission("payments", "read")
async def list_fees(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await db.execute(text("SELECT * FROM fees ORDER BY name"))
    return {"items": [dict(r._mapping) for r in rows]}


@router.post("/fees", status_code=201)
@require_permission("payments", "create")
async def create_fee(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        INSERT INTO fees (name, amount, fee_type, academic_year_id, description)
        VALUES (:name, :amount, :fee_type, :year_id, :description)
        RETURNING id
    """), {
        "name": data["name"],
        "amount": data["amount"],
        "fee_type": data.get("fee_type", "tuition"),
        "year_id": data.get("academic_year_id"),
        "description": data.get("description"),
    })
    await db.commit()
    return {"id": row.scalar(), "message": "To'lov turi yaratildi"}


@router.put("/fees/{fee_id}")
@require_permission("payments", "update")
async def update_fee(
    fee_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        UPDATE fees SET name = COALESCE(:name, name),
            amount = COALESCE(:amount, amount),
            fee_type = COALESCE(:fee_type, fee_type),
            description = COALESCE(:description, description)
        WHERE id = :id RETURNING id
    """), {**{k: data.get(k) for k in ("name", "amount", "fee_type", "description")}, "id": fee_id})
    if not result.fetchone():
        raise NotFoundError("To'lov turi")
    await db.commit()
    return {"message": "To'lov turi yangilandi"}


@router.delete("/fees/{fee_id}")
@require_permission("payments", "delete")
async def delete_fee(
    fee_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("DELETE FROM fees WHERE id = :id RETURNING id"), {"id": fee_id})
    if not result.fetchone():
        raise NotFoundError("To'lov turi")
    await db.commit()
    return {"message": "To'lov turi o'chirildi"}

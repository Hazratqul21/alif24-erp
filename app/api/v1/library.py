from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional

from app.core.dependencies import get_db, get_current_user, get_alif24_db
from app.core.rbac import require_permission
from app.core.exceptions import NotFoundError, AppError

router = APIRouter(prefix="/library", tags=["Library"])


@router.get("/books")
@require_permission("library", "read")
async def search_books(
    search: Optional[str] = None,
    category: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conditions = []
    params: dict = {"limit": per_page, "offset": (page - 1) * per_page}
    if search:
        conditions.append("(b.title ILIKE :search OR b.author ILIKE :search OR b.isbn ILIKE :search)")
        params["search"] = f"%{search}%"
    if category:
        conditions.append("b.category = :category")
        params["category"] = category

    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    total = (await db.execute(text(f"SELECT COUNT(*) FROM books b {where}"), params)).scalar()
    rows = await db.execute(text(f"""
        SELECT b.id, b.title, b.author, b.isbn, b.category, b.total_copies,
               b.available_copies, b.created_at
        FROM books b {where}
        ORDER BY b.title LIMIT :limit OFFSET :offset
    """), params)
    return {"items": [dict(r._mapping) for r in rows], "total": total, "page": page}


@router.post("/books", status_code=201)
@require_permission("library", "create")
async def add_book(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        INSERT INTO books (title, author, isbn, category, total_copies, available_copies, central_book_id)
        VALUES (:title, :author, :isbn, :category, :copies, :copies, :central_id)
        RETURNING id
    """), {
        "title": data["title"], "author": data.get("author"), "isbn": data.get("isbn"),
        "category": data.get("category"), "copies": data.get("total_copies", 1),
        "central_id": data.get("central_book_id"),
    })
    await db.commit()
    return {"id": row.scalar(), "message": "Kitob qo'shildi"}


@router.get("/central")
@require_permission("library", "read")
async def search_central(
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    alif_db: AsyncSession = Depends(get_alif24_db),
    db: AsyncSession = Depends(get_db),
):
    if not alif_db:
        return {"items": [], "message": "Markaziy baza ulanmagan"}

    params: dict = {"limit": per_page, "offset": (page - 1) * per_page}
    where = ""
    if search:
        where = "WHERE title ILIKE :search OR author ILIKE :search"
        params["search"] = f"%{search}%"

    rows = await alif_db.execute(text(f"""
        SELECT id, title, author, isbn, category, subject, grade_level
        FROM central_books {where}
        ORDER BY title LIMIT :limit OFFSET :offset
    """), params)
    return {"items": [dict(r._mapping) for r in rows]}


@router.post("/central", status_code=201)
@require_permission("library", "create")
async def add_central_book(
    data: dict,
    current_user: dict = Depends(get_current_user),
    alif_db: AsyncSession = Depends(get_alif24_db),
):
    if not alif_db:
        raise AppError("Markaziy baza ulanmagan")

    row = await alif_db.execute(text("""
        INSERT INTO central_books (title, author, isbn, category, subject, grade_level)
        VALUES (:title, :author, :isbn, :category, :subject, :grade_level)
        RETURNING id
    """), {
        "title": data["title"], "author": data.get("author"), "isbn": data.get("isbn"),
        "category": data.get("category"), "subject": data.get("subject"),
        "grade_level": data.get("grade_level"),
    })
    await alif_db.commit()
    return {"id": row.scalar(), "message": "Markaziy kitob qo'shildi"}


@router.post("/loans", status_code=201)
@require_permission("library", "create")
async def lend_book(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    book = await db.execute(text("SELECT available_copies FROM books WHERE id = :id"), {"id": data["book_id"]})
    avail = book.scalar()
    if avail is None:
        raise NotFoundError("Kitob")
    if avail <= 0:
        raise AppError("Kitob mavjud emas (barcha nusxalar berilgan)")

    row = await db.execute(text("""
        INSERT INTO book_loans (book_id, student_id, loaned_by, loan_date, due_date)
        VALUES (:book_id, :student_id, :loaned_by, NOW(), :due_date)
        RETURNING id
    """), {
        "book_id": data["book_id"], "student_id": data["student_id"],
        "loaned_by": current_user["id"], "due_date": data["due_date"],
    })
    await db.execute(text("UPDATE books SET available_copies = available_copies - 1 WHERE id = :id"), {"id": data["book_id"]})
    await db.commit()
    return {"id": row.scalar(), "message": "Kitob berildi"}


@router.put("/loans/{loan_id}/return")
@require_permission("library", "update")
async def return_book(
    loan_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    loan = await db.execute(text("SELECT book_id, returned_at FROM book_loans WHERE id = :id"), {"id": loan_id})
    row = loan.fetchone()
    if not row:
        raise NotFoundError("Kitob berish yozuvi")
    if row[1]:
        raise AppError("Kitob allaqachon qaytarilgan")

    await db.execute(text("UPDATE book_loans SET returned_at = NOW() WHERE id = :id"), {"id": loan_id})
    await db.execute(text("UPDATE books SET available_copies = available_copies + 1 WHERE id = :id"), {"id": row[0]})
    await db.commit()
    return {"message": "Kitob qaytarildi"}


@router.get("/loans/overdue")
@require_permission("library", "read")
async def overdue_loans(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await db.execute(text("""
        SELECT bl.id, b.title, u.first_name, u.last_name, bl.loan_date, bl.due_date,
               (CURRENT_DATE - bl.due_date) as days_overdue
        FROM book_loans bl
        JOIN books b ON b.id = bl.book_id
        JOIN students s ON s.id = bl.student_id
        JOIN users u ON u.id = s.user_id
        WHERE bl.returned_at IS NULL AND bl.due_date < CURRENT_DATE
        ORDER BY bl.due_date
    """))
    return {"overdue": [dict(r._mapping) for r in rows]}


@router.get("/stats")
@require_permission("library", "read")
async def library_stats(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stats = await db.execute(text("""
        SELECT
            (SELECT COUNT(*) FROM books) as total_books,
            (SELECT SUM(total_copies) FROM books) as total_copies,
            (SELECT SUM(available_copies) FROM books) as available_copies,
            (SELECT COUNT(*) FROM book_loans WHERE returned_at IS NULL) as active_loans,
            (SELECT COUNT(*) FROM book_loans WHERE returned_at IS NULL AND due_date < CURRENT_DATE) as overdue
    """))
    return dict(stats.fetchone()._mapping)


@router.get("/export")
@require_permission("library", "read")
async def export_books(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await db.execute(text("""
        SELECT b.title, b.author, b.isbn, b.category, b.total_copies, b.available_copies
        FROM books b ORDER BY b.title
    """))
    return {"data": [dict(r._mapping) for r in rows], "format": "xlsx", "message": "Eksport tayyor"}


@router.get("/interlibrary/nearby")
@require_permission("library", "read")
async def nearby_schools(
    current_user: dict = Depends(get_current_user),
    alif_db: AsyncSession = Depends(get_alif24_db),
):
    if not alif_db:
        return {"schools": []}

    rows = await alif_db.execute(text("""
        SELECT t.id, t.name, sl.city, sl.latitude, sl.longitude
        FROM tenants t
        LEFT JOIN school_locations sl ON sl.tenant_id = t.id
        WHERE t.is_active = true
        ORDER BY t.name LIMIT 50
    """))
    return {"schools": [dict(r._mapping) for r in rows]}


@router.post("/interlibrary/request", status_code=201)
@require_permission("library", "create")
async def interlibrary_request(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        INSERT INTO interlibrary_requests (book_id, requesting_school_id, target_school_id, status, requested_by)
        VALUES (:book_id, :from_id, :to_id, 'pending', :user_id)
        RETURNING id
    """), {
        "book_id": data["book_id"], "from_id": current_user.get("tenant_id"),
        "to_id": data["target_school_id"], "user_id": current_user["id"],
    })
    await db.commit()
    return {"id": row.scalar(), "message": "Kutubxonalararo so'rov yuborildi"}


@router.put("/interlibrary/{request_id}/approve")
@require_permission("library", "update")
async def approve_interlibrary(
    request_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        UPDATE interlibrary_requests SET status = 'approved', reviewed_by = :uid, reviewed_at = NOW()
        WHERE id = :id AND status = 'pending' RETURNING id
    """), {"id": request_id, "uid": current_user["id"]})
    if not result.fetchone():
        raise NotFoundError("So'rov")
    await db.commit()
    return {"message": "So'rov tasdiqlandi"}


@router.put("/interlibrary/{request_id}/reject")
@require_permission("library", "update")
async def reject_interlibrary(
    request_id: int,
    data: dict = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    reason = data.get("reason", "") if data else ""
    result = await db.execute(text("""
        UPDATE interlibrary_requests SET status = 'rejected', reviewed_by = :uid,
            reviewed_at = NOW(), reject_reason = :reason
        WHERE id = :id AND status = 'pending' RETURNING id
    """), {"id": request_id, "uid": current_user["id"], "reason": reason})
    if not result.fetchone():
        raise NotFoundError("So'rov")
    await db.commit()
    return {"message": "So'rov rad etildi"}

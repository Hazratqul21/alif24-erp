from fastapi import APIRouter, Depends, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional

from app.core.dependencies import get_db, get_current_user
from app.core.rbac import require_permission
from app.core.exceptions import NotFoundError, AppError

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("/")
@require_permission("students", "read")
async def list_students(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    class_id: Optional[int] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conditions = []
    params: dict = {"limit": per_page, "offset": (page - 1) * per_page}

    if search:
        conditions.append("(u.first_name ILIKE :search OR u.last_name ILIKE :search OR s.student_code ILIKE :search)")
        params["search"] = f"%{search}%"
    if class_id:
        conditions.append("s.class_id = :class_id")
        params["class_id"] = class_id

    where = "WHERE s.deleted_at IS NULL"
    if conditions:
        where += " AND " + " AND ".join(conditions)

    count_q = await db.execute(text(f"SELECT COUNT(*) FROM students s JOIN users u ON u.id = s.user_id {where}"), params)
    total = count_q.scalar()

    rows = await db.execute(text(f"""
        SELECT s.id, s.student_code, u.first_name, u.last_name, u.phone, s.class_id,
               c.name as class_name, s.created_at, u.alif24_user_id
        FROM students s
        JOIN users u ON u.id = s.user_id
        LEFT JOIN classes c ON c.id = s.class_id
        {where}
        ORDER BY u.last_name, u.first_name
        LIMIT :limit OFFSET :offset
    """), params)

    items = [dict(r._mapping) for r in rows]
    return {"items": items, "total": total, "page": page, "per_page": per_page}


@router.post("/", status_code=201)
@require_permission("students", "create")
async def create_student(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Alif24 ID berilgan bo'lsa — Alif24 dan import qilish
    if data.get("alif24_id"):
        from app.services.alif24_integration import import_student_from_alif24
        return await import_student_from_alif24(
            erp_db=db,
            alif24_id=data["alif24_id"],
            class_id=data.get("class_id"),
            student_code=data.get("student_code"),
        )

    user_result = await db.execute(text("""
        INSERT INTO users (email, phone, first_name, last_name, password_hash, is_active)
        VALUES (:email, :phone, :first_name, :last_name, :password_hash, true)
        RETURNING id
    """), {
        "email": data.get("email"),
        "phone": data["phone"],
        "first_name": data["first_name"],
        "last_name": data["last_name"],
        "password_hash": data.get("password_hash", "changeme_hashed"),
    })
    user_id = user_result.scalar()

    student_result = await db.execute(text("""
        INSERT INTO students (user_id, student_code, class_id, birth_date, gender, address)
        VALUES (:user_id, :student_code, :class_id, :birth_date, :gender, :address)
        RETURNING id, student_code
    """), {
        "user_id": user_id,
        "student_code": data.get("student_code"),
        "class_id": data.get("class_id"),
        "birth_date": data.get("birth_date"),
        "gender": data.get("gender"),
        "address": data.get("address"),
    })
    row = student_result.fetchone()

    await db.execute(text("""
        INSERT INTO user_roles (user_id, role_id)
        SELECT :user_id, id FROM roles WHERE name = 'student'
    """), {"user_id": user_id})

    await db.commit()
    return {"id": row[0], "student_code": row[1], "user_id": user_id, "message": "O'quvchi muvaffaqiyatli yaratildi"}


@router.get("/{student_id}")
@require_permission("students", "read")
async def get_student(
    student_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        SELECT s.id, s.student_code, u.first_name, u.last_name, u.email, u.phone,
               s.class_id, c.name as class_name, s.birth_date, s.gender, s.address,
               s.created_at, u.alif24_user_id
        FROM students s
        JOIN users u ON u.id = s.user_id
        LEFT JOIN classes c ON c.id = s.class_id
        WHERE s.id = :id AND s.deleted_at IS NULL
    """), {"id": student_id})
    student = row.fetchone()
    if not student:
        raise NotFoundError("O'quvchi")

    grades_q = await db.execute(text("""
        SELECT sub.name as subject, ROUND(AVG(g.score), 1) as avg_score
        FROM grades g
        JOIN subjects sub ON sub.id = g.subject_id
        WHERE g.student_id = :id
        GROUP BY sub.name
    """), {"id": student_id})

    return {
        **dict(student._mapping),
        "grades_summary": [dict(r._mapping) for r in grades_q],
    }


@router.put("/{student_id}")
@require_permission("students", "update")
async def update_student(
    student_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    check = await db.execute(text("SELECT id, user_id FROM students WHERE id = :id AND deleted_at IS NULL"), {"id": student_id})
    student = check.fetchone()
    if not student:
        raise NotFoundError("O'quvchi")

    if any(k in data for k in ("first_name", "last_name", "phone", "email")):
        await db.execute(text("""
            UPDATE users SET first_name = COALESCE(:first_name, first_name),
                last_name = COALESCE(:last_name, last_name),
                phone = COALESCE(:phone, phone),
                email = COALESCE(:email, email),
                updated_at = NOW()
            WHERE id = :user_id
        """), {
            "first_name": data.get("first_name"),
            "last_name": data.get("last_name"),
            "phone": data.get("phone"),
            "email": data.get("email"),
            "user_id": student[1],
        })

    await db.execute(text("""
        UPDATE students SET class_id = COALESCE(:class_id, class_id),
            birth_date = COALESCE(:birth_date, birth_date),
            gender = COALESCE(:gender, gender),
            address = COALESCE(:address, address),
            updated_at = NOW()
        WHERE id = :id
    """), {
        "class_id": data.get("class_id"),
        "birth_date": data.get("birth_date"),
        "gender": data.get("gender"),
        "address": data.get("address"),
        "id": student_id,
    })
    await db.commit()
    return {"message": "O'quvchi ma'lumotlari yangilandi"}


@router.delete("/{student_id}")
@require_permission("students", "delete")
async def delete_student(
    student_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        UPDATE students SET deleted_at = NOW() WHERE id = :id AND deleted_at IS NULL RETURNING id
    """), {"id": student_id})
    if not result.fetchone():
        raise NotFoundError("O'quvchi")
    await db.commit()
    return {"message": "O'quvchi o'chirildi"}


@router.get("/{student_id}/grades")
@require_permission("students", "read")
async def student_grades(
    student_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await db.execute(text("""
        SELECT g.id, g.score, g.grade_type, g.comment, g.graded_at,
               sub.name as subject, u.first_name || ' ' || u.last_name as teacher
        FROM grades g
        JOIN subjects sub ON sub.id = g.subject_id
        LEFT JOIN teachers t ON t.id = g.teacher_id
        LEFT JOIN users u ON u.id = t.user_id
        WHERE g.student_id = :id
        ORDER BY g.graded_at DESC
    """), {"id": student_id})
    return {"grades": [dict(r._mapping) for r in rows]}


@router.get("/{student_id}/attendance")
@require_permission("students", "read")
async def student_attendance(
    student_id: int,
    month: Optional[int] = None,
    year: Optional[int] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    params: dict = {"id": student_id}
    extra = ""
    if month and year:
        extra = "AND EXTRACT(MONTH FROM a.date) = :month AND EXTRACT(YEAR FROM a.date) = :year"
        params["month"] = month
        params["year"] = year

    rows = await db.execute(text(f"""
        SELECT a.id, a.date, a.status, a.note
        FROM attendance a WHERE a.student_id = :id {extra}
        ORDER BY a.date DESC
    """), params)
    return {"attendance": [dict(r._mapping) for r in rows]}


@router.get("/{student_id}/schedule")
@require_permission("students", "read")
async def student_schedule(
    student_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("SELECT class_id FROM students WHERE id = :id"), {"id": student_id})
    cls = row.scalar()
    if not cls:
        raise NotFoundError("O'quvchi")

    rows = await db.execute(text("""
        SELECT sc.id, sc.day_of_week, sc.start_time, sc.end_time,
               sub.name as subject, u.first_name || ' ' || u.last_name as teacher,
               r.name as room
        FROM schedules sc
        JOIN subjects sub ON sub.id = sc.subject_id
        LEFT JOIN teachers t ON t.id = sc.teacher_id
        LEFT JOIN users u ON u.id = t.user_id
        LEFT JOIN rooms r ON r.id = sc.room_id
        WHERE sc.class_id = :class_id
        ORDER BY sc.day_of_week, sc.start_time
    """), {"class_id": cls})
    return {"schedule": [dict(r._mapping) for r in rows]}


@router.get("/{student_id}/payments")
@require_permission("students", "read")
async def student_payments(
    student_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await db.execute(text("""
        SELECT p.id, p.amount, p.payment_type, p.status, p.paid_at, p.description
        FROM payments p WHERE p.student_id = :id
        ORDER BY p.paid_at DESC
    """), {"id": student_id})
    return {"payments": [dict(r._mapping) for r in rows]}


@router.post("/bulk-enroll")
@require_permission("students", "create")
async def bulk_enroll(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename.endswith((".xlsx", ".xls")):
        raise AppError("Faqat Excel fayllari qabul qilinadi (.xlsx, .xls)")

    content = await file.read()
    try:
        import openpyxl
        from io import BytesIO
        wb = openpyxl.load_workbook(BytesIO(content))
        ws = wb.active
    except Exception:
        raise AppError("Excel faylini o'qishda xatolik")

    created = 0
    errors = []
    for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        if not row or not row[0]:
            continue
        try:
            first_name, last_name, phone = row[0], row[1], row[2]
            class_id = row[3] if len(row) > 3 else None

            user_res = await db.execute(text("""
                INSERT INTO users (phone, first_name, last_name, password_hash, is_active)
                VALUES (:phone, :first_name, :last_name, 'changeme', true)
                RETURNING id
            """), {"phone": str(phone), "first_name": first_name, "last_name": last_name})
            uid = user_res.scalar()

            await db.execute(text("""
                INSERT INTO students (user_id, class_id) VALUES (:uid, :cid)
            """), {"uid": uid, "cid": class_id})

            await db.execute(text("""
                INSERT INTO user_roles (user_id, role_id)
                SELECT :uid, id FROM roles WHERE name = 'student'
            """), {"uid": uid})

            created += 1
        except Exception as e:
            errors.append({"row": idx, "error": str(e)})

    await db.commit()
    return {"created": created, "errors": errors, "message": f"{created} ta o'quvchi ro'yxatga olindi"}

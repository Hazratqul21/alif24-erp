from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional

from app.core.dependencies import get_db, get_current_user
from app.core.rbac import require_permission
from app.core.exceptions import NotFoundError

router = APIRouter(tags=["Teachers"])


@router.get("/")
@require_permission("teachers", "read")
async def list_teachers(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    params: dict = {"limit": per_page, "offset": (page - 1) * per_page}
    where = "WHERE t.deleted_at IS NULL"
    if search:
        where += " AND (u.first_name ILIKE :search OR u.last_name ILIKE :search)"
        params["search"] = f"%{search}%"

    total = (await db.execute(text(f"SELECT COUNT(*) FROM teachers t JOIN users u ON u.id = t.user_id {where}"), params)).scalar()
    rows = await db.execute(text(f"""
        SELECT t.id, u.first_name, u.last_name, u.email, u.phone,
               t.specialization, t.hire_date, t.created_at
        FROM teachers t JOIN users u ON u.id = t.user_id
        {where} ORDER BY u.last_name LIMIT :limit OFFSET :offset
    """), params)
    return {"items": [dict(r._mapping) for r in rows], "total": total, "page": page, "per_page": per_page}


@router.post("/", status_code=201)
@require_permission("teachers", "create")
async def create_teacher(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if data.get("alif24_id"):
        from app.services.alif24_integration import import_teacher_from_alif24
        return await import_teacher_from_alif24(erp_db=db, alif24_id=data["alif24_id"])

    user_res = await db.execute(text("""
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
    user_id = user_res.scalar()

    teacher_res = await db.execute(text("""
        INSERT INTO teachers (user_id, specialization, hire_date, education, experience_years)
        VALUES (:user_id, :specialization, :hire_date, :education, :experience_years)
        RETURNING id
    """), {
        "user_id": user_id,
        "specialization": data.get("specialization"),
        "hire_date": data.get("hire_date"),
        "education": data.get("education"),
        "experience_years": data.get("experience_years"),
    })
    teacher_id = teacher_res.scalar()

    await db.execute(text("""
        INSERT INTO user_roles (user_id, role_id)
        SELECT :uid, id FROM roles WHERE name = 'teacher'
    """), {"uid": user_id})

    await db.commit()
    return {"id": teacher_id, "user_id": user_id, "message": "O'qituvchi muvaffaqiyatli yaratildi"}


@router.get("/{teacher_id}")
@require_permission("teachers", "read")
async def get_teacher(
    teacher_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        SELECT t.id, u.first_name, u.last_name, u.email, u.phone,
               t.specialization, t.hire_date, t.education, t.experience_years, t.created_at
        FROM teachers t JOIN users u ON u.id = t.user_id
        WHERE t.id = :id AND t.deleted_at IS NULL
    """), {"id": teacher_id})
    teacher = row.fetchone()
    if not teacher:
        raise NotFoundError("O'qituvchi")
    return dict(teacher._mapping)


@router.put("/{teacher_id}")
@require_permission("teachers", "update")
async def update_teacher(
    teacher_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    check = await db.execute(text("SELECT id, user_id FROM teachers WHERE id = :id AND deleted_at IS NULL"), {"id": teacher_id})
    teacher = check.fetchone()
    if not teacher:
        raise NotFoundError("O'qituvchi")

    if any(k in data for k in ("first_name", "last_name", "phone", "email")):
        await db.execute(text("""
            UPDATE users SET first_name = COALESCE(:first_name, first_name),
                last_name = COALESCE(:last_name, last_name),
                phone = COALESCE(:phone, phone), email = COALESCE(:email, email),
                updated_at = NOW()
            WHERE id = :user_id
        """), {**{k: data.get(k) for k in ("first_name", "last_name", "phone", "email")}, "user_id": teacher[1]})

    await db.execute(text("""
        UPDATE teachers SET specialization = COALESCE(:specialization, specialization),
            education = COALESCE(:education, education),
            experience_years = COALESCE(:experience_years, experience_years),
            updated_at = NOW()
        WHERE id = :id
    """), {
        "specialization": data.get("specialization"),
        "education": data.get("education"),
        "experience_years": data.get("experience_years"),
        "id": teacher_id,
    })
    await db.commit()
    return {"message": "O'qituvchi ma'lumotlari yangilandi"}


@router.get("/{teacher_id}/schedule")
@require_permission("teachers", "read")
async def teacher_schedule(
    teacher_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await db.execute(text("""
        SELECT sc.id, sc.day_of_week, sc.start_time, sc.end_time,
               sub.name as subject, c.name as class_name, r.name as room
        FROM schedules sc
        JOIN subjects sub ON sub.id = sc.subject_id
        JOIN classes c ON c.id = sc.class_id
        LEFT JOIN rooms r ON r.id = sc.room_id
        WHERE sc.teacher_id = :id
        ORDER BY sc.day_of_week, sc.start_time
    """), {"id": teacher_id})
    return {"schedule": [dict(r._mapping) for r in rows]}


@router.post("/{teacher_id}/subjects")
@require_permission("teachers", "update")
async def assign_subjects(
    teacher_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    check = await db.execute(text("SELECT id FROM teachers WHERE id = :id AND deleted_at IS NULL"), {"id": teacher_id})
    if not check.fetchone():
        raise NotFoundError("O'qituvchi")

    subject_ids = data.get("subject_ids", [])
    await db.execute(text("DELETE FROM teacher_subjects WHERE teacher_id = :tid"), {"tid": teacher_id})

    for sid in subject_ids:
        await db.execute(text("""
            INSERT INTO teacher_subjects (teacher_id, subject_id) VALUES (:tid, :sid)
        """), {"tid": teacher_id, "sid": sid})

    await db.commit()
    return {"message": f"{len(subject_ids)} ta fan biriktirildi"}

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional

from app.core.dependencies import get_db, get_current_user
from app.core.rbac import require_permission
from app.core.exceptions import NotFoundError

router = APIRouter(prefix="/admissions", tags=["Admissions"])


@router.post("/", status_code=201)
@require_permission("admissions", "create")
async def submit_application(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        INSERT INTO admissions (
            applicant_first_name, applicant_last_name, birth_date, gender,
            parent_name, parent_phone, parent_email,
            desired_grade, desired_class_id, previous_school,
            documents_path, notes, status, submitted_by
        ) VALUES (
            :first_name, :last_name, :birth_date, :gender,
            :parent_name, :parent_phone, :parent_email,
            :desired_grade, :desired_class_id, :previous_school,
            :documents_path, :notes, 'pending', :submitted_by
        ) RETURNING id
    """), {
        "first_name": data["first_name"], "last_name": data["last_name"],
        "birth_date": data.get("birth_date"), "gender": data.get("gender"),
        "parent_name": data.get("parent_name"), "parent_phone": data.get("parent_phone"),
        "parent_email": data.get("parent_email"), "desired_grade": data.get("desired_grade"),
        "desired_class_id": data.get("desired_class_id"),
        "previous_school": data.get("previous_school"),
        "documents_path": data.get("documents_path"), "notes": data.get("notes"),
        "submitted_by": current_user["id"],
    })
    await db.commit()
    return {"id": row.scalar(), "message": "Ariza qabul qilindi"}


@router.get("/")
@require_permission("admissions", "read")
async def list_applications(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    params: dict = {"limit": per_page, "offset": (page - 1) * per_page}
    conditions = []
    if status:
        conditions.append("a.status = :status")
        params["status"] = status

    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    total = (await db.execute(text(f"SELECT COUNT(*) FROM admissions a {where}"), params)).scalar()
    rows = await db.execute(text(f"""
        SELECT a.id, a.applicant_first_name, a.applicant_last_name, a.birth_date,
               a.desired_grade, a.status, a.parent_phone, a.created_at
        FROM admissions a {where}
        ORDER BY a.created_at DESC LIMIT :limit OFFSET :offset
    """), params)
    return {"items": [dict(r._mapping) for r in rows], "total": total, "page": page}


@router.get("/{app_id}")
@require_permission("admissions", "read")
async def get_application(
    app_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("SELECT * FROM admissions WHERE id = :id"), {"id": app_id})
    app = row.fetchone()
    if not app:
        raise NotFoundError("Ariza")
    return dict(app._mapping)


@router.put("/{app_id}")
@require_permission("admissions", "update")
async def update_application(
    app_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        UPDATE admissions SET
            desired_grade = COALESCE(:desired_grade, desired_grade),
            desired_class_id = COALESCE(:desired_class_id, desired_class_id),
            notes = COALESCE(:notes, notes),
            updated_at = NOW()
        WHERE id = :id RETURNING id
    """), {**{k: data.get(k) for k in ("desired_grade", "desired_class_id", "notes")}, "id": app_id})
    if not result.fetchone():
        raise NotFoundError("Ariza")
    await db.commit()
    return {"message": "Ariza yangilandi"}


@router.put("/{app_id}/review")
@require_permission("admissions", "update")
async def review_application(
    app_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        UPDATE admissions SET status = 'review', review_notes = :review_notes,
            reviewed_by = :reviewed_by, reviewed_at = NOW()
        WHERE id = :id AND status = 'pending' RETURNING id
    """), {"review_notes": data.get("review_notes"), "reviewed_by": current_user["id"], "id": app_id})
    if not result.fetchone():
        raise NotFoundError("Ariza yoki holat noto'g'ri")
    await db.commit()
    return {"message": "Ariza ko'rib chiqilmoqda"}


@router.put("/{app_id}/approve")
@require_permission("admissions", "update")
async def approve_application(
    app_id: int,
    data: dict = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        UPDATE admissions SET status = 'approved', reviewed_by = :reviewed_by, reviewed_at = NOW()
        WHERE id = :id AND status IN ('pending', 'review') RETURNING id
    """), {"reviewed_by": current_user["id"], "id": app_id})
    if not result.fetchone():
        raise NotFoundError("Ariza yoki holat noto'g'ri")
    await db.commit()
    return {"message": "Ariza tasdiqlandi"}


@router.put("/{app_id}/reject")
@require_permission("admissions", "update")
async def reject_application(
    app_id: int,
    data: dict = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    reason = (data or {}).get("reason", "")
    result = await db.execute(text("""
        UPDATE admissions SET status = 'rejected', review_notes = :reason,
            reviewed_by = :reviewed_by, reviewed_at = NOW()
        WHERE id = :id AND status IN ('pending', 'review') RETURNING id
    """), {"reason": reason, "reviewed_by": current_user["id"], "id": app_id})
    if not result.fetchone():
        raise NotFoundError("Ariza yoki holat noto'g'ri")
    await db.commit()
    return {"message": "Ariza rad etildi"}

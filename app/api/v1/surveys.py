from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional

from app.core.dependencies import get_db, get_current_user
from app.core.rbac import require_permission
from app.core.exceptions import NotFoundError, AppError

router = APIRouter(tags=["Surveys"])


@router.get("")
@require_permission("surveys", "view")
async def list_surveys(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    params: dict = {"limit": per_page, "offset": (page - 1) * per_page}
    conditions = []
    if status:
        conditions.append("s.status = :status")
        params["status"] = status

    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    total = (await db.execute(text(f"SELECT COUNT(*) FROM surveys s {where}"), params)).scalar()
    rows = await db.execute(text(f"""
        SELECT s.id, s.title, s.description, s.target_audience, s.status,
               s.start_date, s.end_date, s.created_at,
               (SELECT COUNT(*) FROM survey_responses sr WHERE sr.survey_id = s.id) as response_count
        FROM surveys s {where}
        ORDER BY s.created_at DESC LIMIT :limit OFFSET :offset
    """), params)
    return {"items": [dict(r._mapping) for r in rows], "total": total, "page": page}


@router.post("", status_code=201)
@require_permission("surveys", "create")
async def create_survey(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        INSERT INTO surveys (title, description, questions, target_audience, status,
                            start_date, end_date, is_anonymous, created_by)
        VALUES (:title, :description, :questions::jsonb, :target_audience, :status,
                :start_date, :end_date, :is_anonymous, :created_by)
        RETURNING id
    """), {
        "title": data["title"], "description": data.get("description"),
        "questions": str(data.get("questions", "[]")),
        "target_audience": data.get("target_audience", "all"),
        "status": data.get("status", "draft"),
        "start_date": data.get("start_date"), "end_date": data.get("end_date"),
        "is_anonymous": data.get("is_anonymous", False),
        "created_by": current_user["id"],
    })
    await db.commit()
    return {"id": row.scalar(), "message": "So'rovnoma yaratildi"}


@router.get("/{survey_id}")
@require_permission("surveys", "view")
async def get_survey(
    survey_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("SELECT * FROM surveys WHERE id = :id"), {"id": survey_id})
    survey = row.fetchone()
    if not survey:
        raise NotFoundError("So'rovnoma")
    return dict(survey._mapping)


@router.put("/{survey_id}")
@require_permission("surveys", "update")
async def update_survey(
    survey_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        UPDATE surveys SET title = COALESCE(:title, title),
            description = COALESCE(:description, description),
            target_audience = COALESCE(:target_audience, target_audience),
            status = COALESCE(:status, status),
            start_date = COALESCE(:start_date, start_date),
            end_date = COALESCE(:end_date, end_date),
            updated_at = NOW()
        WHERE id = :id RETURNING id
    """), {**{k: data.get(k) for k in ("title", "description", "target_audience", "status", "start_date", "end_date")}, "id": survey_id})
    if not result.fetchone():
        raise NotFoundError("So'rovnoma")
    await db.commit()
    return {"message": "So'rovnoma yangilandi"}


@router.delete("/{survey_id}")
@require_permission("surveys", "delete")
async def delete_survey(
    survey_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("DELETE FROM surveys WHERE id = :id RETURNING id"), {"id": survey_id})
    if not result.fetchone():
        raise NotFoundError("So'rovnoma")
    await db.commit()
    return {"message": "So'rovnoma o'chirildi"}


@router.post("/{survey_id}/respond", status_code=201)
async def submit_response(
    survey_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    check = await db.execute(text("SELECT id, status FROM surveys WHERE id = :id"), {"id": survey_id})
    survey = check.fetchone()
    if not survey:
        raise NotFoundError("So'rovnoma")
    if survey[1] != "active":
        raise AppError("So'rovnoma hozirda faol emas")

    existing = await db.execute(text("""
        SELECT id FROM survey_responses WHERE survey_id = :sid AND user_id = :uid
    """), {"sid": survey_id, "uid": current_user["id"]})
    if existing.fetchone():
        raise AppError("Siz allaqachon javob bergansiz")

    row = await db.execute(text("""
        INSERT INTO survey_responses (survey_id, user_id, answers, submitted_at)
        VALUES (:survey_id, :user_id, :answers::jsonb, NOW())
        RETURNING id
    """), {
        "survey_id": survey_id, "user_id": current_user["id"],
        "answers": str(data.get("answers", "{}")),
    })
    await db.commit()
    return {"id": row.scalar(), "message": "Javob qabul qilindi"}


@router.get("/{survey_id}/results")
@require_permission("surveys", "view")
async def survey_results(
    survey_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    check = await db.execute(text("SELECT id, title, is_anonymous FROM surveys WHERE id = :id"), {"id": survey_id})
    survey = check.fetchone()
    if not survey:
        raise NotFoundError("So'rovnoma")

    total = (await db.execute(text(
        "SELECT COUNT(*) FROM survey_responses WHERE survey_id = :id"
    ), {"id": survey_id})).scalar()

    rows = await db.execute(text("""
        SELECT sr.id, sr.answers, sr.submitted_at,
               CASE WHEN :is_anon THEN NULL ELSE u.first_name || ' ' || u.last_name END as respondent
        FROM survey_responses sr
        LEFT JOIN users u ON u.id = sr.user_id
        WHERE sr.survey_id = :id
        ORDER BY sr.submitted_at
    """), {"id": survey_id, "is_anon": survey[2]})

    return {
        "survey": {"id": survey[0], "title": survey[1]},
        "total_responses": total,
        "responses": [dict(r._mapping) for r in rows],
    }

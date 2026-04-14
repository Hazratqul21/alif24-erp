from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional

from app.core.dependencies import get_db, get_current_user
from app.core.rbac import require_role
from app.core.exceptions import NotFoundError

router = APIRouter(tags=["Psychology"])


# --- Psychological Tests ---

@router.get("/tests")
@require_role("psychologist", "director", "administrator")
async def list_tests(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await db.execute(text("""
        SELECT id, name, description, test_type, target_age_group, created_at
        FROM psych_tests ORDER BY name LIMIT :limit OFFSET :offset
    """), {"limit": per_page, "offset": (page - 1) * per_page})
    return {"items": [dict(r._mapping) for r in rows]}


@router.post("/tests", status_code=201)
@require_role("psychologist")
async def create_test(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        INSERT INTO psych_tests (name, description, test_type, target_age_group, questions, created_by)
        VALUES (:name, :description, :test_type, :target_age_group, :questions::jsonb, :created_by)
        RETURNING id
    """), {
        "name": data["name"], "description": data.get("description"),
        "test_type": data.get("test_type"), "target_age_group": data.get("target_age_group"),
        "questions": str(data.get("questions", "[]")), "created_by": current_user["id"],
    })
    await db.commit()
    return {"id": row.scalar(), "message": "Psixologik test yaratildi"}


@router.get("/tests/{test_id}")
@require_role("psychologist", "director")
async def get_test(
    test_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("SELECT * FROM psych_tests WHERE id = :id"), {"id": test_id})
    t = row.fetchone()
    if not t:
        raise NotFoundError("Psixologik test")
    return dict(t._mapping)


@router.put("/tests/{test_id}")
@require_role("psychologist")
async def update_test(
    test_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        UPDATE psych_tests SET name = COALESCE(:name, name),
            description = COALESCE(:description, description),
            test_type = COALESCE(:test_type, test_type),
            updated_at = NOW()
        WHERE id = :id RETURNING id
    """), {**{k: data.get(k) for k in ("name", "description", "test_type")}, "id": test_id})
    if not result.fetchone():
        raise NotFoundError("Psixologik test")
    await db.commit()
    return {"message": "Psixologik test yangilandi"}


@router.delete("/tests/{test_id}")
@require_role("psychologist", "director")
async def delete_test(
    test_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("DELETE FROM psych_tests WHERE id = :id RETURNING id"), {"id": test_id})
    if not result.fetchone():
        raise NotFoundError("Psixologik test")
    await db.commit()
    return {"message": "Psixologik test o'chirildi"}


@router.post("/tests/{test_id}/conduct")
@require_role("psychologist")
async def conduct_test(
    test_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    check = await db.execute(text("SELECT id FROM psych_tests WHERE id = :id"), {"id": test_id})
    if not check.fetchone():
        raise NotFoundError("Psixologik test")

    row = await db.execute(text("""
        INSERT INTO psych_test_results (test_id, student_id, answers, score, evaluation, conducted_by, conducted_at)
        VALUES (:test_id, :student_id, :answers::jsonb, :score, :evaluation, :conducted_by, NOW())
        RETURNING id
    """), {
        "test_id": test_id, "student_id": data["student_id"],
        "answers": str(data.get("answers", "{}")), "score": data.get("score"),
        "evaluation": data.get("evaluation"), "conducted_by": current_user["id"],
    })
    await db.commit()
    return {"id": row.scalar(), "message": "Test o'tkazildi"}


# --- Counseling Sessions ---

@router.get("/sessions")
@require_role("psychologist", "director")
async def list_sessions(
    student_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    params: dict = {"limit": per_page, "offset": (page - 1) * per_page}
    where = ""
    if student_id:
        where = "WHERE cs.student_id = :student_id"
        params["student_id"] = student_id

    rows = await db.execute(text(f"""
        SELECT cs.id, cs.student_id, u.first_name, u.last_name, cs.session_date,
               cs.session_type, cs.summary, cs.recommendations, cs.created_at
        FROM counseling_sessions cs
        JOIN students s ON s.id = cs.student_id
        JOIN users u ON u.id = s.user_id
        {where} ORDER BY cs.session_date DESC LIMIT :limit OFFSET :offset
    """), params)
    return {"items": [dict(r._mapping) for r in rows]}


@router.post("/sessions", status_code=201)
@require_role("psychologist")
async def create_session(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        INSERT INTO counseling_sessions (student_id, session_date, session_type, summary, recommendations, conducted_by)
        VALUES (:student_id, :session_date, :session_type, :summary, :recommendations, :conducted_by)
        RETURNING id
    """), {
        "student_id": data["student_id"], "session_date": data["session_date"],
        "session_type": data.get("session_type", "individual"),
        "summary": data.get("summary"), "recommendations": data.get("recommendations"),
        "conducted_by": current_user["id"],
    })
    await db.commit()
    return {"id": row.scalar(), "message": "Maslahat sessiyasi yaratildi"}


@router.put("/sessions/{session_id}")
@require_role("psychologist")
async def update_session(
    session_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        UPDATE counseling_sessions SET summary = COALESCE(:summary, summary),
            recommendations = COALESCE(:recommendations, recommendations),
            session_type = COALESCE(:session_type, session_type),
            updated_at = NOW()
        WHERE id = :id RETURNING id
    """), {**{k: data.get(k) for k in ("summary", "recommendations", "session_type")}, "id": session_id})
    if not result.fetchone():
        raise NotFoundError("Maslahat sessiyasi")
    await db.commit()
    return {"message": "Maslahat sessiyasi yangilandi"}


@router.delete("/sessions/{session_id}")
@require_role("psychologist", "director")
async def delete_session(
    session_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("DELETE FROM counseling_sessions WHERE id = :id RETURNING id"), {"id": session_id})
    if not result.fetchone():
        raise NotFoundError("Maslahat sessiyasi")
    await db.commit()
    return {"message": "Maslahat sessiyasi o'chirildi"}


# --- Behavior Records ---

@router.get("/behavior")
@require_role("psychologist", "director", "teacher")
async def list_behavior(
    student_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    params: dict = {"limit": per_page, "offset": (page - 1) * per_page}
    where = ""
    if student_id:
        where = "WHERE br.student_id = :student_id"
        params["student_id"] = student_id

    rows = await db.execute(text(f"""
        SELECT br.id, br.student_id, u.first_name, u.last_name,
               br.behavior_type, br.description, br.severity, br.date, br.created_at
        FROM behavior_records br
        JOIN students s ON s.id = br.student_id
        JOIN users u ON u.id = s.user_id
        {where} ORDER BY br.date DESC LIMIT :limit OFFSET :offset
    """), params)
    return {"items": [dict(r._mapping) for r in rows]}


@router.post("/behavior", status_code=201)
@require_role("psychologist", "teacher")
async def create_behavior(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    row = await db.execute(text("""
        INSERT INTO behavior_records (student_id, behavior_type, description, severity, date, recorded_by)
        VALUES (:student_id, :behavior_type, :description, :severity, COALESCE(:date, CURRENT_DATE), :recorded_by)
        RETURNING id
    """), {
        "student_id": data["student_id"], "behavior_type": data["behavior_type"],
        "description": data.get("description"), "severity": data.get("severity", "low"),
        "date": data.get("date"), "recorded_by": current_user["id"],
    })
    await db.commit()
    return {"id": row.scalar(), "message": "Xulq-atvor yozuvi yaratildi"}


@router.put("/behavior/{behavior_id}")
@require_role("psychologist")
async def update_behavior(
    behavior_id: int,
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        UPDATE behavior_records SET description = COALESCE(:description, description),
            severity = COALESCE(:severity, severity),
            behavior_type = COALESCE(:behavior_type, behavior_type),
            updated_at = NOW()
        WHERE id = :id RETURNING id
    """), {**{k: data.get(k) for k in ("description", "severity", "behavior_type")}, "id": behavior_id})
    if not result.fetchone():
        raise NotFoundError("Xulq-atvor yozuvi")
    await db.commit()
    return {"message": "Xulq-atvor yozuvi yangilandi"}


@router.delete("/behavior/{behavior_id}")
@require_role("psychologist", "director")
async def delete_behavior(
    behavior_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("DELETE FROM behavior_records WHERE id = :id RETURNING id"), {"id": behavior_id})
    if not result.fetchone():
        raise NotFoundError("Xulq-atvor yozuvi")
    await db.commit()
    return {"message": "Xulq-atvor yozuvi o'chirildi"}

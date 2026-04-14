from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional

from app.core.dependencies import get_db, get_current_user
from app.core.rbac import require_permission, require_role

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/director-dashboard")
@require_role("director", "administrator", "super_admin")
async def director_dashboard(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stats = await db.execute(text("""
        SELECT
            (SELECT COUNT(*) FROM students WHERE deleted_at IS NULL) as total_students,
            (SELECT COUNT(*) FROM teachers WHERE deleted_at IS NULL) as total_teachers,
            (SELECT COUNT(*) FROM classes) as total_classes,
            (SELECT COUNT(*) FROM users WHERE is_active = true) as active_users,
            (SELECT ROUND(AVG(g.score), 1) FROM grades g) as avg_grade,
            (SELECT COUNT(*) FROM attendance WHERE date = CURRENT_DATE AND status = 'present') as today_present,
            (SELECT COUNT(*) FROM attendance WHERE date = CURRENT_DATE AND status = 'absent') as today_absent,
            (SELECT COALESCE(SUM(amount), 0) FROM payments WHERE status = 'paid'
                AND EXTRACT(MONTH FROM paid_at) = EXTRACT(MONTH FROM CURRENT_DATE)) as monthly_revenue
    """))
    return dict(stats.fetchone()._mapping)


@router.get("/teacher-dashboard")
@require_role("teacher", "director", "administrator")
async def teacher_dashboard(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    teacher = await db.execute(text("""
        SELECT t.id FROM teachers t WHERE t.user_id = :uid
    """), {"uid": current_user["id"]})
    teacher_row = teacher.fetchone()
    teacher_id = teacher_row[0] if teacher_row else None

    classes = await db.execute(text("""
        SELECT DISTINCT c.id, c.name, c.grade_level
        FROM schedules sc
        JOIN classes c ON c.id = sc.class_id
        WHERE sc.teacher_id = :tid
    """), {"tid": teacher_id})

    today_schedule = await db.execute(text("""
        SELECT sc.start_time, sc.end_time, sub.name as subject, c.name as class_name, r.name as room
        FROM schedules sc
        JOIN subjects sub ON sub.id = sc.subject_id
        JOIN classes c ON c.id = sc.class_id
        LEFT JOIN rooms r ON r.id = sc.room_id
        WHERE sc.teacher_id = :tid AND sc.day_of_week = EXTRACT(ISODOW FROM CURRENT_DATE)
        ORDER BY sc.start_time
    """), {"tid": teacher_id})

    recent_grades = await db.execute(text("""
        SELECT COUNT(*) as total_grades,
               ROUND(AVG(score), 1) as avg_score
        FROM grades WHERE teacher_id = :tid AND graded_at > CURRENT_DATE - INTERVAL '30 days'
    """), {"tid": teacher_id})

    return {
        "teacher_id": teacher_id,
        "classes": [dict(r._mapping) for r in classes],
        "today_schedule": [dict(r._mapping) for r in today_schedule],
        "recent_grades_stats": dict(recent_grades.fetchone()._mapping),
    }


@router.get("/parent-dashboard")
@require_role("parent", "director", "administrator")
async def parent_dashboard(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    parent = await db.execute(text("SELECT id FROM parents WHERE user_id = :uid"), {"uid": current_user["id"]})
    parent_row = parent.fetchone()
    parent_id = parent_row[0] if parent_row else None

    children = await db.execute(text("""
        SELECT s.id, su.first_name, su.last_name, c.name as class_name,
               (SELECT ROUND(AVG(g.score), 1) FROM grades g WHERE g.student_id = s.id) as avg_grade,
               (SELECT COUNT(*) FROM attendance a WHERE a.student_id = s.id
                    AND a.status = 'absent' AND a.date > CURRENT_DATE - INTERVAL '30 days') as monthly_absences
        FROM parent_students ps
        JOIN students s ON s.id = ps.student_id
        JOIN users su ON su.id = s.user_id
        LEFT JOIN classes c ON c.id = s.class_id
        WHERE ps.parent_id = :pid
    """), {"pid": parent_id})

    unread_notifications = (await db.execute(text("""
        SELECT COUNT(*) FROM notifications WHERE user_id = :uid AND read_at IS NULL
    """), {"uid": current_user["id"]})).scalar()

    return {
        "children": [dict(r._mapping) for r in children],
        "unread_notifications": unread_notifications,
    }


@router.get("/financial")
@require_role("director", "administrator", "accountant", "super_admin")
async def financial_report(
    month: Optional[int] = None,
    year: Optional[int] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conditions = ["p.status = 'paid'"]
    params: dict = {}
    if month:
        conditions.append("EXTRACT(MONTH FROM p.paid_at) = :month")
        params["month"] = month
    if year:
        conditions.append("EXTRACT(YEAR FROM p.paid_at) = :year")
        params["year"] = year

    where = "WHERE " + " AND ".join(conditions)

    revenue = await db.execute(text(f"""
        SELECT COALESCE(SUM(p.amount), 0) as total_revenue,
               COUNT(*) as total_payments,
               p.payment_method, COUNT(*) as count_per_method,
               SUM(p.amount) as amount_per_method
        FROM payments p {where}
        GROUP BY p.payment_method
    """), params)

    debts = await db.execute(text("""
        SELECT COUNT(DISTINCT s.id) as students_with_debt,
               COALESCE(SUM(f.amount) - COALESCE(SUM(p.amount), 0), 0) as total_debt
        FROM students s
        CROSS JOIN fees f
        LEFT JOIN payments p ON p.student_id = s.id AND p.fee_id = f.id AND p.status = 'paid'
        WHERE s.deleted_at IS NULL
        GROUP BY s.id, f.id
        HAVING f.amount - COALESCE(SUM(p.amount), 0) > 0
    """))

    return {
        "revenue_by_method": [dict(r._mapping) for r in revenue],
        "debt_summary": [dict(r._mapping) for r in debts],
    }


@router.get("/attendance-summary")
@require_permission("reports", "read")
async def attendance_summary(
    month: Optional[int] = None,
    year: Optional[int] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conditions = []
    params: dict = {}
    if month:
        conditions.append("EXTRACT(MONTH FROM a.date) = :month")
        params["month"] = month
    if year:
        conditions.append("EXTRACT(YEAR FROM a.date) = :year")
        params["year"] = year

    where = "WHERE " + " AND ".join(conditions) if conditions else ""

    rows = await db.execute(text(f"""
        SELECT c.name as class_name,
               COUNT(*) as total_records,
               COUNT(*) FILTER (WHERE a.status = 'present') as present,
               COUNT(*) FILTER (WHERE a.status = 'absent') as absent,
               COUNT(*) FILTER (WHERE a.status = 'late') as late,
               ROUND(100.0 * COUNT(*) FILTER (WHERE a.status = 'present') / NULLIF(COUNT(*), 0), 1) as attendance_rate
        FROM attendance a
        JOIN classes c ON c.id = a.class_id
        {where}
        GROUP BY c.name ORDER BY c.name
    """), params)
    return {"summary": [dict(r._mapping) for r in rows]}


@router.post("/custom")
@require_role("director", "administrator", "super_admin")
async def custom_report(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    report_type = data.get("report_type", "students")
    filters = data.get("filters", {})
    fields = data.get("fields", [])

    if report_type == "students":
        conditions = []
        params: dict = {}
        if filters.get("class_id"):
            conditions.append("s.class_id = :class_id")
            params["class_id"] = filters["class_id"]

        where = "WHERE s.deleted_at IS NULL"
        if conditions:
            where += " AND " + " AND ".join(conditions)

        rows = await db.execute(text(f"""
            SELECT s.id, s.student_code, u.first_name, u.last_name, u.phone,
                   c.name as class_name, s.created_at
            FROM students s
            JOIN users u ON u.id = s.user_id
            LEFT JOIN classes c ON c.id = s.class_id
            {where} ORDER BY u.last_name
        """), params)
        return {"report_type": report_type, "data": [dict(r._mapping) for r in rows]}

    elif report_type == "grades":
        rows = await db.execute(text("""
            SELECT c.name as class_name, sub.name as subject,
                   ROUND(AVG(g.score), 1) as avg_score,
                   COUNT(g.id) as grade_count
            FROM grades g
            JOIN students s ON s.id = g.student_id
            LEFT JOIN classes c ON c.id = s.class_id
            JOIN subjects sub ON sub.id = g.subject_id
            GROUP BY c.name, sub.name
            ORDER BY c.name, sub.name
        """))
        return {"report_type": report_type, "data": [dict(r._mapping) for r in rows]}

    return {"report_type": report_type, "data": [], "message": "Hisobot turi topilmadi"}

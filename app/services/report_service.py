import logging
from datetime import date
from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError

logger = logging.getLogger(__name__)


async def generate_attendance_report(
    db: AsyncSession,
    class_id: int,
    date_from: date,
    date_to: date,
) -> dict:
    if date_from > date_to:
        raise ValidationError("Boshlanish sanasi tugash sanasidan katta bo'lishi mumkin emas")

    cls_result = await db.execute(
        text("SELECT id, name, grade_level FROM classes WHERE id = :cid"),
        {"cid": class_id},
    )
    cls_row = cls_result.fetchone()
    if not cls_row:
        raise NotFoundError("Sinf")

    try:
        students_result = await db.execute(
            text(
                "SELECT s.id, s.student_id, u.first_name, u.last_name "
                "FROM students s "
                "JOIN users u ON u.id = s.user_id "
                "WHERE s.current_class_id = :cid AND s.status = 'active' "
                "ORDER BY u.last_name, u.first_name"
            ),
            {"cid": class_id},
        )
        students = [dict(r._mapping) for r in students_result.fetchall()]

        summary_result = await db.execute(
            text(
                "SELECT a.student_id, a.status, COUNT(*) as cnt "
                "FROM attendance a "
                "JOIN students s ON s.id = a.student_id "
                "WHERE s.current_class_id = :cid "
                "AND a.attendance_date BETWEEN :d_from AND :d_to "
                "GROUP BY a.student_id, a.status"
            ),
            {"cid": class_id, "d_from": date_from, "d_to": date_to},
        )
        summary_rows = summary_result.fetchall()

        attendance_map: dict[str, dict] = {}
        for row in summary_rows:
            sid = row.student_id
            if sid not in attendance_map:
                attendance_map[sid] = {"present": 0, "absent": 0, "late": 0, "excused": 0}
            attendance_map[sid][row.status] = row.cnt

        report_rows = []
        for student in students:
            stats = attendance_map.get(student["id"], {"present": 0, "absent": 0, "late": 0, "excused": 0})
            total = sum(stats.values())
            report_rows.append({
                "student_id": student["student_id"],
                "first_name": student["first_name"],
                "last_name": student["last_name"],
                **stats,
                "total_days": total,
                "attendance_rate": round(stats["present"] / total * 100, 1) if total else 0,
            })

        total_students = len(students)
        total_present = sum(r["present"] for r in report_rows)
        total_absent = sum(r["absent"] for r in report_rows)
        total_days = sum(r["total_days"] for r in report_rows)

        return {
            "class": {"id": cls_row.id, "name": cls_row.name, "grade_level": cls_row.grade_level},
            "period": {"from": date_from.isoformat(), "to": date_to.isoformat()},
            "summary": {
                "total_students": total_students,
                "total_present": total_present,
                "total_absent": total_absent,
                "overall_rate": round(total_present / total_days * 100, 1) if total_days else 0,
            },
            "students": report_rows,
        }
    except (ValidationError, NotFoundError):
        raise
    except Exception as e:
        logger.error(f"Attendance report generation error: {e}")
        raise


async def generate_grade_report(
    db: AsyncSession,
    student_id: str,
    academic_year_id: int,
) -> dict:
    student_result = await db.execute(
        text(
            "SELECT s.id, s.student_id, u.first_name, u.last_name, "
            "c.name as class_name, c.grade_level "
            "FROM students s "
            "JOIN users u ON u.id = s.user_id "
            "LEFT JOIN classes c ON c.id = s.current_class_id "
            "WHERE s.id = :sid"
        ),
        {"sid": student_id},
    )
    student_row = student_result.fetchone()
    if not student_row:
        raise NotFoundError("O'quvchi")

    year_result = await db.execute(
        text("SELECT id, name, start_date, end_date FROM academic_years WHERE id = :yid"),
        {"yid": academic_year_id},
    )
    year_row = year_result.fetchone()
    if not year_row:
        raise NotFoundError("O'quv yili")

    try:
        grades_result = await db.execute(
            text(
                "SELECT g.id, g.grade_value, g.max_grade, g.grade_date, g.comment, "
                "sub.name as subject_name, sub.code as subject_code, "
                "gt.name as grade_type, gt.weight_percent "
                "FROM grades g "
                "JOIN subjects sub ON sub.id = g.subject_id "
                "LEFT JOIN grade_types gt ON gt.id = g.grade_type_id "
                "WHERE g.student_id = :sid AND g.academic_year_id = :yid "
                "ORDER BY sub.name, g.grade_date"
            ),
            {"sid": student_id, "yid": academic_year_id},
        )
        grades = [dict(r._mapping) for r in grades_result.fetchall()]

        subjects_map: dict[str, list] = {}
        for g in grades:
            key = g["subject_code"]
            if key not in subjects_map:
                subjects_map[key] = []
            subjects_map[key].append(g)

        subject_summaries = []
        for code, grade_list in subjects_map.items():
            values = [g["grade_value"] for g in grade_list]
            max_vals = [g["max_grade"] for g in grade_list]
            avg = sum(values) / len(values) if values else 0
            subject_summaries.append({
                "subject": grade_list[0]["subject_name"],
                "subject_code": code,
                "grades_count": len(grade_list),
                "average": round(avg, 1),
                "min": min(values) if values else 0,
                "max": max(values) if values else 0,
                "grades": grade_list,
            })

        all_values = [g["grade_value"] for g in grades]
        gpa = round(sum(all_values) / len(all_values), 2) if all_values else 0

        report_card_result = await db.execute(
            text(
                "SELECT gpa, teacher_comments, principal_comments, issue_date "
                "FROM report_cards "
                "WHERE student_id = :sid AND academic_year_id = :yid "
                "ORDER BY semester DESC LIMIT 1"
            ),
            {"sid": student_id, "yid": academic_year_id},
        )
        report_card = report_card_result.fetchone()

        return {
            "student": {
                "id": student_row.id,
                "student_id": student_row.student_id,
                "first_name": student_row.first_name,
                "last_name": student_row.last_name,
                "class": student_row.class_name,
                "grade_level": student_row.grade_level,
            },
            "academic_year": {
                "id": year_row.id,
                "name": year_row.name,
            },
            "summary": {
                "total_subjects": len(subject_summaries),
                "total_grades": len(grades),
                "gpa": gpa,
                "official_gpa": float(report_card.gpa) if report_card and report_card.gpa else None,
            },
            "subjects": subject_summaries,
        }
    except (NotFoundError,):
        raise
    except Exception as e:
        logger.error(f"Grade report generation error: {e}")
        raise


async def generate_financial_report(
    db: AsyncSession,
    date_from: date,
    date_to: date,
    tenant_id: Optional[int] = None,
) -> dict:
    if date_from > date_to:
        raise ValidationError("Boshlanish sanasi tugash sanasidan katta bo'lishi mumkin emas")

    try:
        totals_result = await db.execute(
            text(
                "SELECT "
                "  COUNT(*) as total_payments, "
                "  COALESCE(SUM(CASE WHEN status = 'completed' THEN amount ELSE 0 END), 0) as total_received, "
                "  COALESCE(SUM(CASE WHEN status = 'pending' THEN amount ELSE 0 END), 0) as total_pending, "
                "  COALESCE(SUM(CASE WHEN status = 'failed' THEN amount ELSE 0 END), 0) as total_failed, "
                "  COALESCE(SUM(amount), 0) as total_amount "
                "FROM payments "
                "WHERE payment_date BETWEEN :d_from AND :d_to"
            ),
            {"d_from": date_from, "d_to": date_to},
        )
        totals = dict(totals_result.fetchone()._mapping)

        by_type_result = await db.execute(
            text(
                "SELECT payment_type, "
                "  COUNT(*) as count, "
                "  COALESCE(SUM(amount), 0) as total "
                "FROM payments "
                "WHERE payment_date BETWEEN :d_from AND :d_to "
                "GROUP BY payment_type "
                "ORDER BY total DESC"
            ),
            {"d_from": date_from, "d_to": date_to},
        )
        by_type = [dict(r._mapping) for r in by_type_result.fetchall()]

        by_method_result = await db.execute(
            text(
                "SELECT COALESCE(payment_method, 'unknown') as method, "
                "  COUNT(*) as count, "
                "  COALESCE(SUM(amount), 0) as total "
                "FROM payments "
                "WHERE payment_date BETWEEN :d_from AND :d_to AND status = 'completed' "
                "GROUP BY payment_method "
                "ORDER BY total DESC"
            ),
            {"d_from": date_from, "d_to": date_to},
        )
        by_method = [dict(r._mapping) for r in by_method_result.fetchall()]

        monthly_result = await db.execute(
            text(
                "SELECT "
                "  TO_CHAR(payment_date, 'YYYY-MM') as month, "
                "  COUNT(*) as count, "
                "  COALESCE(SUM(CASE WHEN status = 'completed' THEN amount ELSE 0 END), 0) as received "
                "FROM payments "
                "WHERE payment_date BETWEEN :d_from AND :d_to "
                "GROUP BY TO_CHAR(payment_date, 'YYYY-MM') "
                "ORDER BY month"
            ),
            {"d_from": date_from, "d_to": date_to},
        )
        monthly = [dict(r._mapping) for r in monthly_result.fetchall()]

        overdue_result = await db.execute(
            text(
                "SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total "
                "FROM payments "
                "WHERE status = 'pending' AND due_date < CURRENT_DATE"
            ),
        )
        overdue = dict(overdue_result.fetchone()._mapping)

        return {
            "period": {"from": date_from.isoformat(), "to": date_to.isoformat()},
            "totals": {
                "total_payments": totals["total_payments"],
                "total_received": float(totals["total_received"]),
                "total_pending": float(totals["total_pending"]),
                "total_failed": float(totals["total_failed"]),
                "total_amount": float(totals["total_amount"]),
            },
            "by_type": by_type,
            "by_method": by_method,
            "monthly_breakdown": monthly,
            "overdue": {
                "count": overdue["count"],
                "total": float(overdue["total"]),
            },
        }
    except (ValidationError,):
        raise
    except Exception as e:
        logger.error(f"Financial report generation error: {e}")
        raise

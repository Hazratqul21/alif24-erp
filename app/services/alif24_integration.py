"""
Alif24 Integration Service

Alif24 platformasidan foydalanuvchi ma'lumotlarini olish va ERP bilan bog'lash.
Alif24 database'iga faqat O'QISH (SELECT) bilan murojaat qilinadi.
ERP database'iga YOZISH amalga oshiriladi.

Alif24 jadval tuzilishi:
  - users: id(8-char), first_name, last_name, phone, email, role, avatar, date_of_birth, gender
  - student_profiles: user_id, grade, school_name, level, total_points, average_score, total_lessons_completed, total_games_played
  - teacher_profiles: user_id, specialization, subjects, qualification, years_of_experience, rating
  - parent_profiles: user_id, occupation
"""
import logging
from typing import Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Alif24SessionLocal
from app.core.exceptions import AppError, NotFoundError

logger = logging.getLogger(__name__)


def _check_alif24_connection():
    if Alif24SessionLocal is None:
        raise AppError(
            "Alif24 database ulanishi sozlanmagan. "
            "ALIF24_DATABASE_URL environment variable o'rnating.",
            status_code=503,
        )


async def lookup_alif24_user(alif24_id: str) -> Optional[dict]:
    """
    Alif24 dagi foydalanuvchini ID bo'yicha qidirish.
    Faqat O'QISH — alif24 database'iga hech narsa yozilmaydi.
    """
    _check_alif24_connection()

    async with Alif24SessionLocal() as session:
        result = await session.execute(
            text("""
                SELECT u.id, u.first_name, u.last_name, u.phone, u.email,
                       u.role, u.avatar, u.date_of_birth, u.gender,
                       u.username, u.status, u.created_at
                FROM users u
                WHERE u.id = :uid AND u.status = 'active'
            """),
            {"uid": alif24_id},
        )
        row = result.fetchone()
        if not row:
            return None

        user_data = {
            "alif24_id": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "phone": row[3],
            "email": row[4],
            "role": row[5],
            "avatar": row[6],
            "date_of_birth": str(row[7]) if row[7] else None,
            "gender": row[8],
            "username": row[9],
            "status": row[10],
            "created_at": str(row[11]) if row[11] else None,
        }

        # Agar o'quvchi bo'lsa — student_profiles dan qo'shimcha ma'lumot
        if row[5] == "student":
            sp = await session.execute(
                text("""
                    SELECT sp.grade, sp.school_name, sp.level, sp.total_points,
                           sp.average_score, sp.total_lessons_completed,
                           sp.total_games_played, sp.total_time_spent,
                           sp.current_streak, sp.longest_streak
                    FROM student_profiles sp
                    WHERE sp.user_id = :uid
                """),
                {"uid": alif24_id},
            )
            sp_row = sp.fetchone()
            if sp_row:
                user_data["student_profile"] = {
                    "grade": sp_row[0],
                    "school_name": sp_row[1],
                    "level": sp_row[2],
                    "total_points": sp_row[3],
                    "average_score": float(sp_row[4]) if sp_row[4] else 0.0,
                    "total_lessons_completed": sp_row[5],
                    "total_games_played": sp_row[6],
                    "total_time_spent_minutes": sp_row[7],
                    "current_streak": sp_row[8],
                    "longest_streak": sp_row[9],
                }

        # Agar o'qituvchi bo'lsa
        elif row[5] == "teacher":
            tp = await session.execute(
                text("""
                    SELECT tp.specialization, tp.qualification,
                           tp.years_of_experience, tp.subjects, tp.rating,
                           tp.total_students, tp.total_classrooms
                    FROM teacher_profiles tp
                    WHERE tp.user_id = :uid
                """),
                {"uid": alif24_id},
            )
            tp_row = tp.fetchone()
            if tp_row:
                user_data["teacher_profile"] = {
                    "specialization": tp_row[0],
                    "qualification": tp_row[1],
                    "years_of_experience": tp_row[2],
                    "subjects": tp_row[3],
                    "rating": float(tp_row[4]) if tp_row[4] else 0.0,
                    "total_students": tp_row[5],
                    "total_classrooms": tp_row[6],
                }

        # Agar ota-ona bo'lsa
        elif row[5] == "parent":
            pp = await session.execute(
                text("""
                    SELECT pp.occupation
                    FROM parent_profiles pp
                    WHERE pp.user_id = :uid
                """),
                {"uid": alif24_id},
            )
            pp_row = pp.fetchone()
            if pp_row:
                user_data["parent_profile"] = {"occupation": pp_row[0]}

            # Ota-onaning bolalarini ham olish
            children = await session.execute(
                text("""
                    SELECT u.id, u.first_name, u.last_name, u.username,
                           sp.grade, sp.level, sp.average_score
                    FROM users u
                    LEFT JOIN student_profiles sp ON sp.user_id = u.id
                    WHERE u.parent_id = :uid AND u.status = 'active'
                """),
                {"uid": alif24_id},
            )
            user_data["children"] = [
                {
                    "alif24_id": c[0],
                    "first_name": c[1],
                    "last_name": c[2],
                    "username": c[3],
                    "grade": c[4],
                    "level": c[5],
                    "average_score": float(c[6]) if c[6] else 0.0,
                }
                for c in children
            ]

        return user_data


async def search_alif24_users(
    query: str,
    role: Optional[str] = None,
    limit: int = 20,
) -> list[dict]:
    """
    Alif24 da foydalanuvchilarni qidirish (ism, telefon, email, ID bo'yicha).
    Faqat O'QISH.
    """
    _check_alif24_connection()

    async with Alif24SessionLocal() as session:
        conditions = ["u.status = 'active'"]
        params: dict = {"limit": limit}

        if query:
            conditions.append(
                "(u.first_name ILIKE :q OR u.last_name ILIKE :q "
                "OR u.phone ILIKE :q OR u.email ILIKE :q OR u.id = :exact_q)"
            )
            params["q"] = f"%{query}%"
            params["exact_q"] = query

        if role:
            conditions.append("u.role = :role")
            params["role"] = role

        where = " AND ".join(conditions)

        result = await session.execute(
            text(f"""
                SELECT u.id, u.first_name, u.last_name, u.phone, u.email,
                       u.role, u.avatar, u.date_of_birth
                FROM users u
                WHERE {where}
                ORDER BY u.last_name, u.first_name
                LIMIT :limit
            """),
            params,
        )

        return [
            {
                "alif24_id": row[0],
                "first_name": row[1],
                "last_name": row[2],
                "phone": row[3],
                "email": row[4],
                "role": row[5],
                "avatar": row[6],
                "date_of_birth": str(row[7]) if row[7] else None,
            }
            for row in result
        ]


async def link_alif24_user_to_erp(
    erp_db: AsyncSession,
    erp_user_id: str,
    alif24_id: str,
) -> dict:
    """
    Mavjud ERP foydalanuvchisini Alif24 ID bilan bog'lash.
    ERP database'ga yozadi, Alif24 ga tegmaydi.
    """
    alif24_user = await lookup_alif24_user(alif24_id)
    if not alif24_user:
        raise NotFoundError(f"Alif24 da {alif24_id} ID li foydalanuvchi topilmadi")

    # ERP dagi foydalanuvchini yangilash
    result = await erp_db.execute(
        text("UPDATE users SET alif24_user_id = :a24id WHERE id = :uid RETURNING id"),
        {"a24id": alif24_id, "uid": erp_user_id},
    )
    if not result.fetchone():
        raise NotFoundError("ERP foydalanuvchisi topilmadi")

    await erp_db.commit()
    logger.info(f"ERP user {erp_user_id} linked to Alif24 user {alif24_id}")

    return {
        "erp_user_id": erp_user_id,
        "alif24_id": alif24_id,
        "alif24_name": f"{alif24_user['first_name']} {alif24_user['last_name']}",
        "alif24_role": alif24_user["role"],
    }


async def import_student_from_alif24(
    erp_db: AsyncSession,
    alif24_id: str,
    class_id: Optional[int] = None,
    student_code: Optional[str] = None,
) -> dict:
    """
    Alif24 dagi o'quvchini ERP ga import qilish.
    Alif24 dan ma'lumotlarni O'QIYDI, ERP ga YOZADI.
    """
    alif24_user = await lookup_alif24_user(alif24_id)
    if not alif24_user:
        raise NotFoundError(f"Alif24 da {alif24_id} ID li foydalanuvchi topilmadi")

    # Allaqachon import qilinganmi tekshirish
    existing = await erp_db.execute(
        text("SELECT id FROM users WHERE alif24_user_id = :a24id"),
        {"a24id": alif24_id},
    )
    if existing.fetchone():
        raise AppError(
            f"Bu foydalanuvchi allaqachon ERP ga qo'shilgan (Alif24 ID: {alif24_id})",
            status_code=409,
        )

    from app.core.database import generate_uuid
    from app.core.auth import hash_password

    user_id = generate_uuid()
    temp_password = f"alif24_{alif24_id}"

    # ERP da yangi user yaratish (Alif24 ma'lumotlari bilan)
    await erp_db.execute(
        text("""
            INSERT INTO users (id, email, phone, first_name, last_name, password_hash,
                               is_active, alif24_user_id, birth_date, gender, avatar)
            VALUES (:id, :email, :phone, :first_name, :last_name, :password_hash,
                    true, :alif24_user_id, :birth_date, :gender, :avatar)
        """),
        {
            "id": user_id,
            "email": alif24_user.get("email"),
            "phone": alif24_user.get("phone"),
            "first_name": alif24_user["first_name"],
            "last_name": alif24_user["last_name"],
            "password_hash": hash_password(temp_password),
            "alif24_user_id": alif24_id,
            "birth_date": alif24_user.get("date_of_birth"),
            "gender": alif24_user.get("gender"),
            "avatar": alif24_user.get("avatar"),
        },
    )

    # Student yozuvini yaratish
    await erp_db.execute(
        text("""
            INSERT INTO students (user_id, student_code, class_id)
            VALUES (:user_id, :student_code, :class_id)
            RETURNING id
        """),
        {
            "user_id": user_id,
            "student_code": student_code,
            "class_id": class_id,
        },
    )

    # Student rolini berish
    await erp_db.execute(
        text("""
            INSERT INTO user_roles (user_id, role_id)
            SELECT :uid, id FROM roles WHERE name = 'student'
        """),
        {"uid": user_id},
    )

    await erp_db.commit()
    logger.info(f"Student imported from Alif24: {alif24_id} -> ERP user {user_id}")

    return {
        "erp_user_id": user_id,
        "alif24_id": alif24_id,
        "first_name": alif24_user["first_name"],
        "last_name": alif24_user["last_name"],
        "role_in_alif24": alif24_user["role"],
        "student_profile": alif24_user.get("student_profile"),
        "message": "O'quvchi Alif24 dan muvaffaqiyatli import qilindi",
    }


async def import_teacher_from_alif24(
    erp_db: AsyncSession,
    alif24_id: str,
) -> dict:
    """
    Alif24 dagi o'qituvchini ERP ga import qilish.
    """
    alif24_user = await lookup_alif24_user(alif24_id)
    if not alif24_user:
        raise NotFoundError(f"Alif24 da {alif24_id} ID li foydalanuvchi topilmadi")

    existing = await erp_db.execute(
        text("SELECT id FROM users WHERE alif24_user_id = :a24id"),
        {"a24id": alif24_id},
    )
    if existing.fetchone():
        raise AppError(
            f"Bu foydalanuvchi allaqachon ERP ga qo'shilgan (Alif24 ID: {alif24_id})",
            status_code=409,
        )

    from app.core.database import generate_uuid
    from app.core.auth import hash_password

    user_id = generate_uuid()
    temp_password = f"alif24_{alif24_id}"

    await erp_db.execute(
        text("""
            INSERT INTO users (id, email, phone, first_name, last_name, password_hash,
                               is_active, alif24_user_id, birth_date, gender, avatar)
            VALUES (:id, :email, :phone, :first_name, :last_name, :password_hash,
                    true, :alif24_user_id, :birth_date, :gender, :avatar)
        """),
        {
            "id": user_id,
            "email": alif24_user.get("email"),
            "phone": alif24_user.get("phone"),
            "first_name": alif24_user["first_name"],
            "last_name": alif24_user["last_name"],
            "password_hash": hash_password(temp_password),
            "alif24_user_id": alif24_id,
            "birth_date": alif24_user.get("date_of_birth"),
            "gender": alif24_user.get("gender"),
            "avatar": alif24_user.get("avatar"),
        },
    )

    tp = alif24_user.get("teacher_profile", {})
    await erp_db.execute(
        text("""
            INSERT INTO teachers (user_id, specialization, qualification)
            VALUES (:user_id, :specialization, :qualification)
        """),
        {
            "user_id": user_id,
            "specialization": tp.get("specialization"),
            "qualification": tp.get("qualification"),
        },
    )

    await erp_db.execute(
        text("""
            INSERT INTO user_roles (user_id, role_id)
            SELECT :uid, id FROM roles WHERE name = 'teacher'
        """),
        {"uid": user_id},
    )

    await erp_db.commit()
    logger.info(f"Teacher imported from Alif24: {alif24_id} -> ERP user {user_id}")

    return {
        "erp_user_id": user_id,
        "alif24_id": alif24_id,
        "first_name": alif24_user["first_name"],
        "last_name": alif24_user["last_name"],
        "teacher_profile": tp,
        "message": "O'qituvchi Alif24 dan muvaffaqiyatli import qilindi",
    }


async def import_parent_from_alif24(
    erp_db: AsyncSession,
    alif24_id: str,
) -> dict:
    """
    Alif24 dagi ota-onani ERP ga import qilish.
    Bolalarni ham avtomatik qidiradi.
    """
    alif24_user = await lookup_alif24_user(alif24_id)
    if not alif24_user:
        raise NotFoundError(f"Alif24 da {alif24_id} ID li foydalanuvchi topilmadi")

    existing = await erp_db.execute(
        text("SELECT id FROM users WHERE alif24_user_id = :a24id"),
        {"a24id": alif24_id},
    )
    if existing.fetchone():
        raise AppError(
            f"Bu foydalanuvchi allaqachon ERP ga qo'shilgan (Alif24 ID: {alif24_id})",
            status_code=409,
        )

    from app.core.database import generate_uuid
    from app.core.auth import hash_password

    user_id = generate_uuid()
    temp_password = f"alif24_{alif24_id}"

    await erp_db.execute(
        text("""
            INSERT INTO users (id, email, phone, first_name, last_name, password_hash,
                               is_active, alif24_user_id, avatar)
            VALUES (:id, :email, :phone, :first_name, :last_name, :password_hash,
                    true, :alif24_user_id, :avatar)
        """),
        {
            "id": user_id,
            "email": alif24_user.get("email"),
            "phone": alif24_user.get("phone"),
            "first_name": alif24_user["first_name"],
            "last_name": alif24_user["last_name"],
            "password_hash": hash_password(temp_password),
            "alif24_user_id": alif24_id,
            "avatar": alif24_user.get("avatar"),
        },
    )

    await erp_db.execute(
        text("""
            INSERT INTO parents (user_id, occupation)
            VALUES (:user_id, :occupation)
        """),
        {
            "user_id": user_id,
            "occupation": alif24_user.get("parent_profile", {}).get("occupation"),
        },
    )

    await erp_db.execute(
        text("""
            INSERT INTO user_roles (user_id, role_id)
            SELECT :uid, id FROM roles WHERE name = 'parent'
        """),
        {"uid": user_id},
    )

    await erp_db.commit()
    logger.info(f"Parent imported from Alif24: {alif24_id} -> ERP user {user_id}")

    return {
        "erp_user_id": user_id,
        "alif24_id": alif24_id,
        "first_name": alif24_user["first_name"],
        "last_name": alif24_user["last_name"],
        "children_in_alif24": alif24_user.get("children", []),
        "message": "Ota-ona Alif24 dan muvaffaqiyatli import qilindi",
    }


async def sync_alif24_results(
    erp_db: AsyncSession,
    erp_user_id: str,
) -> dict:
    """
    ERP foydalanuvchisining Alif24 dagi eng so'nggi natijalarini olish.
    Alif24 dan O'QIYDI, ERP dagi hech narsani o'zgartirmaydi.
    """
    _check_alif24_connection()

    # ERP dan alif24_user_id ni olish
    result = await erp_db.execute(
        text("SELECT alif24_user_id FROM users WHERE id = :uid"),
        {"uid": erp_user_id},
    )
    row = result.fetchone()
    if not row or not row[0]:
        raise AppError("Bu foydalanuvchi Alif24 ga bog'lanmagan")

    alif24_id = row[0]

    async with Alif24SessionLocal() as a24_session:
        # O'quvchi natijalarini olish
        sp = await a24_session.execute(
            text("""
                SELECT sp.level, sp.total_points, sp.average_score,
                       sp.total_lessons_completed, sp.total_games_played,
                       sp.total_time_spent, sp.current_streak, sp.longest_streak,
                       sp.total_coins
                FROM student_profiles sp
                WHERE sp.user_id = :uid
            """),
            {"uid": alif24_id},
        )
        sp_row = sp.fetchone()

        if not sp_row:
            return {
                "alif24_id": alif24_id,
                "message": "Alif24 da o'quvchi profili topilmadi",
                "results": None,
            }

        results = {
            "alif24_id": alif24_id,
            "level": sp_row[0],
            "total_points": sp_row[1],
            "average_score": float(sp_row[2]) if sp_row[2] else 0.0,
            "total_lessons_completed": sp_row[3],
            "total_games_played": sp_row[4],
            "total_time_spent_minutes": sp_row[5],
            "current_streak": sp_row[6],
            "longest_streak": sp_row[7],
            "total_coins": sp_row[8],
        }

        return {
            "alif24_id": alif24_id,
            "message": "Alif24 natijalari muvaffaqiyatli olindi",
            "results": results,
        }


async def bulk_import_students_from_alif24(
    erp_db: AsyncSession,
    alif24_ids: list[str],
    class_id: Optional[int] = None,
) -> dict:
    """
    Bir nechta o'quvchini Alif24 dan ERP ga import qilish.
    """
    imported = []
    errors = []

    for alif24_id in alif24_ids:
        try:
            result = await import_student_from_alif24(
                erp_db, alif24_id, class_id=class_id
            )
            imported.append(result)
        except Exception as e:
            errors.append({"alif24_id": alif24_id, "error": str(e)})

    return {
        "imported_count": len(imported),
        "error_count": len(errors),
        "imported": imported,
        "errors": errors,
    }

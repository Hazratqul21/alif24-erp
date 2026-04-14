"""
Alif24 Integration API

O'quv markaz admin panelidan Alif24 platformasidagi foydalanuvchilarni
qidirib, ularni ERP ga import qilish uchun endpointlar.

Jarayon:
  1. Admin Alif24 ID yoki ism/telefon bilan qidiradi → /search, /lookup
  2. Topilgan foydalanuvchini ERP ga import qiladi → /import/student, /import/teacher
  3. Alif24 dagi natijalarini ko'radi → /results/{erp_user_id}
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.dependencies import get_db, get_current_user
from app.core.rbac import require_permission
from app.services.alif24_integration import (
    lookup_alif24_user,
    search_alif24_users,
    link_alif24_user_to_erp,
    import_student_from_alif24,
    import_teacher_from_alif24,
    import_parent_from_alif24,
    sync_alif24_results,
    bulk_import_students_from_alif24,
)

router = APIRouter(tags=["Alif24 Integration"])


@router.get("/lookup/{alif24_id}")
@require_permission("students", "read")
async def lookup_user(
    alif24_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Alif24 dagi foydalanuvchini ID bo'yicha ko'rish.
    O'quv markaz admini ID kiritib, bolaning to'liq ma'lumotlarini ko'radi.
    """
    user = await lookup_alif24_user(alif24_id)
    if not user:
        return {"found": False, "message": f"Alif24 da {alif24_id} ID topilmadi"}
    return {"found": True, "user": user}


@router.get("/search")
@require_permission("students", "read")
async def search_users(
    q: str = Query(..., min_length=2, description="Ism, telefon, email yoki ID"),
    role: Optional[str] = Query(None, description="student, teacher, parent"),
    limit: int = Query(20, ge=1, le=50),
    current_user: dict = Depends(get_current_user),
):
    """
    Alif24 dan foydalanuvchi qidirish.
    Ism, familiya, telefon, email yoki ID bo'yicha qidiradi.
    """
    users = await search_alif24_users(q, role=role, limit=limit)
    return {"count": len(users), "users": users}


@router.post("/import/student")
@require_permission("students", "create")
async def import_student(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Alif24 dagi o'quvchini ERP ga qo'shish.

    Body:
        alif24_id: str  — Alif24 dagi foydalanuvchi ID si
        class_id: int (optional) — ERP dagi sinf ID
        student_code: str (optional) — ERP dagi o'quvchi kodi
    """
    result = await import_student_from_alif24(
        erp_db=db,
        alif24_id=data["alif24_id"],
        class_id=data.get("class_id"),
        student_code=data.get("student_code"),
    )
    return result


@router.post("/import/teacher")
@require_permission("teachers", "create")
async def import_teacher(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Alif24 dagi o'qituvchini ERP ga qo'shish.

    Body:
        alif24_id: str — Alif24 dagi foydalanuvchi ID si
    """
    result = await import_teacher_from_alif24(
        erp_db=db,
        alif24_id=data["alif24_id"],
    )
    return result


@router.post("/import/parent")
@require_permission("parents", "create")
async def import_parent(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Alif24 dagi ota-onani ERP ga qo'shish.

    Body:
        alif24_id: str — Alif24 dagi foydalanuvchi ID si
    """
    result = await import_parent_from_alif24(
        erp_db=db,
        alif24_id=data["alif24_id"],
    )
    return result


@router.post("/import/students/bulk")
@require_permission("students", "create")
async def bulk_import_students(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Bir nechta o'quvchini Alif24 dan ERP ga import qilish.

    Body:
        alif24_ids: list[str] — Alif24 foydalanuvchi ID lari ro'yxati
        class_id: int (optional) — Barchani shu sinfga qo'shish
    """
    result = await bulk_import_students_from_alif24(
        erp_db=db,
        alif24_ids=data["alif24_ids"],
        class_id=data.get("class_id"),
    )
    return result


@router.get("/results/{erp_user_id}")
@require_permission("students", "read")
async def get_alif24_results(
    erp_user_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    ERP foydalanuvchisining Alif24 dagi natijalarini ko'rish.
    O'quv markaz admini har qanday paytda bolaning Alif24 dagi
    o'yin natijalari, darslari, baholarini ko'ra oladi.
    """
    result = await sync_alif24_results(erp_db=db, erp_user_id=erp_user_id)
    return result


@router.post("/link")
@require_permission("students", "update")
async def link_user(
    data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Mavjud ERP foydalanuvchisini Alif24 ID bilan bog'lash.
    Agar o'quvchi ERP da bor, lekin Alif24 ga bog'lanmagan bo'lsa.

    Body:
        erp_user_id: str — ERP dagi foydalanuvchi ID
        alif24_id: str — Alif24 dagi foydalanuvchi ID
    """
    result = await link_alif24_user_to_erp(
        erp_db=db,
        erp_user_id=data["erp_user_id"],
        alif24_id=data["alif24_id"],
    )
    return result

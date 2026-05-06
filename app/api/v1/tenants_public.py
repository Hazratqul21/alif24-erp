from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.dependencies import get_public_db
from app.core.exceptions import NotFoundError

router = APIRouter(tags=["Tenants (public)"])


@router.get("/by-subdomain/{subdomain}")
async def get_tenant_by_subdomain(
    subdomain: str,
    db: AsyncSession = Depends(get_public_db),
):
    """Frontend TenantContext tomonidan ishlatiladi — subdomain bo'yicha maktab ma'lumotlarini qaytaradi."""
    row = await db.execute(
        text("""
            SELECT id, name, subdomain, domain, logo, is_active, region, address
            FROM tenants
            WHERE subdomain = :sub AND deleted_at IS NULL AND is_active = true
        """),
        {"sub": subdomain},
    )
    tenant = row.fetchone()
    if not tenant:
        raise NotFoundError("Maktab")
    return dict(tenant._mapping)

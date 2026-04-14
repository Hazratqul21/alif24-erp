from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text, event
from typing import Optional
import uuid

from app.config import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_pre_ping=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_recycle=300,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

alif24_engine = None
Alif24SessionLocal = None

if settings.ALIF24_DATABASE_URL:
    alif24_engine = create_async_engine(
        settings.ALIF24_DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=5,
        pool_recycle=300,
    )
    Alif24SessionLocal = async_sessionmaker(
        alif24_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


def generate_uuid() -> str:
    return str(uuid.uuid4())


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_tenant_db(schema_name: str) -> AsyncSession:
    async with AsyncSessionLocal() as session:
        await session.execute(text(f"SET search_path TO {schema_name}, public"))
        try:
            yield session
        finally:
            await session.close()


async def get_alif24_db() -> Optional[AsyncSession]:
    if Alif24SessionLocal is None:
        yield None
        return
    async with Alif24SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def set_tenant_schema(session: AsyncSession, tenant_id: int):
    schema_name = f"tenant_{tenant_id}"
    await session.execute(text(f"SET search_path TO {schema_name}, public"))


async def create_tenant_schema(session: AsyncSession, tenant_id: int):
    schema_name = f"tenant_{tenant_id}"
    await session.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
    await session.commit()


async def drop_tenant_schema(session: AsyncSession, tenant_id: int):
    schema_name = f"tenant_{tenant_id}"
    await session.execute(text(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE"))
    await session.commit()


async def create_tenant_tables(tenant_id: int):
    """Create all tenant-specific tables in the tenant's schema."""
    from app.models.tenant import (
        user, role, student, teacher, parent, academic,
        schedule, attendance, grade, payment, library,
        medical, psychology, discipline, canteen, transport,
        notification, document, competition, room, homework,
        exam, admission, portfolio, survey, audit, holiday,
    )

    schema_name = f"tenant_{tenant_id}"

    def _set_schema(target, connection, **kw):
        connection.execute(text(f"SET search_path TO {schema_name}, public"))

    tenant_tables = []
    for model_module in [
        user, role, student, teacher, parent, academic,
        schedule, attendance, grade, payment, library,
        medical, psychology, discipline, canteen, transport,
        notification, document, competition, room, homework,
        exam, admission, portfolio, survey, audit, holiday,
    ]:
        for attr_name in dir(model_module):
            attr = getattr(model_module, attr_name)
            if hasattr(attr, "__tablename__") and hasattr(attr, "metadata"):
                tenant_tables.append(attr.__table__)

    async with engine.begin() as conn:
        await conn.execute(text(f"SET search_path TO {schema_name}, public"))
        await conn.run_sync(Base.metadata.create_all, tables=tenant_tables)


async def init_public_schema():
    """Create public schema tables (tenants, plans, central_books, etc.)."""
    from app.models.public import tenant, plan, central_book, school_location  # noqa

    async with engine.begin() as conn:
        await conn.execute(text("SET search_path TO public"))
        await conn.run_sync(Base.metadata.create_all)

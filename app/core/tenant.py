from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from sqlalchemy import select, text
from datetime import date, datetime
import logging

from app.core.database import AsyncSessionLocal
from app.core.cache import cache_get, cache_set
from app.config import settings

logger = logging.getLogger(__name__)

SUPERADMIN_SUBDOMAINS = {"admin", "erp"}
PUBLIC_PATHS = {"/api/v1/auth/login", "/api/v1/auth/refresh", "/health", "/", "/docs", "/openapi.json", "/redoc"}


class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        host = request.headers.get("host", "")
        path = request.url.path

        if path in PUBLIC_PATHS or path.startswith("/docs") or path.startswith("/redoc"):
            request.state.tenant = None
            request.state.schema_name = "public"
            return await call_next(request)

        subdomain = self._extract_subdomain(host)

        if not subdomain or subdomain in SUPERADMIN_SUBDOMAINS:
            request.state.tenant = None
            request.state.schema_name = "public"
            request.state.is_superadmin = subdomain in SUPERADMIN_SUBDOMAINS
            return await call_next(request)

        tenant = await self._resolve_tenant(subdomain)

        if tenant is None:
            return JSONResponse(
                status_code=404,
                content={"detail": "Maktab topilmadi"},
            )

        if not tenant["is_active"]:
            return JSONResponse(
                status_code=403,
                content={"detail": "Maktab bloklangan"},
            )

        if tenant["subscription_end"] and tenant["subscription_end"] < date.today().isoformat():
            return JSONResponse(
                status_code=403,
                content={"detail": "Obuna muddati tugagan"},
            )

        request.state.tenant = tenant
        request.state.schema_name = f"tenant_{tenant['id']}"
        request.state.tenant_id = tenant["id"]

        return await call_next(request)

    def _extract_subdomain(self, host: str) -> str | None:
        host = host.split(":")[0]
        base = settings.BASE_DOMAIN

        if host == base or host == f"www.{base}":
            return None

        if host.endswith(f".{base}"):
            subdomain = host[: -(len(base) + 1)]
            return subdomain if subdomain else None

        if host in ("localhost", "127.0.0.1"):
            return None

        return None

    async def _resolve_tenant(self, subdomain: str) -> dict | None:
        cache_key = f"tenant:{subdomain}"
        cached = await cache_get(cache_key)
        if cached:
            return cached

        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    text("SELECT id, subdomain, name, is_active, subscription_end, plan_id FROM tenants WHERE subdomain = :sub"),
                    {"sub": subdomain},
                )
                row = result.fetchone()
                if row is None:
                    return None

                tenant_data = {
                    "id": row[0],
                    "subdomain": row[1],
                    "name": row[2],
                    "is_active": row[3],
                    "subscription_end": row[4].isoformat() if row[4] else None,
                    "plan_id": row[5],
                }

                await cache_set(cache_key, tenant_data, expire=60)
                return tenant_data
        except Exception as e:
            logger.error(f"Tenant resolution error: {e}")
            return None

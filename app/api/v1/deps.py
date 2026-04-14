"""Re-export commonly used dependencies for convenience."""
from app.core.dependencies import (
    get_db,
    get_public_db,
    get_alif24_db,
    get_tenant,
    get_tenant_id,
    get_current_user,
    get_optional_user,
)

__all__ = [
    "get_db",
    "get_public_db",
    "get_alif24_db",
    "get_tenant",
    "get_tenant_id",
    "get_current_user",
    "get_optional_user",
]

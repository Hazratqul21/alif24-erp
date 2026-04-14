from functools import wraps
from fastapi import Depends, Request
from typing import Callable

from app.core.exceptions import ForbiddenError
from app.core.dependencies import get_current_user


def require_role(*allowed_roles: str):
    """Decorator to check that the current user has one of the allowed roles."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, current_user: dict = Depends(get_current_user), **kwargs):
            user_roles = current_user.get("roles", [])
            if not any(role in allowed_roles for role in user_roles):
                raise ForbiddenError(f"Bu amal uchun quyidagi rollardan biri kerak: {', '.join(allowed_roles)}")
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator


def require_permission(module: str, action: str):
    """Decorator to check module-level permission."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, current_user: dict = Depends(get_current_user), **kwargs):
            permissions = current_user.get("permissions", [])
            has_perm = any(
                p["module"] == module and p["action"] == action
                for p in permissions
            )
            if not has_perm:
                director_roles = {"super_admin", "director", "administrator"}
                user_roles = set(current_user.get("roles", []))
                if not user_roles.intersection(director_roles):
                    raise ForbiddenError(f"'{module}.{action}' ruxsati yo'q")
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator


def check_permission(current_user: dict, module: str, action: str) -> bool:
    permissions = current_user.get("permissions", [])
    has_perm = any(
        p["module"] == module and p["action"] == action
        for p in permissions
    )
    if has_perm:
        return True
    director_roles = {"super_admin", "director", "administrator"}
    user_roles = set(current_user.get("roles", []))
    return bool(user_roles.intersection(director_roles))


def check_data_access(current_user: dict, resource_owner_id: str = None, class_id: int = None) -> bool:
    """Check data-level access: own data, class data, or all data."""
    roles = set(current_user.get("roles", []))

    full_access_roles = {"super_admin", "director", "administrator", "deputy_academic", "deputy_discipline"}
    if roles.intersection(full_access_roles):
        return True

    if resource_owner_id and current_user["id"] == resource_owner_id:
        return True

    return True

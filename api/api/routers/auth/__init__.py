# Generado por tai-api: este fichero lo reescribe `tai-api generate`.
"""
agendarte-api - Authentication Module
Generado automáticamente por tai-api auth init
"""
from fastapi import APIRouter
from .dependencies import (
    can,
    require_permission,
    requires_permissions,
    requires_permissions_from_realm,
    requires_authentication,
    websocket_requires_authentication,
    websocket_requires_permissions,
    CurrentUser,
    get_current_user,
)
from .login_router import router as l_router
from .jwt import AccessToken
from .utils import build_owner_rules, build_rls_rules, owner_locked_columns, owner_violation, rls_for
from .rbac_router import router as r_router

auth_router = APIRouter()
auth_router.include_router(l_router)
auth_router.include_router(r_router)

#: La marca del contrato de `/auth` y `/rbac` (`tai_api/contract/auth.py`). `app/` la añade a
#: `X-Tai-Contract` como `auth=<hash>`, y el cliente TypeScript avisa si la suya es otra.
CONTRACT_HASH = "9dd5c1c0d819"

# Los quince primeros son el contrato: iguales con los dos backends (tests/test_paridad_auth.py).
# Los demás son propios del backend, y un código que los use no sobrevive a `tai-api auth switch`.
__all__ = [
    "requires_permissions",
    "requires_permissions_from_realm",
    "requires_authentication",
    "websocket_requires_authentication",
    "websocket_requires_permissions",
    "build_rls_rules",
    "rls_for",
    "can",
    "require_permission",
    "build_owner_rules",
    "owner_locked_columns",
    "owner_violation",
    "auth_router",
    "AccessToken",
    "CONTRACT_HASH",
    "CurrentUser",
    "get_current_user",
]
# Generado por tai-api: este fichero lo reescribe `tai-api generate`.
"""
agendarte-api - Authentication Dependencies
Generado automáticamente por tai-api

Las dependencias de FastAPI que deciden quién pasa: `requires_permissions`,
`requires_permissions_from_realm`, `requires_authentication` y `get_current_user`, y sus dos
equivalentes de WebSocket, `websocket_requires_authentication` y `websocket_requires_permissions`.
Todas validan el token por el mismo camino, `_validar`.
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Annotated, Callable, Literal, Optional

from fastapi import Depends, WebSocket
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer

from .jwt import JWTHandler, AccessToken
from .utils import rbac_activo
from .websocket import autenticar_websocket
from api.database.auth import auth_async_api as auth_api, UserRead
from api.resources import (
    APIException,
    ErrorCode,
    UnAuthorizedException,
    InvalidTokenException,
)

# auto_error=False: sin RBAC no hay token que exigir, y la dependencia tiene que poder
# resolverse igual. Quien lo exige es `_validar`, ya con RBAC activo.
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/docslogin",
    auto_error=False,
    description="Multi-realm: usa el formato username@realm para autenticación",
)

# Como en Keycloak: el token se acepta pegado tal cual (Bearer) o del flujo de login de la
# documentación. Las dos leen la misma cabecera; declararlas es lo que las ofrece `/docs`.
http_bearer = HTTPBearer(auto_error=False)


async def _token_crudo(
    bearer: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
    oauth2_token: Optional[str] = Depends(oauth2_scheme),
) -> Optional[str]:
    return bearer.credentials if bearer else oauth2_token


TokenCrudo = Annotated[Optional[str], Depends(_token_crudo)]


def _sin_token() -> APIException:
    """
    La respuesta a una petición sin token: **401**, no 403.

    Antes era `UnAuthorizedException`, cuyo código es el de «permisos insuficientes» y sale
    como 403. La diferencia no es cosmética: ante un 401 un cliente manda a iniciar sesión;
    ante un 403, enseña que no tiene permiso.
    """
    return APIException(
        "No se ha encontrado token. Prueba con /login",
        error_code=ErrorCode.UNAUTHORIZED_ACCESS,
    )


def _token_de_desarrollo() -> AccessToken:
    """
    El token que se usa con la autorización desactivada (`tai-api dev`). Nunca en producción.

    Antes no llevaba `realm_name`, que es obligatorio, así que construirlo fallaba y con la
    autorización apagada **cualquier endpoint respondía 500**: el modo de desarrollo del
    backend Database no funcionaba.
    """
    return AccessToken(
        # fijo y no el UUID nulo, que un proyecto puede usar como marca (tai-chat: el límite por defecto)
        user_id="d5b9c7fb-1c1e-5312-8b43-f52c4a36e7a0",
        username="anonymous",
        realm_name="main",
        exp=datetime.now(timezone.utc),
        permissions=["sudo"],
    )


async def _validar(token: Optional[str]) -> AccessToken:
    """
    Valida un access token y, con sesión única, que su sesión siga viva.

    Es el único sitio donde se decide si un token vale, y lo usan las cuatro dependencias.
    Sin sesión única el token es autosuficiente: vale hasta que caduca, aunque el usuario
    se desactive o cambie la contraseña entretanto. Activar `session_management` en el
    `.taiapiproject` es lo que permite revocarlo.
    """
    if not token:
        raise _sin_token()

    payload = JWTHandler.decode_token(token, "access")

    return payload


def permisos_del_token(token: AccessToken) -> list[str]:
    """Los permisos de API del token: los que comprueban las dependencias. Como en Keycloak."""
    return sorted(set(token.api_roles))


def _tiene_permiso(token: AccessToken, requerido: str, comodines: tuple[str, ...]) -> bool:
    permisos = set(token.api_roles)
    return "sudo" in permisos or requerido in permisos or any(c in permisos for c in comodines)


def _exigir_permiso(token: AccessToken, action: str, resource: str) -> None:
    requerido = f"{resource}-{action}"
    if not _tiene_permiso(token, requerido, (f"{resource}-admin", f"allresources-{action}")):
        raise UnAuthorizedException(
            "Permisos insuficientes",
            details={"required_permission": requerido},
        )


def can(token: AccessToken, action: Literal["admin", "create", "read", "update", "delete"], resource: str) -> bool:
    """
    Si el token tiene el permiso de `action` sobre `resource`, con la misma regla que
    `requires_permissions`: `<recurso>-<acción>`, o `sudo`, `<recurso>-admin` o `allresources-<acción>`.

    Es para el código propio —un endpoint de `routers/custom/`, o lo que llame desde ahí con el
    token—, que antes tenía que copiar la regla. Con la autorización apagada (`tai-api dev`), `True`,
    como las dependencias. Junto a `rls_for`, da lo mismo que un endpoint generado:

        if can(token, "read", "chat"):
            filas = await chatbot_async_api.chat.find_many(rls=rls_for(token, "chatbot"))
    """
    if not rbac_activo():
        return True
    return _tiene_permiso(token, f"{resource}-{action}", (f"{resource}-admin", f"allresources-{action}"))


def require_permission(token: AccessToken, action: Literal["admin", "create", "read", "update", "delete"], resource: str) -> None:
    """
    Lo mismo que `can`, pero sin el permiso lanza lo que lanzaría el endpoint generado: un 403
    `INSUFFICIENT_PERMISSIONS` con `details.required_permission`.
    """
    if rbac_activo():
        _exigir_permiso(token, action, resource)


def requires_permissions(
    action: Literal["admin", "create", "read", "update", "delete"],
    resource: str,
) -> Callable:
    """Exige el permiso `<recurso>-<acción>`, o `sudo`, `<recurso>-admin` o `allresources-<acción>`."""

    async def permission_dependency(token: TokenCrudo = None) -> AccessToken:
        # El interruptor se consulta aquí, por petición, y no al construir la dependencia:
        # entonces se leía durante el import de los endpoints, antes de que `__main__.py`
        # llegara a activarlo, y la API quedaba abierta sin ningún aviso.
        if not rbac_activo():
            return _token_de_desarrollo()

        payload = await _validar(token)
        _exigir_permiso(payload, action, resource)
        return payload

    return permission_dependency


def requires_permissions_from_realm(
    action: Literal["admin", "create", "read", "update", "delete"],
) -> Callable:
    """
    Exige administrar el realm de la ruta: `<realm>-<acción>` o `<realm>-admin`, del mismo realm.

    `sudo` y `allrealms-<acción>` valen para cualquier realm. Fuera de eso, el realm del
    token tiene que ser el de la ruta, igual que en el backend de Keycloak: un administrador
    de un centro no gestiona los usuarios de otro.
    """

    async def permission_dependency(realm_name: str, token: TokenCrudo = None) -> AccessToken:
        if not rbac_activo():
            return _token_de_desarrollo()

        payload = await _validar(token)
        if _tiene_permiso(payload, "", ("sudo", f"allrealms-{action}")):
            return payload
        if payload.realm_name != realm_name:
            raise UnAuthorizedException(
                "El realm del token no coincide con el realm de la ruta",
                details={"token_realm": payload.realm_name, "path_realm": realm_name},
            )
        requerido = f"{realm_name}-{action}"
        if not _tiene_permiso(payload, requerido, (f"{realm_name}-admin",)):
            raise UnAuthorizedException(
                "Permisos insuficientes",
                details={"required_permission": requerido},
            )
        return payload

    return permission_dependency


def requires_authentication() -> Callable:
    """
    Exige identidad, no un permiso concreto.

    Es para lo que describe la API sin ser un dato de nadie —los enumerados del schema—:
    pedir un permiso por recurso obligaría a inventar uno que ningún rol tiene hoy y
    dejaría todos esos endpoints en 403, y no pedir nada los dejaba accesibles sin token,
    que es como estaban. Respeta el mismo interruptor que `requires_permissions`: con la
    autorización desactivada no exige nada.
    """

    async def authentication_dependency(token: TokenCrudo = None) -> AccessToken:
        if not rbac_activo():
            return _token_de_desarrollo()
        return await _validar(token)

    return authentication_dependency


# ============================================================================
# WEBSOCKET
# ============================================================================

def websocket_requires_authentication(subprotocol: Optional[str] = None) -> Callable:
    """
    Exige identidad en una ruta `@router.websocket`; es `requires_authentication` para WebSocket.

    La conexión **llega aceptada** al endpoint, que no tiene que llamar a `accept()` (si lo hace,
    no pasa nada). El token se valida igual que en HTTP —firma, caducidad, usuario activo y
    sesión vigente— y viaja en el subprotocolo `tai.bearer` o en `Authorization: Bearer`, nunca
    en la URL. Si no vale, la conexión se cierra con 4401, o con 4419 si ha caducado. Ver
    `websocket.py`.

    Args:
        subprotocol: Un subprotocolo propio que aceptar en vez de `tai.bearer`, si el cliente lo
            ofrece junto al token.
    """

    async def websocket_authentication_dependency(websocket: WebSocket) -> AccessToken:
        async def validar(token: Optional[str]) -> AccessToken:
            if not rbac_activo():
                return _token_de_desarrollo()
            return await _validar(token)

        return await autenticar_websocket(websocket, validar, subprotocol)

    return websocket_authentication_dependency


def websocket_requires_permissions(
    action: Literal["admin", "create", "read", "update", "delete"],
    resource: str,
    subprotocol: Optional[str] = None,
) -> Callable:
    """
    Exige el permiso `<recurso>-<acción>` en una ruta `@router.websocket`.

    Es `requires_permissions` para WebSocket, con los mismos comodines (`sudo`,
    `<recurso>-admin`, `allresources-<acción>`). Sin el permiso, la conexión se cierra con 4403.
    """

    async def websocket_permission_dependency(websocket: WebSocket) -> AccessToken:
        async def validar(token: Optional[str]) -> AccessToken:
            if not rbac_activo():
                return _token_de_desarrollo()
            payload = await _validar(token)
            _exigir_permiso(payload, action, resource)
            return payload

        return await autenticar_websocket(websocket, validar, subprotocol)

    return websocket_permission_dependency


async def get_current_user(token: TokenCrudo = None) -> UserRead:
    """
    El usuario del token, leído de la base de datos con sus roles.

    Valida el token como las demás dependencias y después lee la fila; con sesión única
    esa lectura sustituye a la que haría `_validar`, así que no se consulta dos veces.
    """
    if not token:
        raise _sin_token()

    payload = JWTHandler.decode_token(token, "access")
    usuario = await auth_api.user.find(payload.user_id, includes=["user_roles.role", "realm"])
    if usuario is None or not usuario.is_active:
        raise InvalidTokenException("El usuario no existe o está desactivado")

    return usuario


CurrentUser = Annotated[UserRead, Depends(get_current_user)]
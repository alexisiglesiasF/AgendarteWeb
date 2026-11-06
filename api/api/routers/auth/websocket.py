# Generado por tai-api: este fichero lo reescribe `tai-api generate`.
"""
agendarte-api - Autenticación de WebSocket
Generado automáticamente por tai-api

El transporte de las dependencias `websocket_requires_authentication` y
`websocket_requires_permissions` (en `dependencies.py`): de dónde sale el token en un handshake,
qué origen se acepta y cómo se rechaza una conexión para que el navegador lo entienda. Validar el
token es de cada backend; aquí solo se le pasa en crudo.

Por qué las dependencias HTTP no sirven: `HTTPBearer` y `OAuth2PasswordBearer` leen el token del
`Request`, y en una ruta `@router.websocket` no hay `Request`: la dependencia falla antes de
llegar al endpoint. Y CORS no cubre WebSocket, así que el origen lo comprueba esto.

El token llega por una de dos vías, nunca por la URL (una URL acaba en los logs de acceso de
uvicorn y de cualquier proxy):

- **El subprotocolo** `Sec-WebSocket-Protocol: tai.bearer, <access token>`: lo único que un
  navegador puede poner en un handshake, porque `new WebSocket()` no admite cabeceras. El servidor
  responde `tai.bearer`, nunca el token.
- **`Authorization: Bearer <access token>`**: para un cliente que no es un navegador.

Una conexión rechazada **se acepta y se cierra** con un código de aplicación. Si se cerrara antes
de aceptarla, el navegador solo vería un 1006 —sin código ni motivo— y no podría distinguir un
token caducado de una caída de red:

| Código | Motivo | Qué hace el cliente |
|---|---|---|
| 4401 | Sin token, token inválido o sesión cerrada | Iniciar sesión otra vez |
| 4419 | Token caducado (`TOKEN_EXPIRED`) | Pedir un token vigente y reconectar |
| 4403 | Sin permiso, u origen no permitido | Nada: reconectar no lo arregla |
| 1013 | El proveedor de identidad no responde (`SERVICE_UNAVAILABLE`) | Reintentar más tarde |
"""
from __future__ import annotations
import os
from typing import Awaitable, Callable, List, Optional, Tuple, TypeVar
from urllib.parse import urlsplit

from fastapi import WebSocket, WebSocketException
from starlette.websockets import WebSocketState

from api.resources import APIException

#: El subprotocolo que lleva el token detrás: `["tai.bearer", token]` en `new WebSocket(url, …)`.
SUBPROTOCOLO = "tai.bearer"

CIERRE_SIN_AUTENTICAR = 4401
CIERRE_TOKEN_CADUCADO = 4419
CIERRE_PROHIBIDO = 4403

#: 1013 es el «vuelve a intentarlo» del protocolo: el proveedor de identidad no responde.
CIERRE_REINTENTAR = 1013

#: Por el **valor** del `ErrorCode`, no por el miembro: `resources/` se copia una vez en `init`,
#: y un proyecto con una revisión anterior no tiene por qué tener todos los de hoy.
_CIERRE_POR_CODIGO = {
    "TOKEN_EXPIRED": CIERRE_TOKEN_CADUCADO,
    "UNAUTHORIZED_ACCESS": CIERRE_SIN_AUTENTICAR,
    "INVALID_TOKEN": CIERRE_SIN_AUTENTICAR,
    "SESSION_INVALIDATED": CIERRE_SIN_AUTENTICAR,
    "INSUFFICIENT_PERMISSIONS": CIERRE_PROHIBIDO,
    "SERVICE_UNAVAILABLE": CIERRE_REINTENTAR,
}

T = TypeVar("T")


def token_del_handshake(websocket: WebSocket) -> Tuple[Optional[str], List[str]]:
    """
    El token del handshake y los subprotocolos propios de la aplicación que ofrece el cliente.

    La pareja `tai.bearer, <token>` se saca de la lista: lo que queda es lo que la aplicación
    puede negociar.
    """
    ofrecidos = list(websocket.scope.get("subprotocols") or [])
    token = None
    if SUBPROTOCOLO in ofrecidos:
        i = ofrecidos.index(SUBPROTOCOLO)
        token = ofrecidos[i + 1] if i + 1 < len(ofrecidos) else None
        del ofrecidos[i:i + 2]
    if token is None:
        cabecera = websocket.headers.get("authorization", "")
        if cabecera[:7].lower() == "bearer ":
            token = cabecera[7:].strip() or None
    return token, ofrecidos


def _origen(url: str) -> str:
    partes = urlsplit(url)
    return f"{partes.scheme}://{partes.netloc}".lower()


def _mismo_origen(websocket: WebSocket) -> set:
    """
    El origen con el que el navegador ve esta API, que es el que trae un frontend del mismo sitio.

    Detrás del proxy `/api` del frontend, la API recibe `Host` del proxy (`changeOrigin`) y el
    original en `X-Forwarded-Host`/`X-Forwarded-Proto`; `PUBLIC_URL`, si está, también vale.
    `taiApiProxy()` pone `X-Forwarded-Host` también en el upgrade, que http-proxy no pone solo.
    Un navegador no puede poner esas cabeceras en un WebSocket, así que confiar en ellas no
    abre nada: solo reconoce lo que ya era el mismo sitio.
    """
    cabeceras = websocket.headers
    esquema = "https" if websocket.url.scheme == "wss" else "http"
    propios = set()
    host = cabeceras.get("host")
    if host:
        propios.add(f"{esquema}://{host}".lower())
    reenviado = (cabeceras.get("x-forwarded-host") or "").split(",")[0].strip()
    if reenviado:
        protocolo = (cabeceras.get("x-forwarded-proto") or esquema).split(",")[0].strip().lower()
        # En el upgrade de un WebSocket, el proxy de Vite (http-proxy) manda `ws`/`wss`, y el
        # `Origin` del navegador es `http`/`https`.
        protocolo = {"ws": "http", "wss": "https"}.get(protocolo, protocolo)
        propios.add(f"{protocolo}://{reenviado}".lower())
    publica = os.environ.get("PUBLIC_URL")
    if publica:
        propios.add(_origen(publica))
    return propios


def origen_permitido(websocket: WebSocket) -> bool:
    """
    `Origin` contra `ALLOWED_ORIGINS`, que es la misma lista que gobierna CORS.

    - Sin `Origin` no es un navegador, y la comprobación no le aplica.
    - `"*"` acepta cualquier origen, como en CORS.
    - Una lista acepta sus orígenes **y el mismo origen**: con la sesión en cookie y el proxy
      `/api`, `ALLOWED_ORIGINS` está vacía y el frontend es el mismo sitio.
    """
    origen = websocket.headers.get("origin")
    if not origen:
        return True
    # Al validar, no al importar: `config.py` es del proyecto y puede importar sus routers.
    from api.config import ALLOWED_ORIGINS

    if "*" in ALLOWED_ORIGINS:
        return True
    origen = origen.lower()
    return origen in {_origen(o) for o in ALLOWED_ORIGINS} or origen in _mismo_origen(websocket)


async def _aceptar(websocket: WebSocket, subprotocolo: Optional[str]) -> None:
    """
    Acepta la conexión, y deja `websocket.accept()` sin efecto para el resto del endpoint.

    El endpoint recibe la conexión ya aceptada. El código que ya llamaba a `accept()` —un gestor
    de conexiones, por ejemplo— no tiene que cambiar: aceptar dos veces es un error de Starlette,
    y aquí la segunda llamada no hace nada.
    """
    if websocket.client_state == WebSocketState.CONNECTING:
        await websocket.accept(subprotocol=subprotocolo)

    async def ya_aceptada(subprotocol: Optional[str] = None, headers=None) -> None:
        return None

    websocket.accept = ya_aceptada  # type: ignore[method-assign]


async def autenticar_websocket(
    websocket: WebSocket,
    validar: Callable[[Optional[str]], Awaitable[T]],
    subprotocolo: Optional[str] = None,
) -> T:
    """
    Acepta la conexión y devuelve lo que diga `validar` del token; si no vale, la cierra.

    Args:
        websocket: La conexión, aún sin aceptar.
        validar: La validación del backend: recibe el token en crudo (o `None`) y devuelve el
            `AccessToken`, o lanza la `APIException` que daría la misma petición por HTTP.
        subprotocolo: Un subprotocolo propio de la aplicación que aceptar en lugar de
            `tai.bearer`, si el cliente lo ofrece.
    """
    token, propios = token_del_handshake(websocket)
    if subprotocolo and subprotocolo in propios:
        elegido = subprotocolo
    elif SUBPROTOCOLO in (websocket.scope.get("subprotocols") or []):
        elegido = SUBPROTOCOLO
    else:
        elegido = None
    await _aceptar(websocket, elegido)

    if not origen_permitido(websocket):
        raise WebSocketException(code=CIERRE_PROHIBIDO, reason="ORIGIN_NOT_ALLOWED")
    try:
        return await validar(token)
    except APIException as exc:
        codigo = getattr(exc.error_code, "value", str(exc.error_code))
        cierre = _CIERRE_POR_CODIGO.get(codigo)
        if cierre is None:
            raise
        raise WebSocketException(code=cierre, reason=codigo) from None
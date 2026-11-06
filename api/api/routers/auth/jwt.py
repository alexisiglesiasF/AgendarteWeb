# Generado por tai-api: este fichero lo reescribe `tai-api generate`.
"""
agendarte-api - JWT Token Handler
Generado automáticamente por tai-api

Emisión y validación de los tokens del modo Database. Un access token lleva los permisos de
**API** del usuario —los que comprueba `requires_permissions`— y sus reglas de RLS; los de
aplicación (los que usa el front para decidir qué enseña) viajan en la respuesta del login y
de `/auth/me`, no en el token.
"""
from __future__ import annotations
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Literal, Optional

from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
from pydantic import BaseModel

from api.resources import InvalidTokenException, TokenExpiredException

JWT_SECRET_KEY = os.getenv("SECRET_KEY")
if not JWT_SECRET_KEY:
    raise ValueError(
        "La clave secreta JWT no está configurada. "
        "Establezca la variable de entorno SECRET_KEY."
    )
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION = 2444666668888888


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AccessToken(BaseModel):
    user_id: str
    username: str
    realm_name: str
    exp: datetime
    session_id: Optional[str] = None
    #: Permisos de API: los que se comprueban en cada endpoint.
    permissions: List[str] = []
    rls: Optional[Dict[str, Dict[str, Dict[str, List[str]]]]] = None

    @property
    def sub(self) -> str:
        return self.user_id

    @property
    def preferred_username(self) -> str:
        return self.username

    @property
    def api_roles(self) -> List[str]:
        return self.permissions


def rls_desde_atributos(attributes: Optional[dict]) -> Dict[str, Dict[str, Dict[str, List[str]]]]:
    """
    Las reglas de RLS de un usuario, a partir de sus atributos `rls.<schema>.<tabla>.<columna>`.

    Es la misma forma que tienen en Keycloak, así que un endpoint no sabe de qué backend
    salió su token.

    Un atributo a `null` es «no aplica», como si no estuviera: no entra en el token. Antes llegaba
    como el texto `"None"`, que no casaba con nada (o daba un 500 sobre una columna numérica). Una
    lista vacía sí entra: es «cero valores», y el endpoint no devuelve ninguna fila.
    """
    reglas: Dict[str, Dict[str, Dict[str, List[str]]]] = {}
    for clave, valor in (attributes or {}).items():
        partes = clave.split(".")
        if len(partes) != 4 or partes[0] != "rls" or valor is None:
            continue
        _, schema, tabla, columna = partes
        valores = valor if isinstance(valor, list) else [valor]
        reglas.setdefault(schema, {}).setdefault(tabla, {})[columna] = [str(v) for v in valores]
    return reglas


class JWTHandler:

    @staticmethod
    def create_tokens(
        user_id: str,
        username: str,
        realm_name: str,
        session_id: Optional[str] = None,
        permissions: Optional[List[str]] = None,
        attributes: Optional[dict] = None,
    ) -> TokenResponse:
        ahora = datetime.now(timezone.utc)

        access_payload = {
            "user_id": user_id,
            "username": username,
            "realm_name": realm_name,
            "typ": "access",
            "iat": ahora,
            "exp": ahora + timedelta(minutes=JWT_EXPIRATION),
            "session_id": session_id,
            "permissions": permissions or [],
            "rls": rls_desde_atributos(attributes),
        }
        refresh_payload = {
            "user_id": user_id,
            "username": username,
            "realm_name": realm_name,
            "typ": "refresh",
            "iat": ahora,
            "exp": ahora + timedelta(minutes=JWT_EXPIRATION * 4),
            "session_id": session_id,
        }

        return TokenResponse(
            access_token=jwt.encode(access_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM),
            refresh_token=jwt.encode(refresh_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM),
        )

    @staticmethod
    def decode_token(
        token: str,
        grant_type: Literal["access", "refresh"],
        verify_exp: bool = True,
    ) -> AccessToken:
        """
        Valida la firma, la caducidad y el tipo de un token, y devuelve su contenido.

        El tipo se exige siempre. Antes solo se comprobaba si el claim estaba, así que un
        token firmado sin `typ` valía igual como access que como refresh.
        """
        try:
            payload = jwt.decode(
                token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM], options={"verify_exp": verify_exp}
            )
        except ExpiredSignatureError:
            raise TokenExpiredException("El token ha expirado")
        except JWTError:
            raise InvalidTokenException("Token inválido")

        if payload.get("typ") != grant_type:
            raise InvalidTokenException(
                f"Tipo de token inválido: se esperaba '{grant_type}'"
            )

        if isinstance(payload.get("exp"), (int, float)):
            payload["exp"] = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)

        try:
            return AccessToken(**payload)
        except (TypeError, ValueError) as e:
            # Un token con nuestra firma y una forma que no reconocemos: de una versión
            # anterior del proyecto, o manipulado antes de firmarse. No es un 500.
            raise InvalidTokenException(f"Token con un contenido no válido: {e}")

    @staticmethod
    def generate_session_id() -> str:
        return str(uuid.uuid4())
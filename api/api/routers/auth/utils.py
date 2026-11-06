# Generado por tai-api: este fichero lo reescribe `tai-api generate`.
"""
agendarte-api - Utils
Generado automáticamente por tai-api set-auth

Este módulo contiene utilidades para la integración con database.
"""
from __future__ import annotations
import importlib
import os
from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Callable, Dict, List, Optional, Type

from tai_alphi import Alphi

from datetime import datetime

from api.resources import APIException, ErrorCode, ValidationException
from .rbac_models import rls_valores


logger = Alphi.get_logger_by_name("tai-api")


class LoginRequest(BaseModel):
    """Modelo para la solicitud de login"""
    username: str
    password: str


class RefreshRequest(BaseModel):
    """Modelo para solicitud de refresh token"""
    refresh_token: str


class LoginData(BaseModel):
    """
    La respuesta de un login o de un refresco.

    `refresh_token` falta cuando la sesión va en cookie (`auth.session.transport: "cookie"`):
    entonces viaja en una cookie httpOnly que el JavaScript no puede leer, que es el objetivo.
    `expires_in` son los segundos que vale el access token, contados desde que llega la
    respuesta: un cliente que calculara la caducidad con el `exp` del JWT y su propio reloj
    refrescaría sin parar, o nunca, en un equipo con la hora mal. `session_expires_at` es el
    límite absoluto de la sesión, que ningún refresco alarga.
    """
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    session_expires_at: Optional[datetime] = None
    user: UserData


class LogoutData(BaseModel):
    """Modelo para la respuesta de logout"""
    message: str = "Sesión cerrada"


class UserRoleData(BaseModel):
    """Modelo para la información del rol en la solicitud de asignación o eliminación del rol del usuario"""
    role_name: str


class UserData(BaseModel):
    """Modelo para la información del usuario en la respuesta de login y refresh"""
    sub: Optional[str] = None
    preferred_username: str
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    email_verified: Optional[bool] = None
    permissions: Optional[List[str]] = None


class MeUpdate(BaseModel):
    """Campos que un usuario puede modificar de su propio perfil.

    Deliberadamente NO hereda ni reutiliza RBACUserUpdate: aquel incluye `is_active`,
    `roles` y los atributos de RLS, que solo puede tocar un administrador del realm.
    `extra="forbid"` rechaza además cualquier intento de colar `username` o
    `realm_name` en el cuerpo; la identidad se toma siempre del token.

    La contraseña no está: se cambia por `POST /auth/me/password` (`PasswordChange`), que
    pide la actual. Antes había dos formas, con efectos opuestos sobre la sesión.
    """
    model_config = ConfigDict(extra="forbid")

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None


#: La longitud mínima de la contraseña nueva en `POST /auth/me/password`.
PASSWORD_MIN_LENGTH = 8


class PasswordChange(BaseModel):
    """El cambio de contraseña del propio usuario: la actual, que se comprueba, y la nueva.

    `extra="forbid"`: el usuario sale del token, y un `username` en el cuerpo es un error.
    """
    model_config = ConfigDict(extra="forbid")

    current_password: str = Field(description="La contraseña actual, que se comprueba antes de cambiarla.")
    new_password: str = Field(description=f"La contraseña nueva (mínimo {PASSWORD_MIN_LENGTH} caracteres).")

    def comprobar(self) -> None:
        """Lo que se puede decidir sin el backend. Los errores son 422 con su `field`."""
        if len(self.new_password) < PASSWORD_MIN_LENGTH:
            raise ValidationException(
                f"La contraseña nueva debe tener al menos {PASSWORD_MIN_LENGTH} caracteres", field="new_password",
            )
        if self.new_password == self.current_password:
            raise ValidationException("La contraseña nueva debe ser distinta de la actual", field="new_password")


class UserInfoData(BaseModel):
    """Modelo para la información del usuario"""
    id: str
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    is_active: bool = True
    roles: Optional[List[str]] = None
    permissions: Optional[List[str]] = None
    #: Cuándo caduca la contraseña. Con Keycloak va vacío: la caducidad la aplica su política de
    #: contraseñas, no la API. Está en los dos para que la respuesta tenga la misma forma.
    password_expiration: Optional[datetime] = None



def rbac_activo() -> bool:
    """
    Si la autorización está activa. Se consulta **en cada petición**, no al importar.

    Antes se leía al construir la dependencia, es decir durante el import del módulo del
    endpoint, y la línea que la activa en `__main__.py` va después de importar los
    routers: cuando se ejecutaba, las dependencias ya estaban construidas y la API
    quedaba abierta con permisos de superusuario. Lo que salvaba a los despliegues era
    que el dockerfile define la variable en el entorno; arrancar de cualquier otra forma
    —un compose propio, un uvicorn a mano, un test— la dejaba abierta sin un solo aviso.

    Leerlo aquí hace que el orden de los imports deje de importar.
    """
    return os.getenv("RBAC_ENABLED", "false").lower() == "true"


def build_rls_rules(
    token: Any,
    schema_name: str,
    resolve_model: Callable[[str], Optional[Type[Any]]],
    rls_cls: Type[Any],
) -> List[Any]:
    """
    Traduce las reglas de RLS que trae el token a las reglas que entiende el DAO.

    Esto vivía repetido dentro de cada endpoint como una comprensión de lista que
    terminaba en `if get_model_by_name(...) is not None`. Ese `is not None` tapaba dos
    casos muy distintos:

    - **La regla es de otro schema.** Es lo normal: un token describe el ámbito del
      usuario en toda la aplicación, y un endpoint de `ventas` recibe también las reglas
      de `almacen`. Cada router resuelve contra el registro de su propio schema, así que
      las ajenas no resuelven y no tienen por qué: no aplican aquí. Se omiten en silencio
      porque no hay nada que decir.

    - **La regla es de este schema y aun así no resuelve.** Entonces iba dirigida a
      nosotros y no se ha podido aplicar —una tabla renombrada, un token emitido contra
      un schema anterior—, y lo que ocurría es que la consulta salía **sin ese filtro**:
      devolvía filas que el usuario no debía ver, sin error y sin rastro. Un filtro de
      seguridad falla en cerrado, y si ni siquiera se puede construir, falla en voz alta.

    `resolve_model` y `rls_cls` entran por parámetro porque son del cliente de cada
    schema —hay un registro y una clase `RLS` por schema— y este módulo es común a todos.

    Args:
        token: el token validado, con su diccionario `rls` {schema: {tabla: {columna: valores}}}.
        schema_name: el schema del router que llama, para saber qué reglas iban dirigidas a él.
        resolve_model: `get_model_by_name` del schema que llama.
        rls_cls: la clase `RLS` del schema que llama.

    Raises:
        APIException: si una regla de este schema no se puede resolver.
    """
    reglas: List[Any] = []

    for esquema, tablas in (getattr(token, "rls", None) or {}).items():
        for tabla, columnas in (tablas or {}).items():
            modelo = resolve_model(f"{esquema}.{tabla}")

            if modelo is None:
                if esquema != schema_name:
                    continue
                logger.error(
                    f"[{schema_name}] El token trae una regla RLS sobre "
                    f"{esquema}.{tabla}, que no existe en este schema — denegando"
                )
                raise APIException(
                    message="No se puede aplicar el filtrado por fila",
                    error_code=ErrorCode.INTERNAL_SERVER_ERROR,
                    details={
                        "rule": f"{esquema}.{tabla}",
                        "reason": "la tabla de la regla no existe en el schema",
                    },
                )

            for columna, condiciones in (columnas or {}).items():
                # `None`: la regla no aplica a este usuario. `[]` (o el `RLS_SIN_VALORES` con que
                # Keycloak guarda «cero valores»): aplica y el DAO no devuelve ninguna fila.
                valores = rls_valores(condiciones)
                if valores is None:
                    continue
                reglas.append(
                    rls_cls(
                        target_model=modelo,
                        target_column=columna,
                        values=valores,
                    )
                )

    # Las de propietario van con las demás: así las aplica todo lo que ya pasa `rls` al DAO
    # —las lecturas, las escrituras sobre filas existentes y los routers propios—.
    reglas.extend(build_owner_rules(token, schema_name, resolve_model, rls_cls))
    return reglas


#: El paquete de los clientes de datos (`<paquete>.database`): `rls_for` importa de ahí el del
#: schema que se le pide.
DATABASE_IMPORT_ROOT = "api.database"


def rls_for(token: Any, schema_name: str) -> List[Any]:
    """
    Las reglas que hay que pasar al DAO de `schema_name` para que filtre como la API generada.

    Es la forma de que el código propio —un endpoint de `routers/custom/`, o lo que llame desde
    ahí: una herramienta que lee en nombre del usuario— consulte con el mismo RLS que el CRUD,
    **con solo el token**:

        rls = rls_for(token, "chatbot")
        chat = await chatbot_async_api.chat.find(id=chat_id, rls=rls)

    Son las mismas reglas que construye cada endpoint generado: las del token y las de
    propietario (`owner()`). `build_rls_rules` pide además el registro y la clase `RLS` del
    cliente, piezas internas que el código propio no tendría por qué conocer; aquí se resuelven
    importando el cliente del schema al llamar, así que no importa el orden en que se generaron.

    Falla en cerrado, como `build_rls_rules`: un schema sin cliente generado o una regla del
    token que no resuelve lanzan `APIException` (500). Nunca devuelve menos reglas de las que tocan.
    """
    módulo = f"{DATABASE_IMPORT_ROOT}.{schema_name}"
    try:
        if not schema_name.isidentifier():
            raise ModuleNotFoundError(name=módulo)
        cliente = importlib.import_module(módulo)
        compartido = importlib.import_module(f"{módulo}._shared")
    except ModuleNotFoundError as error:
        if error.name not in (módulo, f"{módulo}._shared"):
            raise
        logger.error(f"[{schema_name}] rls_for: no hay cliente generado para el schema — denegando")
        raise APIException(
            message="No se puede aplicar el filtrado por fila",
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            details={"schema": schema_name, "reason": "el schema no tiene cliente generado"},
        ) from None
    return build_rls_rules(token, schema_name, compartido.get_model_by_name, cliente.RLS)


# ============================================================================
# PROPIETARIO: owner() de rbac/<realm>.py
# ============================================================================

#: Las reglas `owner()` de los `rbac/<realm>.py`: las filas de cada tabla son del usuario que dice
#: su columna. Son del servicio, no del realm: se aplican a los tokens de todos.
OWNER_RULES: List[Dict[str, Any]] = [
]


def _permisos(token: Any) -> set:
    # Al llamar, no al importar: `dependencies.py` importa este módulo.
    from .dependencies import permisos_del_token

    return set(permisos_del_token(token))


def build_owner_rules(
    token: Any,
    schema_name: str,
    resolve_model: Callable[[str], Optional[Type[Any]]],
    rls_cls: Type[Any],
    model: Optional[Type[Any]] = None,
) -> List[Any]:
    """
    Las reglas de propietario que se aplican a este token en este schema, como reglas del DAO.

    El valor es el usuario del token —su nombre (`preferred_username`) o, con `compare_to="user_id"`, su
    identidad (`sub`)—, así que no hay usuario sin acotar:
    sin usuario no hay token válido, y un token sin él se rechaza. Con la autorización apagada
    (`tai-api dev`) no se aplican, como el resto de la autorización. Un permiso de `exempt` las
    salta.

    `build_rls_rules` ya las incluye. Esta función sirve para lo que solo atañe a ellas: comprobar
    tras una escritura que la fila sigue siendo del usuario. Con `model`, solo devuelve las que
    alcanzan a ese modelo —por su columna o por sus relaciones many-to-one—.
    """
    if not OWNER_RULES or not rbac_activo():
        return []

    reglas: List[Any] = []
    permisos: Optional[set] = None
    for regla in OWNER_RULES:
        if regla["schema"] != schema_name:
            continue
        if regla["exempt"]:
            permisos = _permisos(token) if permisos is None else permisos
            if permisos & set(regla["exempt"]):
                continue
        modelo = resolve_model(f"{regla['schema']}.{regla['table']}")
        if modelo is None:
            logger.error(f"[{schema_name}] La regla owner() de {regla['schema']}.{regla['table']} no resuelve — denegando")
            raise APIException(
                message="No se puede aplicar el filtrado por propietario",
                error_code=ErrorCode.INTERNAL_SERVER_ERROR,
                details={"rule": f"{regla['schema']}.{regla['table']}", "reason": "la tabla de la regla no existe en el schema"},
            )
        usuario = getattr(token, "sub" if regla.get("compare_to") == "user_id" else "preferred_username", None)
        if not usuario:
            raise APIException(
                message="El token no dice quién es el usuario",
                error_code=ErrorCode.INVALID_TOKEN,
            )
        rls = rls_cls(target_model=modelo, target_column=regla["field"], values=[usuario])
        if model is None or rls.applies_to(model):
            reglas.append(rls)
    return reglas


def owner_locked_columns(rules: List[Any], model: Type[Any]) -> set:
    """
    Las columnas de `model` que un `update_many` no puede tocar mientras le alcance una regla de
    propietario: la del propio dueño y, si la regla llega por relaciones, sus claves foráneas
    —cambiar una saca la fila del ámbito del usuario—. El PATCH por clave primaria sí las deja
    cambiar, porque comprueba la fila después.
    """
    columnas: set = set()
    for regla in rules:
        if regla.target_model is model:
            columnas.add(regla.target_column)
        elif regla.applies_to(model):
            columnas |= {c.key for c in model.__table__.columns if c.foreign_keys}
    return columnas


def owner_violation() -> APIException:
    """Una escritura que deja la fila fuera de lo del usuario: 403, y la transacción se deshace."""
    return APIException(
        message="Solo puedes escribir filas tuyas",
        error_code=ErrorCode.INSUFFICIENT_PERMISSIONS,
        details={"reason": "OWNER"},
    )
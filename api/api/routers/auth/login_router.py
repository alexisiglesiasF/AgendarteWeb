# Generado por tai-api: este fichero lo reescribe `tai-api generate`.
"""
agendarte-api - Login Router
Generado automáticamente por tai-api

Endpoints de autenticación del modo Database: login, refresco, cierre de sesión y el perfil
del usuario autenticado. Se apoyan en el cliente del schema `auth` que genera tai-sql, por
su fachada, y cada operación va en **una sola transacción** con su gestor de sesiones.
"""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from typing import Set

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from .jwt import JWTHandler
from .dependencies import CurrentUser
from api.database.auth import auth_async_api as auth_api, UserRead, UserUpdateValues
from api.resources import (
    APIResponse,
    InvalidCredentialsException,
    ValidationException,
)
from .utils import (
    LoginRequest,
    LoginData,
    LogoutData,
    MeUpdate,
    PasswordChange,
    RefreshRequest,
    UserData,
    UserInfoData,
)

router = APIRouter(prefix="/auth", tags=["Autenticación"])

#: Lo que se responde ante cualquier fallo de credenciales, sin distinguir la causa: decir
#: «no existe» y «no coincide» por separado es lo que permite averiguar qué usuarios hay.
CREDENCIALES_INVALIDAS = "Username/password inválidos"


# ============================================================================
# PERMISOS
# ============================================================================

@dataclass
class Permisos:
    """Los permisos efectivos de un usuario, separados por tipo."""
    #: De API: los que comprueba `requires_permissions`. Son los que viajan en el token.
    api: Set[str] = field(default_factory=set)
    #: De aplicación: los que usa el front para decidir qué enseña.
    app: Set[str] = field(default_factory=set)

    @property
    def todos(self) -> list[str]:
        """Los de los dos tipos, que es lo que ve el cliente en el login y en `/auth/me`."""
        return sorted(self.api | self.app)


async def _permisos(usuario: UserRead, session) -> Permisos:
    """
    Los permisos de un usuario: los de sus roles y los de los ancestros de cada rol.

    Se cargan en una consulta todos los roles **del realm del usuario** con sus permisos, y
    la cadena de padres se recorre aquí, por id. Solo cuentan los roles de su realm: una
    asignación a un rol de otro realm (que la clave ya no impide) no da nada.
    """
    roles = await auth_api.role.find_many(
        realm_id=usuario.realm_id,
        includes=["role_permissions.permission"],
        session=session,
    )
    por_id = {rol.id: rol for rol in roles}

    permisos = Permisos()
    visitados: Set[int] = set()
    pendientes = [ur.role_id for ur in (usuario.user_roles or [])]
    while pendientes:
        rol_id = pendientes.pop()
        rol = por_id.get(rol_id)
        # `visitados` corta los ciclos: una jerarquía mal declarada no cuelga el login.
        if rol is None or rol_id in visitados:
            continue
        visitados.add(rol_id)
        for rp in rol.role_permissions or []:
            if rp.permission is None:
                continue
            tipo = getattr(rp.permission.type, "value", rp.permission.type)
            (permisos.app if tipo == "app" else permisos.api).add(rp.permission.name)
        if rol.parent_id is not None:
            pendientes.append(rol.parent_id)
    return permisos


# ============================================================================
# AUTENTICACIÓN
# ============================================================================

async def _autenticar(username: str, password: str, realm_name: str, session) -> UserRead:
    """
    Comprueba credenciales y devuelve el usuario con sus roles.

    La contraseña se verifica **siempre**, exista el usuario o no: `verify_password` tarda lo
    mismo sin fila (compara contra un hash de relleno), y sin usuario se le pregunta por un id
    que no es de nadie. Así el tiempo de respuesta no delata qué usuarios hay; cortar en cuanto
    no se encontraba volvía a abrir esa puerta.
    """
    realm = await auth_api.realm.find_by(name=realm_name, session=session)
    usuario = None if realm is None else await auth_api.user.find_by(
        username=username, realm_id=realm.id, includes=["user_roles.role", "realm"], session=session,
    )
    if not await auth_api.user.verify_password(
        usuario.id if usuario is not None else uuid.uuid4(), value=password, session=session,
    ) or usuario is None:
        raise InvalidCredentialsException(CREDENCIALES_INVALIDAS)
    _comprobar_vigencia(usuario)
    return usuario


def _comprobar_vigencia(usuario: UserRead) -> None:
    """Un usuario desactivado no obtiene tokens, ni al entrar ni al refrescar."""
    if not usuario.is_active:
        raise InvalidCredentialsException("Usuario deshabilitado")


async def _emitir(usuario: UserRead, permisos: Permisos, session, nueva_sesion: bool) -> LoginData:
    """
    Los tokens y los datos de usuario de una respuesta de login o de refresco.

    Estaba escrito tres veces —login, login de Swagger y refresco— con diferencias sutiles
    entre ellas.
    """
    session_id = None

    tokens = JWTHandler.create_tokens(
        user_id=str(usuario.id),
        username=usuario.username,
        realm_name=usuario.realm.name,
        session_id=session_id,
        permissions=sorted(permisos.api),
        attributes=usuario.attributes,
    )
    return LoginData(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type="bearer",
        user=_datos_de_usuario(usuario, permisos),
    )


async def _login(username: str, password: str, realm_name: str) -> LoginData:
    """Todo el login en una transacción: verificar, leer, calcular permisos y abrir sesión."""
    async with auth_api.session_manager.get_session() as session:
        usuario = await _autenticar(username, password, realm_name, session)
        permisos = await _permisos(usuario, session)
        return await _emitir(usuario, permisos, session, nueva_sesion=True)


def _datos_de_usuario(usuario: UserRead, permisos: Permisos) -> UserData:
    return UserData(
        sub=str(usuario.id),
        preferred_username=usuario.username,
        given_name=usuario.first_name,
        family_name=usuario.last_name,
        name=usuario.full_name,
        email=usuario.email,
        email_verified=True,
        permissions=permisos.todos,
    )


def _info(usuario: UserRead, permisos: Permisos) -> UserInfoData:
    return UserInfoData(
        id=str(usuario.id),
        username=usuario.username,
        first_name=usuario.first_name,
        last_name=usuario.last_name,
        full_name=usuario.full_name,
        email=usuario.email,
        is_active=usuario.is_active,
        roles=sorted(ur.role.name for ur in (usuario.user_roles or []) if ur.role is not None),
        permissions=permisos.todos,
    )


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/{realm_name}/login", response_model=APIResponse[LoginData])
async def login(realm_name: str, login_request: LoginRequest):
    datos = await _login(login_request.username, login_request.password, realm_name)
    return APIResponse.success(data=datos, message="Autenticación exitosa")


@router.post("/docslogin", include_in_schema=False, response_model=LoginData)
async def docs_login(form_data: OAuth2PasswordRequestForm = Depends()):
    """El login del botón «Authorize» de Swagger, que no admite un campo de realm: `usuario@realm`."""
    raw = (form_data.username or "").strip()
    username, _, realm_name = raw.rpartition("@") if "@" in raw else (raw, "", "main")
    return await _login(username, form_data.password, realm_name or "main")


@router.post("/logout", response_model=APIResponse[LogoutData])
async def logout(logout_request: RefreshRequest):
    # verify_exp=False es deliberado: se permite cerrar sesión con el refresh token ya
    # caducado. Por eso la sesión se comprueba contra la base de datos: sin eso, cualquier
    # refresh token histórico serviría para cerrar la sesión activa del usuario.
    decoded = JWTHandler.decode_token(logout_request.refresh_token, "refresh", verify_exp=False)
    # Sin sesión única no hay nada que revocar en el servidor: el token vale hasta que
    # caduca, y cerrar sesión es que el cliente lo descarte.

    return APIResponse.success(data=LogoutData(), message="Sesión cerrada exitosamente")


@router.post("/refresh", response_model=APIResponse[LoginData])
async def refresh_token(refresh_request: RefreshRequest):
    decoded = JWTHandler.decode_token(refresh_request.refresh_token, "refresh")

    async with auth_api.session_manager.get_session() as session:
        usuario = await auth_api.user.find(decoded.user_id, includes=["user_roles.role", "realm"], session=session)
        if usuario is None:
            raise InvalidCredentialsException(CREDENCIALES_INVALIDAS)
        # Antes no se comprobaba: un usuario desactivado seguía refrescando indefinidamente,
        # porque cada refresco emite un refresh token nuevo.
        _comprobar_vigencia(usuario)
        permisos = await _permisos(usuario, session)
        datos = await _emitir(usuario, permisos, session, nueva_sesion=False)

    return APIResponse.success(data=datos, message="Token refrescado exitosamente")


@router.get("/me", response_model=APIResponse[UserInfoData])
async def get_current_user_info(current_user: CurrentUser):
    async with auth_api.session_manager.get_session() as session:
        permisos = await _permisos(current_user, session)
    return APIResponse.success(
        data=_info(current_user, permisos),
        message="Información del usuario obtenida exitosamente",
    )


@router.patch("/me", response_model=APIResponse[UserInfoData])
async def update_current_user_info(data: MeUpdate, current_user: CurrentUser):
    """Actualiza el perfil del usuario autenticado: nombre, apellidos y email.

    Autoservicio: el usuario a modificar sale de `current_user`, es decir del token ya
    validado, y nunca de la ruta ni del cuerpo. No hay identificador manipulable por el
    cliente, así que no puede tocar el perfil de otro. El DTO `MeUpdate` acota los
    campos: `is_active` y `roles` siguen siendo exclusivos de /rbac/{realm}/user, y la
    contraseña se cambia por `POST /auth/me/password`.
    """
    payload = data.model_dump(exclude_unset=True, exclude_none=True)
    if not payload:
        raise ValidationException("No hay campos que actualizar")

    async with auth_api.session_manager.get_session() as session:
        await auth_api.user.update(
            current_user.id,
            updated_values=UserUpdateValues(**payload),
            session=session,
        )
        usuario = await auth_api.user.find(current_user.id, includes=["user_roles.role", "realm"], session=session)
        permisos = await _permisos(usuario, session)

    return APIResponse.success(data=_info(usuario, permisos), message="Perfil actualizado exitosamente")


@router.post("/me/password", response_model=APIResponse[LoginData])
async def change_password(data: PasswordChange, current_user: CurrentUser):
    """Cambia la contraseña del usuario autenticado, **comprobando antes la actual**.

    En una tablet que se queda con la sesión abierta, nadie puede cambiarla sin saberla. El
    usuario sale del token, nunca del cuerpo.

    Es un login con la contraseña nueva: abre una sesión nueva —la anterior y cualquier token
    emitido antes dejan de valer— y responde como `/auth/{realm}/login`, con los tokens con que
    seguir. La aplicación los adopta y el usuario no tiene que
    volver a entrar.

    Errores (422 `VALIDATION_ERROR`, con su `field`): `current_password` si no es la correcta;
    `new_password` si es corta o igual a la actual.
    """
    data.comprobar()
    valores = UserUpdateValues(password=data.new_password)

    async with auth_api.session_manager.get_session() as session:
        if not await auth_api.user.verify_password(
            current_user.id,
            value=data.current_password, session=session,
        ):
            raise ValidationException("La contraseña actual no es correcta", field="current_password")

        # El setter del modelo la guarda con hash (columna `hash=True` del schema `auth`).
        await auth_api.user.update(
            current_user.id,
            updated_values=valores,
            session=session,
        )
        usuario = await auth_api.user.find(current_user.id, includes=["user_roles.role", "realm"], session=session)
        permisos = await _permisos(usuario, session)
        datos = await _emitir(usuario, permisos, session, nueva_sesion=True)
    return APIResponse.success(data=datos, message="Contraseña cambiada")
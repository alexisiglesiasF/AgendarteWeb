# Generado por tai-api: este fichero lo reescribe `tai-api generate`.
"""
agendarte-api - RBAC Backend (Database)
Generado automáticamente por tai-api

Las operaciones de gestión de usuarios y roles de `/rbac/{realm}`, sobre el cliente del
schema `auth` por su fachada. Cada operación que escribe va en **una transacción**: antes
una actualización de usuario con cambio de roles eran media docena de transacciones, y un
fallo a mitad dejaba los roles cambiados y el resto no.
"""
from __future__ import annotations
from typing import List, Optional

from api.database.auth import (
    auth_async_api as auth_api,
    UserCreate,
    UserRead,
    UserUpdateValues,
    UserRoleCreate,
)
from api.resources import APIException, ErrorCode
from .rbac_models import RBACUser, RBACUserCreate, RBACUserUpdate, RBACRoleInfo, RBACRLS


def _no_encontrado(mensaje: str) -> APIException:
    """
    Un 404 con el mensaje tal cual.

    No se usa `RecordNotFoundException`, que añade « no encontrado» a lo que recibe: los
    mensajes de este módulo salían como «Usuario 'x' no encontrado en realm 'main' no
    encontrado».
    """
    return APIException(mensaje, error_code=ErrorCode.RECORD_NOT_FOUND)


def _user_to_rbac(user: UserRead) -> RBACUser:
    return RBACUser(
        id=str(user.id),
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        full_name=user.full_name,
        email=user.email,
        is_active=user.is_active,
        roles=sorted(ur.role.name for ur in (user.user_roles or []) if ur.role is not None),
        attributes=user.attributes,
    )


async def _realm_id(realm_name: str, session) -> int:
    """El id del realm. `auth` se relaciona por ids; las rutas de `/rbac` lo nombran."""
    realm = await auth_api.realm.find_by(name=realm_name, session=session)
    if realm is None:
        raise _no_encontrado(f"El realm '{realm_name}' no existe")
    return realm.id


async def _usuario(realm_name: str, username: str, session, includes=None) -> UserRead:
    """El usuario por su nombre, que es único en su realm."""
    user = await auth_api.user.find_by(
        username=username, realm_id=await _realm_id(realm_name, session), includes=includes, session=session,
    )
    if user is None:
        raise _no_encontrado(f"Usuario '{username}' no encontrado en realm '{realm_name}'")
    return user


async def _roles(realm_id: int, realm_name: str, roles: List[str], session) -> dict:
    """
    Los ids de unos roles **del realm**, por su nombre, antes de asignarlos.

    Sin esto, un rol inexistente llegaba a la base de datos como una violación de clave
    foránea y el cliente recibía un error de base de datos en vez de saber qué rol falta. Y
    es lo que garantiza que un usuario solo recibe roles de su realm: con ids, la clave de
    `user_role` ya no lo impide.
    """
    if not roles:
        return {}
    existentes = await auth_api.role.find_many(in_name=list(roles), realm_id=realm_id, session=session)
    ids = {rol.name: rol.id for rol in existentes}
    faltan = sorted(set(roles) - set(ids))
    if faltan:
        raise _no_encontrado(f"Roles que no existen en el realm '{realm_name}': {', '.join(faltan)}")
    return ids


async def create_user(realm_name: str, data: RBACUserCreate) -> RBACUser:
    async with auth_api.session_manager.get_session() as session:
        realm_id = await _realm_id(realm_name, session)
        roles = await _roles(realm_id, realm_name, data.roles, session)
        creado = await auth_api.user.create(
            UserCreate(
                username=data.username,
                password=data.password,
                first_name=data.first_name,
                last_name=data.last_name,
                email=data.email,
                is_active=data.is_active,
                attributes=data.attributes,
                realm_id=realm_id,
                user_roles=[UserRoleCreate(role_id=roles[nombre]) for nombre in data.roles],
            ),
            session=session,
        )
        user = await auth_api.user.find(creado.id, includes=["user_roles.role"], session=session)
    return _user_to_rbac(user)


async def list_users(
    realm_name: str,
    limit: int = 100,
    offset: int = 0,
    is_active: Optional[bool] = None,
    username: Optional[str] = None,
    role: Optional[str] = None,
) -> tuple[List[RBACUser], int]:
    """
    Una página de usuarios y el total **con los mismos filtros**.

    Dos defectos que tenía:

    - El total se contaba con `username="%texto%"` —el DTO de filtro lo trata como un
      `ILIKE`— y la página con `username="texto"`, igualdad exacta. Uno y otro no
      describían el mismo conjunto. Ahora los dos buscan por «contiene».
    - El filtro por rol se aplicaba **en memoria después de paginar**: con 100 usuarios por
      página, los del rol que cayeran en la página siguiente no aparecían nunca, y el total
      era el de la página filtrada. Ahora se resuelve antes, contra la tabla de asignaciones.
    """
    async with auth_api.session_manager.get_session() as session:
        filtros = {
            "realm_id": await _realm_id(realm_name, session),
            "is_active": is_active,
            "username": f"%{username}%" if username else None,
        }
        if role is not None:
            rol = await auth_api.role.find_by(name=role, realm_id=filtros["realm_id"], session=session)
            asignaciones = await auth_api.user_role.find_many(
                role_id=rol.id, session=session,
            ) if rol is not None else []
            ids = sorted({a.user_id for a in asignaciones})
            if not ids:
                return [], 0
            filtros["in_id"] = ids

        users = await auth_api.user.find_many(
            limit=limit, offset=offset, order_by=["username"], includes=["user_roles.role"],
            session=session, **filtros,
        )
        total = await auth_api.user.count(session=session, **filtros)
    return [_user_to_rbac(u) for u in users], total


async def get_user(realm_name: str, username: str) -> RBACUser:
    async with auth_api.session_manager.get_session() as session:
        user = await _usuario(realm_name, username, session, includes=["user_roles.role"])
    return _user_to_rbac(user)


async def update_user(realm_name: str, username: str, data: RBACUserUpdate) -> RBACUser:
    """
    Actualiza un usuario, sus atributos de RLS y sus roles, todo en una transacción.
    """
    async with auth_api.session_manager.get_session() as session:
        user = await _usuario(realm_name, username, session, includes=["user_roles.role"])

        valores = UserUpdateValues(**{
            campo: getattr(data, campo)
            for campo in ("first_name", "last_name", "email", "is_active", "password")
            if getattr(data, campo) is not None
        })

        if data.attributes is not None:
            # `None` quita la regla (no aplica); `[]` la deja con cero valores.
            atributos = dict(user.attributes or {})
            for clave, valor in data.attributes.items():
                if valor is None:
                    atributos.pop(clave, None)
                else:
                    atributos[clave] = valor
            valores.attributes = atributos

        if data.roles is not None:
            actuales = {ur.role.name for ur in (user.user_roles or []) if ur.role is not None}
            nuevos = set(data.roles)
            ids = await _roles(user.realm_id, realm_name, sorted(nuevos - actuales), session)
            for ur in user.user_roles or []:
                if ur.role is not None and ur.role.name in actuales - nuevos:
                    await auth_api.user_role.delete(ur.id, session=session)
            for role_name in sorted(nuevos - actuales):
                await auth_api.user_role.create(
                    UserRoleCreate(user_id=user.id, role_id=ids[role_name]),
                    session=session,
                )

        if valores.to_dict():
            await auth_api.user.update(user.id, updated_values=valores, session=session)

        user = await auth_api.user.find(user.id, includes=["user_roles.role"], session=session)
    return _user_to_rbac(user)


async def delete_user(realm_name: str, username: str) -> None:
    async with auth_api.session_manager.get_session() as session:
        user = await _usuario(realm_name, username, session)
        await auth_api.user.delete(user.id, session=session)


async def list_roles(realm_name: str) -> List[RBACRoleInfo]:
    async with auth_api.session_manager.get_session() as session:
        roles = await auth_api.role.find_many(
            realm_id=await _realm_id(realm_name, session),
            includes=["role_permissions.permission"], order_by=["name"], session=session,
        )
    nombres = {role.id: role.name for role in roles}
    return [
        RBACRoleInfo(
            name=role.name,
            description=role.description,
            permissions=sorted(rp.permission.name for rp in (role.role_permissions or []) if rp.permission),
            parent_role_name=nombres.get(role.parent_id),
        )
        for role in roles
    ]


async def assign_role(realm_name: str, username: str, role_name: str) -> None:
    async with auth_api.session_manager.get_session() as session:
        user = await _usuario(realm_name, username, session, includes=["user_roles.role"])
        ids = await _roles(user.realm_id, realm_name, [role_name], session)
        # Asignar un rol que ya tiene no es un error, pero tampoco una fila más.
        if any(ur.role_id == ids[role_name] for ur in (user.user_roles or [])):
            return
        await auth_api.user_role.create(
            UserRoleCreate(user_id=user.id, role_id=ids[role_name]),
            session=session,
        )


async def remove_role(realm_name: str, username: str, role_name: str) -> None:
    async with auth_api.session_manager.get_session() as session:
        user = await _usuario(realm_name, username, session, includes=["user_roles.role"])
        asignaciones = [
            ur for ur in (user.user_roles or []) if ur.role is not None and ur.role.name == role_name
        ]
        if not asignaciones:
            raise _no_encontrado(f"El usuario '{username}' no tiene el rol '{role_name}'")
        for ur in asignaciones:
            await auth_api.user_role.delete(ur.id, session=session)


async def list_rls(realm_name: str) -> List[RBACRLS]:
    async with auth_api.session_manager.get_session() as session:
        rls_list = await auth_api.row_level_security.find_many(
            realm_id=await _realm_id(realm_name, session), session=session,
        )
    return [
        RBACRLS(target_schema=rls.schema_name, target_model=rls.table_name, target_field=rls.column_name)
        for rls in rls_list
    ]
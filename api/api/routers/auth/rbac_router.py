# Generado por tai-api: este fichero lo reescribe `tai-api generate`.
"""
agendarte-api - RBAC Router
Generado automáticamente por tai-api auth init

Endpoints unificados de gestión RBAC.
Funciona con cualquier backend (Database / Keycloak).
"""
from __future__ import annotations
from fastapi import APIRouter, Depends
from typing import List, Optional
from api.resources import APIResponse, PaginatedResponse

from .dependencies import requires_permissions_from_realm
from .utils import UserRoleData
from .rbac_models import RBACUser, RBACUserCreate, RBACUserUpdate, RBACRoleInfo, RBACRLS
from .rbac_backend import (
    create_user,
    list_users,
    get_user,
    update_user,
    delete_user,
    list_roles,
    assign_role,
    remove_role,
    list_rls,
)

router = APIRouter(
    prefix="/rbac/{realm_name}",
    tags=["RBAC"],
    dependencies=[Depends(requires_permissions_from_realm("admin"))]
)


@router.post("/user", response_model=APIResponse[RBACUser])
async def create_user_endpoint(realm_name: str, user: RBACUserCreate):
    result = await create_user(realm_name, user)
    return APIResponse.success(data=result, message="Usuario creado exitosamente")


@router.get("/user", response_model=APIResponse[List[RBACUser]])
async def list_users_endpoint(
        realm_name: str,
        limit: int = 100,
        offset: int = 0,
        is_active: Optional[bool] = None,
        username: Optional[str] = None,
        role: Optional[str] = None
    ):
    users, total = await list_users(
        realm_name,
        limit=limit,
        offset=offset,
        is_active=is_active,
        username=username,
        role=role
    )
    return PaginatedResponse.success_paginated(
        data=users, total=total, limit=limit, offset=offset,
        message="Usuarios obtenidos exitosamente"
    )


@router.get("/user/{username}", response_model=APIResponse[RBACUser])
async def get_user_endpoint(realm_name: str, username: str):
    result = await get_user(realm_name, username)
    return APIResponse.success(data=result, message="Usuario obtenido exitosamente")


@router.patch("/user/{username}", response_model=APIResponse[RBACUser])
async def update_user_endpoint(realm_name: str, username: str, data: RBACUserUpdate):
    result = await update_user(realm_name, username, data)
    return APIResponse.success(data=result, message="Usuario actualizado exitosamente")


@router.delete("/user/{username}", response_model=APIResponse[str])
async def delete_user_endpoint(realm_name: str, username: str):
    await delete_user(realm_name, username)
    return APIResponse.success(data=username, message="Usuario eliminado exitosamente")


@router.get("/role", response_model=APIResponse[List[RBACRoleInfo]])
async def list_roles_endpoint(realm_name: str):
    roles = await list_roles(realm_name)
    return APIResponse.success(data=roles, message="Roles obtenidos exitosamente")


@router.post("/user/{username}/role", response_model=APIResponse[bool])
async def assign_role_endpoint(
    realm_name: str,
    username: str,
    user_role_data: UserRoleData
):
    await assign_role(realm_name, username, user_role_data.role_name)
    return APIResponse.success(
        data=True, message="Rol asignado exitosamente",
        meta={"role": user_role_data.role_name, "username": username}
    )


@router.delete("/user/{username}/role/{role_name}", response_model=APIResponse[bool])
async def remove_role_by_path_endpoint(realm_name: str, username: str, role_name: str):
    """
    Quita un rol al usuario. El rol va en la ruta: un `DELETE` sin cuerpo, que ningún proxy ni
    cliente descarta. Es la que usa el cliente TypeScript.
    """
    await remove_role(realm_name, username, role_name)
    return APIResponse.success(
        data=True, message="Rol removido exitosamente",
        meta={"role": role_name, "username": username}
    )


@router.delete("/user/{username}/role", response_model=APIResponse[bool])
async def remove_role_endpoint(
    realm_name: str,
    username: str,
    user_role_data: UserRoleData
):
    """
    Quita un rol al usuario, con el rol en el cuerpo. Hay proxies y clientes que descartan el cuerpo
    de un `DELETE`: se conserva para los frontends que ya la usan, y lo nuevo usa
    `DELETE /user/{username}/role/{role_name}`.
    """
    await remove_role(realm_name, username, user_role_data.role_name)
    return APIResponse.success(
        data=True, message="Rol removido exitosamente",
        meta={"role": user_role_data.role_name, "username": username}
    )

@router.get("/rls", response_model=APIResponse[List[RBACRLS]])
async def list_rls_endpoint(realm_name: str):
    rls_list = await list_rls(realm_name)
    return APIResponse.success(data=rls_list, message="RLS obtenidos exitosamente")
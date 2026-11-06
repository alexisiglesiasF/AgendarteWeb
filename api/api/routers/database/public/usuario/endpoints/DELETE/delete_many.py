from fastapi import Query, Depends
from typing import Optional, List
from datetime import datetime

from api.routers.auth import requires_permissions, build_rls_rules, AccessToken
from api.database.public import username_context
from api.database.public._shared import get_model_by_name

from api.database.public import public_async_api, UsuarioFilter, RLS
from api.resources import APIResponse, ValidationException
from .docs import DELETE_MANY_RESPONSES, DELETE_MANY_SUMMARY
from ... import usuario_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@usuario_router.delete("",
    response_model=APIResponse[int],
    response_description="Número de registros de usuario eliminados",
    operation_id="public_usuario_delete_many",
    summary=DELETE_MANY_SUMMARY,
    responses=DELETE_MANY_RESPONSES
)
async def usuario_delete_many(
    in_id: Optional[List[int]] = Query(None, description="Filtrar por múltiples valores de id"),
    nombre: Optional[str] = Query(None, description="Filtrar por nombre. Nombre visible"),
    in_nombre: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de nombre"),
    apellido: Optional[str] = Query(None, description="Filtrar por apellido. Apellido visible"),
    in_apellido: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de apellido"),
    email: Optional[str] = Query(None, description="Filtrar por email. Campo email de la tabla usuario"),
    in_email: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de email"),
    min_created_at: Optional[datetime] = Query(None, description="Valor mínimo para created_at (incluido)"),
    max_created_at: Optional[datetime] = Query(None, description="Valor máximo para created_at (incluido)"),
    in_created_by: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de created_by"),
    min_updated_at: Optional[datetime] = Query(None, description="Valor mínimo para updated_at (incluido)"),
    max_updated_at: Optional[datetime] = Query(None, description="Valor máximo para updated_at (incluido)"),
    in_updated_by: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de updated_by"),
    confirm_all: bool = Query(False, description="Necesario para eliminar sin ningún filtro, es decir, todas las filas a las que alcanza tu acceso. Sin filtros y sin esto, la petición se rechaza."),
    token: AccessToken = Depends(requires_permissions("delete", "usuario")),
    _estricto: None = Depends(estricto("usuario", "delete_many")),
) -> APIResponse[int]:
    """
    Elimina múltiples Usuarios que coincidan con los filtros.
    """
    filtro = UsuarioFilter(
        in_id=in_id,
        nombre=nombre,
        in_nombre=in_nombre,
        apellido=apellido,
        in_apellido=in_apellido,
        email=email,
        in_email=in_email,
        min_created_at=min_created_at,
        max_created_at=max_created_at,
        in_created_by=in_created_by,
        min_updated_at=min_updated_at,
        max_updated_at=max_updated_at,
        in_updated_by=in_updated_by,
    )
    if not filtro.to_dict() and not confirm_all:
        raise ValidationException(
            "Sin filtros, esta operación alcanzaría todas las filas. "
            "Añade algún filtro, o confirm_all=true si es lo que quieres.",
            "confirm_all",
        )

    rls = build_rls_rules(token, "public", get_model_by_name, RLS)
    with username_context(token.preferred_username):
        result = await public_async_api.usuario.delete_many(
            in_id=in_id,
            nombre=nombre,
            in_nombre=in_nombre,
            apellido=apellido,
            in_apellido=in_apellido,
            email=email,
            in_email=in_email,
            min_created_at=min_created_at,
            max_created_at=max_created_at,
            in_created_by=in_created_by,
            min_updated_at=min_updated_at,
            max_updated_at=max_updated_at,
            in_updated_by=in_updated_by,
            rls=rls,
        )

        message = f"{result} Usuarios eliminados exitosamente" if result > 0 else "No se encontraron registros que coincidan con los criterios"

        return APIResponse.success(
            data=result,
            message=message
        )

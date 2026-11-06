from fastapi import Query, Depends
from typing import Optional, List
from datetime import datetime

from api.routers.auth import requires_permissions, build_rls_rules, AccessToken
from api.database.public import username_context
from api.database.public._shared import get_model_by_name

from api.database.public import public_async_api, RLS
from api.resources import APIResponse
from .docs import EXISTS_RESPONSES, EXISTS_SUMMARY
from ... import usuario_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@usuario_router.get("/exists",
    response_model=APIResponse[bool],
    operation_id="public_usuario_exists",
    summary=EXISTS_SUMMARY,
    responses=EXISTS_RESPONSES
)
async def usuario_exists(
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
    token: AccessToken = Depends(requires_permissions("read", "usuario")),
    _estricto: None = Depends(estricto("usuario", "exists")),
) -> APIResponse[bool]:
    """
    Verifica si existe al menos un usuario que coincida con los filtros.
    """
    rls = build_rls_rules(token, "public", get_model_by_name, RLS)
    with username_context(token.preferred_username):
        result = await public_async_api.usuario.exists(
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
            rls=rls
        )

        return APIResponse.success(
            data=result,
            message="Verificación realizada exitosamente"
        )

from fastapi import Query, Depends
from typing import Optional, List
from datetime import datetime

from api.routers.auth import requires_permissions, build_rls_rules, AccessToken
from api.database.public import username_context
from api.database.public._shared import get_model_by_name

from api.database.public import public_async_api, RLS
from api.resources import APIResponse
from .docs import COUNT_RESPONSES, COUNT_SUMMARY
from ... import proyecto_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@proyecto_router.get("/count",
    response_model=APIResponse[int],
    response_description="Número de registros de proyecto según los filtros aplicados",
    operation_id="public_proyecto_count",
    summary=COUNT_SUMMARY,
    responses=COUNT_RESPONSES
)
async def proyecto_count(
    in_id: Optional[List[int]] = Query(None, description="Filtrar por múltiples valores de id"),
    id_usuario: Optional[int] = Query(None, description="Filtrar por id_usuario"),
    in_id_usuario: Optional[List[int]] = Query(None, description="Filtrar por múltiples valores de id_usuario"),
    nombre: Optional[str] = Query(None, description="Filtrar por nombre. Nombre del proyecto"),
    in_nombre: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de nombre"),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo. Tipo de proyecto"),
    in_tipo: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de tipo"),
    descripcion: Optional[str] = Query(None, description="Filtrar por descripcion. Descripción del proyecto"),
    in_descripcion: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de descripcion"),
    min_created_at: Optional[datetime] = Query(None, description="Valor mínimo para created_at (incluido)"),
    max_created_at: Optional[datetime] = Query(None, description="Valor máximo para created_at (incluido)"),
    in_created_by: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de created_by"),
    min_updated_at: Optional[datetime] = Query(None, description="Valor mínimo para updated_at (incluido)"),
    max_updated_at: Optional[datetime] = Query(None, description="Valor máximo para updated_at (incluido)"),
    in_updated_by: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de updated_by"),
    token: AccessToken = Depends(requires_permissions("read", "proyecto")),
    _estricto: None = Depends(estricto("proyecto", "count")),
) -> APIResponse[int]:
    """
    Cuenta el número de Proyectos que coinciden con los filtros.
    """
    rls = build_rls_rules(token, "public", get_model_by_name, RLS)
    with username_context(token.preferred_username):
        result = await public_async_api.proyecto.count(
            in_id=in_id,
            id_usuario=id_usuario,
            in_id_usuario=in_id_usuario,
            nombre=nombre,
            in_nombre=in_nombre,
            tipo=tipo,
            in_tipo=in_tipo,
            descripcion=descripcion,
            in_descripcion=in_descripcion,
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
            message="Conteo realizado exitosamente"
        )

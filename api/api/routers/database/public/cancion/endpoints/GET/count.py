from fastapi import Query, Depends
from typing import Optional, List
from datetime import datetime

from api.routers.auth import requires_permissions, build_rls_rules, AccessToken
from api.database.public import username_context
from api.database.public._shared import get_model_by_name

from api.database.public import public_async_api, RLS
from api.resources import APIResponse
from .docs import COUNT_RESPONSES, COUNT_SUMMARY
from ... import cancion_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@cancion_router.get("/count",
    response_model=APIResponse[int],
    response_description="Número de registros de cancion según los filtros aplicados",
    operation_id="public_cancion_count",
    summary=COUNT_SUMMARY,
    responses=COUNT_RESPONSES
)
async def cancion_count(
    in_id: Optional[List[int]] = Query(None, description="Filtrar por múltiples valores de id"),
    id_repertorio: Optional[int] = Query(None, description="Filtrar por id_repertorio"),
    in_id_repertorio: Optional[List[int]] = Query(None, description="Filtrar por múltiples valores de id_repertorio"),
    nombre: Optional[str] = Query(None, description="Filtrar por nombre. Nombre de la canción"),
    in_nombre: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de nombre"),
    min_created_at: Optional[datetime] = Query(None, description="Valor mínimo para created_at (incluido)"),
    max_created_at: Optional[datetime] = Query(None, description="Valor máximo para created_at (incluido)"),
    in_created_by: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de created_by"),
    min_updated_at: Optional[datetime] = Query(None, description="Valor mínimo para updated_at (incluido)"),
    max_updated_at: Optional[datetime] = Query(None, description="Valor máximo para updated_at (incluido)"),
    in_updated_by: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de updated_by"),
    token: AccessToken = Depends(requires_permissions("read", "cancion")),
    _estricto: None = Depends(estricto("cancion", "count")),
) -> APIResponse[int]:
    """
    Cuenta el número de Cancions que coinciden con los filtros.
    """
    rls = build_rls_rules(token, "public", get_model_by_name, RLS)
    with username_context(token.preferred_username):
        result = await public_async_api.cancion.count(
            in_id=in_id,
            id_repertorio=id_repertorio,
            in_id_repertorio=in_id_repertorio,
            nombre=nombre,
            in_nombre=in_nombre,
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

from fastapi.exceptions import RequestValidationError
from fastapi import Query, Path, Depends
from typing import Optional, List
from datetime import datetime

from api.routers.auth import requires_permissions, build_rls_rules, AccessToken
from api.database.public import username_context
from api.database.public._shared import get_model_by_name

from api.database.public import public_async_api, AggRow, RLS
from api.resources import APIResponse
from .docs import MAX_RESPONSES, MAX_SUMMARY
from ... import cancion_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@cancion_router.get("/{field}/max",
    response_model=APIResponse[List[AggRow]],
    operation_id="public_cancion_max_field",
    summary=MAX_SUMMARY,
    responses=MAX_RESPONSES
)
async def cancion_max_field(
    field: str = Path(..., description="Nombre del campo para encontrar el valor máximo"),
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
    _estricto: None = Depends(estricto("cancion", "max")),
) -> APIResponse[List[AggRow]]:
    """
    ## Resumen
    Encuentra el valor máximo de un campo específico que coincida con los filtros.

    ## Parámetros
    - **field** (path): Nombre del campo para encontrar el máximo.

    ## Filtros Opcionales
    - **in_id**: Filtrar por múltiples valores de id (OR lógico)
    - **id_repertorio**: Filtrar por id_repertorio
    - **in_id_repertorio**: Filtrar por múltiples valores de id_repertorio (OR lógico)
    - **nombre**: Filtrar por nombre
    - **in_nombre**: Filtrar por múltiples valores de nombre (OR lógico)
    - **min_created_at**: Filtrar por valor mínimo de created_at (incluído)
    - **max_created_at**: Filtrar por valor máximo de created_at (incluído)
    - **in_created_by**: Filtrar por múltiples valores de created_by (OR lógico)
    - **min_updated_at**: Filtrar por valor mínimo de updated_at (incluído)
    - **max_updated_at**: Filtrar por valor máximo de updated_at (incluído)
    - **in_updated_by**: Filtrar por múltiples valores de updated_by (OR lógico)

    """
    rls = build_rls_rules(token, "public", get_model_by_name, RLS)

    with username_context(token.preferred_username):
        result = await public_async_api.cancion.max(
            agg_fields=[field],
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

        if not result.success:
            raise RequestValidationError([
                {"type": "value_error", "loc": ("path", "field"), "msg": mensaje, "input": field}
                for mensaje in (result.errors or result.warnings or ["La operación no se puede aplicar"])
            ])

        return APIResponse.success(
            data=result.rows,
            message=f"Máximo de '{field}' calculado exitosamente",
            meta=result.metadata
        )

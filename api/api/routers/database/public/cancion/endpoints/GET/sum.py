from fastapi.exceptions import RequestValidationError
from fastapi import Query, Path
from typing import Optional, List
from datetime import datetime


from api.database.public import public_async_api, AggRow
from api.resources import APIResponse
from .docs import SUM_RESPONSES, SUM_SUMMARY
from ... import cancion_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@cancion_router.get("/{field}/sum",
    response_model=APIResponse[List[AggRow]],
    operation_id="public_cancion_sum_field",
    summary=SUM_SUMMARY,
    responses=SUM_RESPONSES
)
async def cancion_sum_field(
    field: str = Path(..., description="Nombre del campo numérico a sumar"),
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
    _estricto: None = Depends(estricto("cancion", "sum")),
) -> APIResponse[List[AggRow]]:
    """
    ## Resumen
    Calcula la suma de un campo numérico específico que coincida con los filtros.

    ## Parámetros
    - **field** (path): Nombre del campo numérico a sumar.

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
    result = await public_async_api.cancion.sum(
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
    )

    if not result.success:
        raise RequestValidationError([
            {"type": "value_error", "loc": ("path", "field"), "msg": mensaje, "input": field}
            for mensaje in (result.errors or result.warnings or ["La operación no se puede aplicar"])
        ])

    return APIResponse.success(
        data=result.rows,
        message=f"Suma de '{field}' calculada exitosamente",
        meta=result.metadata
    )

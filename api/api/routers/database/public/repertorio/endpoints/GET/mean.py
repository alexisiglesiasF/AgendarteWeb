from fastapi.exceptions import RequestValidationError
from fastapi import Query, Path
from typing import Optional, List
from datetime import datetime


from api.database.public import public_async_api, AggRow
from api.resources import APIResponse
from .docs import MEAN_RESPONSES, MEAN_SUMMARY
from ... import repertorio_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@repertorio_router.get("/{field}/mean",
    response_model=APIResponse[List[AggRow]],
    operation_id="public_repertorio_mean_field",
    summary=MEAN_SUMMARY,
    responses=MEAN_RESPONSES
)
async def repertorio_mean_field(
    field: str = Path(..., description="Nombre del campo numérico para calcular la media"),
    in_id: Optional[List[int]] = Query(None, description="Filtrar por múltiples valores de id"),
    usuario_id: Optional[int] = Query(None, description="Filtrar por usuario_id"),
    in_usuario_id: Optional[List[int]] = Query(None, description="Filtrar por múltiples valores de usuario_id"),
    id_proyecto: Optional[int] = Query(None, description="Filtrar por id_proyecto"),
    in_id_proyecto: Optional[List[int]] = Query(None, description="Filtrar por múltiples valores de id_proyecto"),
    nombre: Optional[str] = Query(None, description="Filtrar por nombre. Nombre del repertorio"),
    in_nombre: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de nombre"),
    descripcion: Optional[str] = Query(None, description="Filtrar por descripcion. Descripción del repertorio"),
    in_descripcion: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de descripcion"),
    min_created_at: Optional[datetime] = Query(None, description="Valor mínimo para created_at (incluido)"),
    max_created_at: Optional[datetime] = Query(None, description="Valor máximo para created_at (incluido)"),
    in_created_by: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de created_by"),
    min_updated_at: Optional[datetime] = Query(None, description="Valor mínimo para updated_at (incluido)"),
    max_updated_at: Optional[datetime] = Query(None, description="Valor máximo para updated_at (incluido)"),
    in_updated_by: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de updated_by"),
    _estricto: None = Depends(estricto("repertorio", "mean")),
) -> APIResponse[List[AggRow]]:
    """
    ## Resumen
    Calcula la media (promedio) de un campo numérico específico que coincida con los filtros.

    ## Parámetros
    - **field** (path): Nombre del campo numérico para calcular la media.

    ## Filtros Opcionales
    - **in_id**: Filtrar por múltiples valores de id (OR lógico)
    - **usuario_id**: Filtrar por usuario_id
    - **in_usuario_id**: Filtrar por múltiples valores de usuario_id (OR lógico)
    - **id_proyecto**: Filtrar por id_proyecto
    - **in_id_proyecto**: Filtrar por múltiples valores de id_proyecto (OR lógico)
    - **nombre**: Filtrar por nombre
    - **in_nombre**: Filtrar por múltiples valores de nombre (OR lógico)
    - **descripcion**: Filtrar por descripcion
    - **in_descripcion**: Filtrar por múltiples valores de descripcion (OR lógico)
    - **min_created_at**: Filtrar por valor mínimo de created_at (incluído)
    - **max_created_at**: Filtrar por valor máximo de created_at (incluído)
    - **in_created_by**: Filtrar por múltiples valores de created_by (OR lógico)
    - **min_updated_at**: Filtrar por valor mínimo de updated_at (incluído)
    - **max_updated_at**: Filtrar por valor máximo de updated_at (incluído)
    - **in_updated_by**: Filtrar por múltiples valores de updated_by (OR lógico)

    """
    result = await public_async_api.repertorio.mean(
        agg_fields=[field],
        in_id=in_id,
        usuario_id=usuario_id,
        in_usuario_id=in_usuario_id,
        id_proyecto=id_proyecto,
        in_id_proyecto=in_id_proyecto,
        nombre=nombre,
        in_nombre=in_nombre,
        descripcion=descripcion,
        in_descripcion=in_descripcion,
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
        message=f"Media de '{field}' calculada exitosamente",
        meta=result.metadata
    )

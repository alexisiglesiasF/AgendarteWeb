from fastapi.exceptions import RequestValidationError
from fastapi import Query, Path
from typing import Optional, List
from datetime import datetime


from api.database.public import public_async_api, AggRow
from api.resources import APIResponse
from .docs import MIN_RESPONSES, MIN_SUMMARY
from ... import proyecto_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@proyecto_router.get("/{field}/min",
    response_model=APIResponse[List[AggRow]],
    operation_id="public_proyecto_min_field",
    summary=MIN_SUMMARY,
    responses=MIN_RESPONSES
)
async def proyecto_min_field(
    field: str = Path(..., description="Nombre del campo para encontrar el valor mínimo"),
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
    _estricto: None = Depends(estricto("proyecto", "min")),
) -> APIResponse[List[AggRow]]:
    """
    ## Resumen
    Encuentra el valor mínimo de un campo específico que coincida con los filtros.

    ## Parámetros
    - **field** (path): Nombre del campo para encontrar el mínimo.

    ## Filtros Opcionales
    - **in_id**: Filtrar por múltiples valores de id (OR lógico)
    - **id_usuario**: Filtrar por id_usuario
    - **in_id_usuario**: Filtrar por múltiples valores de id_usuario (OR lógico)
    - **nombre**: Filtrar por nombre
    - **in_nombre**: Filtrar por múltiples valores de nombre (OR lógico)
    - **tipo**: Filtrar por tipo
    - **in_tipo**: Filtrar por múltiples valores de tipo (OR lógico)
    - **descripcion**: Filtrar por descripcion
    - **in_descripcion**: Filtrar por múltiples valores de descripcion (OR lógico)
    - **min_created_at**: Filtrar por valor mínimo de created_at (incluído)
    - **max_created_at**: Filtrar por valor máximo de created_at (incluído)
    - **in_created_by**: Filtrar por múltiples valores de created_by (OR lógico)
    - **min_updated_at**: Filtrar por valor mínimo de updated_at (incluído)
    - **max_updated_at**: Filtrar por valor máximo de updated_at (incluído)
    - **in_updated_by**: Filtrar por múltiples valores de updated_by (OR lógico)

    """
    result = await public_async_api.proyecto.min(
        agg_fields=[field],
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
    )

    if not result.success:
        raise RequestValidationError([
            {"type": "value_error", "loc": ("path", "field"), "msg": mensaje, "input": field}
            for mensaje in (result.errors or result.warnings or ["La operación no se puede aplicar"])
        ])

    return APIResponse.success(
        data=result.rows,
        message=f"Mínimo de '{field}' calculado exitosamente",
        meta=result.metadata
    )

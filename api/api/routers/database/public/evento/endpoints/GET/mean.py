from fastapi.exceptions import RequestValidationError
from fastapi import Query, Path
from typing import Optional, List
from datetime import datetime, time


from api.database.public import public_async_api, AggRow
from api.resources import APIResponse
from .docs import MEAN_RESPONSES, MEAN_SUMMARY
from ... import evento_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@evento_router.get("/{field}/mean",
    response_model=APIResponse[List[AggRow]],
    operation_id="public_evento_mean_field",
    summary=MEAN_SUMMARY,
    responses=MEAN_RESPONSES
)
async def evento_mean_field(
    field: str = Path(..., description="Nombre del campo numérico para calcular la media"),
    in_id: Optional[List[int]] = Query(None, description="Filtrar por múltiples valores de id"),
    usuario_id: Optional[int] = Query(None, description="Filtrar por usuario_id"),
    in_usuario_id: Optional[List[int]] = Query(None, description="Filtrar por múltiples valores de usuario_id"),
    id_proyecto: Optional[int] = Query(None, description="Filtrar por id_proyecto"),
    in_id_proyecto: Optional[List[int]] = Query(None, description="Filtrar por múltiples valores de id_proyecto"),
    nombre: Optional[str] = Query(None, description="Filtrar por nombre. Nombre del evento"),
    in_nombre: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de nombre"),
    ubicacion: Optional[str] = Query(None, description="Filtrar por ubicacion. Ubicacion del evento"),
    in_ubicacion: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de ubicacion"),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo. Tipo de evento"),
    in_tipo: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de tipo"),
    min_fecha: Optional[datetime] = Query(None, description="Valor mínimo para fecha (incluido)"),
    max_fecha: Optional[datetime] = Query(None, description="Valor máximo para fecha (incluido)"),
    min_hora: Optional[time] = Query(None, description="Valor mínimo para hora (incluido)"),
    max_hora: Optional[time] = Query(None, description="Valor máximo para hora (incluido)"),
    estado: Optional[str] = Query(None, description="Filtrar por estado. Estado del evento"),
    in_estado: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de estado"),
    notas: Optional[str] = Query(None, description="Filtrar por notas. Notas adicionales del evento"),
    in_notas: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de notas"),
    min_created_at: Optional[datetime] = Query(None, description="Valor mínimo para created_at (incluido)"),
    max_created_at: Optional[datetime] = Query(None, description="Valor máximo para created_at (incluido)"),
    in_created_by: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de created_by"),
    min_updated_at: Optional[datetime] = Query(None, description="Valor mínimo para updated_at (incluido)"),
    max_updated_at: Optional[datetime] = Query(None, description="Valor máximo para updated_at (incluido)"),
    in_updated_by: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de updated_by"),
    _estricto: None = Depends(estricto("evento", "mean")),
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
    - **ubicacion**: Filtrar por ubicacion
    - **in_ubicacion**: Filtrar por múltiples valores de ubicacion (OR lógico)
    - **tipo**: Filtrar por tipo
    - **in_tipo**: Filtrar por múltiples valores de tipo (OR lógico)
    - **min_fecha**: Filtrar por valor mínimo de fecha (incluído)
    - **max_fecha**: Filtrar por valor máximo de fecha (incluído)
    - **min_hora**: Filtrar por valor mínimo de hora (incluído)
    - **max_hora**: Filtrar por valor máximo de hora (incluído)
    - **estado**: Filtrar por estado
    - **in_estado**: Filtrar por múltiples valores de estado (OR lógico)
    - **notas**: Filtrar por notas
    - **in_notas**: Filtrar por múltiples valores de notas (OR lógico)
    - **min_created_at**: Filtrar por valor mínimo de created_at (incluído)
    - **max_created_at**: Filtrar por valor máximo de created_at (incluído)
    - **in_created_by**: Filtrar por múltiples valores de created_by (OR lógico)
    - **min_updated_at**: Filtrar por valor mínimo de updated_at (incluído)
    - **max_updated_at**: Filtrar por valor máximo de updated_at (incluído)
    - **in_updated_by**: Filtrar por múltiples valores de updated_by (OR lógico)

    """
    result = await public_async_api.evento.mean(
        agg_fields=[field],
        in_id=in_id,
        usuario_id=usuario_id,
        in_usuario_id=in_usuario_id,
        id_proyecto=id_proyecto,
        in_id_proyecto=in_id_proyecto,
        nombre=nombre,
        in_nombre=in_nombre,
        ubicacion=ubicacion,
        in_ubicacion=in_ubicacion,
        tipo=tipo,
        in_tipo=in_tipo,
        min_fecha=min_fecha,
        max_fecha=max_fecha,
        min_hora=min_hora,
        max_hora=max_hora,
        estado=estado,
        in_estado=in_estado,
        notas=notas,
        in_notas=in_notas,
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

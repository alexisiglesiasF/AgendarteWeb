from fastapi import Query
from typing import Optional, List
from datetime import datetime, time


from api.database.public import public_async_api
from api.resources import APIResponse
from .docs import COUNT_RESPONSES, COUNT_SUMMARY
from ... import evento_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@evento_router.get("/count",
    response_model=APIResponse[int],
    response_description="Número de registros de evento según los filtros aplicados",
    operation_id="public_evento_count",
    summary=COUNT_SUMMARY,
    responses=COUNT_RESPONSES
)
async def evento_count(
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
    _estricto: None = Depends(estricto("evento", "count")),
) -> APIResponse[int]:
    """
    Cuenta el número de Eventos que coinciden con los filtros.
    """
    result = await public_async_api.evento.count(
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

    return APIResponse.success(
        data=result,
        message="Conteo realizado exitosamente"
    )

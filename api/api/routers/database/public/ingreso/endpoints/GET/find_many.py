from fastapi import Query
from typing import Optional, List, Literal
from datetime import datetime

from api.database.public import public_async_api, IngresoRead
from api.resources import APIResponse, PaginatedResponse
from .docs import FIND_MANY_RESPONSES, FIND_MANY_SUMMARY, FIND_MANY_DESCRIPTION
from ... import ingreso_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@ingreso_router.get("",
    response_model=APIResponse[List[IngresoRead]],
    response_description="Lista de registros de ingreso obtenido exitosamente",
    operation_id="public_ingreso_find_many",
    summary=FIND_MANY_SUMMARY,
    description=FIND_MANY_DESCRIPTION,
    responses=FIND_MANY_RESPONSES
)
async def ingreso_find_many(
    limit: Optional[int] = Query(None, description="Número de registros a retornar.", gt=0),
    order_by: List[str] = Query(None, description="Lista de nombres de columnas para ordenar los resultados. Si no existen serán omitidas."),
    order: Optional[Literal["ASC", "DESC"]] = Query("ASC", description="Dirección de ordenamiento: 'ASC' para ascendente (por defecto), 'DESC' para descendente. Solo aplica si order_by está definido", pattern="^(ASC|DESC)$"),
    offset: Optional[int] = Query(None, description="Número de registros a omitir desde el inicio. Útil para paginación. Debe ser un valor no negativo", ge=0),
    in_id: Optional[List[int]] = Query(None, description="Filtrar por múltiples valores de id"),
    id_evento: Optional[int] = Query(None, description="Filtrar por id_evento"),
    in_id_evento: Optional[List[int]] = Query(None, description="Filtrar por múltiples valores de id_evento"),
    nombre: Optional[str] = Query(None, description="Filtrar por nombre. Nombre del ingreso"),
    in_nombre: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de nombre"),
    min_importe: Optional[float] = Query(None, description="Valor mínimo para importe (incluido)"),
    max_importe: Optional[float] = Query(None, description="Valor máximo para importe (incluido)"),
    recibido: Optional[bool] = Query(None, description="Filtrar por recibido. Indica si el ingreso ha sido recibido o no"),
    concepto: Optional[str] = Query(None, description="Filtrar por concepto. Concepto del ingreso"),
    in_concepto: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de concepto"),
    min_created_at: Optional[datetime] = Query(None, description="Valor mínimo para created_at (incluido)"),
    max_created_at: Optional[datetime] = Query(None, description="Valor máximo para created_at (incluido)"),
    in_created_by: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de created_by"),
    min_updated_at: Optional[datetime] = Query(None, description="Valor mínimo para updated_at (incluido)"),
    max_updated_at: Optional[datetime] = Query(None, description="Valor máximo para updated_at (incluido)"),
    in_updated_by: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de updated_by"),
    includes: List[str] = Query(None, description="Lista de relaciones a incluir en la respuesta para obtener datos relacionados. Especifica los nombres de las relaciones que deseas expandir"),
    _estricto: None = Depends(estricto("ingreso", "find_many")),
) -> APIResponse[List[IngresoRead]]:
    # Ver el comentario de la rama con autorización: la página y su total comparten
    # transacción para no leerse en dos instantes distintos ni pagar dos conexiones.
    async with public_async_api.session_manager.get_session() as session:
        result = await public_async_api.ingreso.find_many(
            limit=limit,
            offset=offset,
            order_by=order_by,
            order=order,
            in_id=in_id,
            id_evento=id_evento,
            in_id_evento=in_id_evento,
            nombre=nombre,
            in_nombre=in_nombre,
            min_importe=min_importe,
            max_importe=max_importe,
            recibido=recibido,
            concepto=concepto,
            in_concepto=in_concepto,
            min_created_at=min_created_at,
            max_created_at=max_created_at,
            in_created_by=in_created_by,
            min_updated_at=min_updated_at,
            max_updated_at=max_updated_at,
            in_updated_by=in_updated_by,
            includes=includes,
            session=session
        )

        total = None
        if limit is not None or offset is not None:
            total = await public_async_api.ingreso.count(
                in_id=in_id,
                id_evento=id_evento,
                in_id_evento=in_id_evento,
                nombre=nombre,
                in_nombre=in_nombre,
                min_importe=min_importe,
                max_importe=max_importe,
                recibido=recibido,
                concepto=concepto,
                in_concepto=in_concepto,
                min_created_at=min_created_at,
                max_created_at=max_created_at,
                in_created_by=in_created_by,
                min_updated_at=min_updated_at,
                max_updated_at=max_updated_at,
                in_updated_by=in_updated_by,
                session=session
            )

        return PaginatedResponse.success_paginated(
            data=result,
            total=total,
            limit=limit,
            offset=offset,
            message=f"Ingresos obtenidos exitosamente"
        )

from fastapi import Query
from typing import Optional, List
from datetime import datetime


from api.database.public import public_async_api
from api.resources import APIResponse
from .docs import COUNT_RESPONSES, COUNT_SUMMARY
from ... import repertorio_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@repertorio_router.get("/count",
    response_model=APIResponse[int],
    response_description="Número de registros de repertorio según los filtros aplicados",
    operation_id="public_repertorio_count",
    summary=COUNT_SUMMARY,
    responses=COUNT_RESPONSES
)
async def repertorio_count(
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
    _estricto: None = Depends(estricto("repertorio", "count")),
) -> APIResponse[int]:
    """
    Cuenta el número de Repertorios que coinciden con los filtros.
    """
    result = await public_async_api.repertorio.count(
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

    return APIResponse.success(
        data=result,
        message="Conteo realizado exitosamente"
    )

from fastapi import Query
from typing import Optional, List
from datetime import datetime


from api.database.public import public_async_api, CancionFilter
from api.resources import APIResponse, ValidationException
from .docs import DELETE_MANY_RESPONSES, DELETE_MANY_SUMMARY
from ... import cancion_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@cancion_router.delete("",
    response_model=APIResponse[int],
    response_description="Número de registros de cancion eliminados",
    operation_id="public_cancion_delete_many",
    summary=DELETE_MANY_SUMMARY,
    responses=DELETE_MANY_RESPONSES
)
async def cancion_delete_many(
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
    confirm_all: bool = Query(False, description="Necesario para eliminar sin ningún filtro, es decir, todas las filas a las que alcanza tu acceso. Sin filtros y sin esto, la petición se rechaza."),
    _estricto: None = Depends(estricto("cancion", "delete_many")),
) -> APIResponse[int]:
    """
    Elimina múltiples Cancions que coincidan con los filtros.
    """
    filtro = CancionFilter(
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
    if not filtro.to_dict() and not confirm_all:
        raise ValidationException(
            "Sin filtros, esta operación alcanzaría todas las filas. "
            "Añade algún filtro, o confirm_all=true si es lo que quieres.",
            "confirm_all",
        )

    result = await public_async_api.cancion.delete_many(
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

    message = f"{result} Cancions eliminados exitosamente" if result > 0 else "No se encontraron registros que coincidan con los criterios"

    return APIResponse.success(
        data=result,
        message=message
    )

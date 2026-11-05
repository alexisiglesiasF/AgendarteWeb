from fastapi import Query

from api.database.public import public_async_api
from api.routers.database.public._masivos import IngresoUpdateMany
from api.routers.database.public._filtros import con_in_vacio
from api.resources import APIResponse, ValidationException
from .docs import UPDATE_MANY_DESCRIPTION, UPDATE_MANY_RESPONSES, UPDATE_MANY_SUMMARY
from ... import ingreso_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@ingreso_router.patch("",
    response_model=APIResponse[int],
    operation_id="public_ingreso_update_many",
    summary=UPDATE_MANY_SUMMARY,
    description=UPDATE_MANY_DESCRIPTION,
    responses=UPDATE_MANY_RESPONSES
)
async def ingreso_update_many(
    payload: IngresoUpdateMany,
    confirm_all: bool = Query(False, description="Necesario para actualizar sin ningún filtro, es decir, todas las filas a las que alcanza tu acceso. Sin filtros y sin esto, la petición se rechaza."),
    _estricto: None = Depends(estricto("ingreso", "update_many")),
) -> APIResponse[int]:
    """
    Actualiza múltiples Ingresos. `values` solo lleva columnas: un masivo no tiene un
    registro del que colgar escrituras anidadas.
    """
    if not payload.filter.to_dict() and not confirm_all:
        raise ValidationException(
            "Sin filtros, esta operación alcanzaría todas las filas. "
            "Añade algún filtro, o confirm_all=true si es lo que quieres.",
            "confirm_all",
        )
    # Un `in_` con la lista vacía no casa con ninguna fila, y el DAO lo trataría como «sin filtro»:
    # actualizaría todas las que alcanza el usuario. Ninguna fila, sin llamarlo (`_filtros.py`).
    if con_in_vacio(payload.filter.to_dict()) is not None:
        return APIResponse.success(data=0, message="No se encontraron registros que coincidan con los criterios")
    carga = payload.to_dao()

    result = await public_async_api.ingreso.update_many(
        carga,
    )

    message = f"{result} Ingresos actualizados exitosamente" if result > 0 else "No se encontraron registros que coincidan con los criterios"

    return APIResponse.success(
        data=result,
        message=message
    )

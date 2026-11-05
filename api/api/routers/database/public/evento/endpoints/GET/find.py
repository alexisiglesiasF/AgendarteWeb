from fastapi import Query, Path
from typing import Optional, List

from api.database.public import public_async_api, EventoRead
from api.resources import APIResponse, RecordNotFoundException
from .docs import FIND_RESPONSES, FIND_SUMMARY, FIND_DESCRIPTION
from ... import evento_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@evento_router.get("/{id:int}",
    response_model=APIResponse[EventoRead],
    response_description="Registro único de evento obtenido exitosamente",
    operation_id="public_evento_find",
    summary=FIND_SUMMARY,
    description=FIND_DESCRIPTION,
    responses=FIND_RESPONSES
)
async def evento_find(
    id: int = Path(..., description="Campo id de la tabla evento"),
    includes: List[str] = Query(None, description="Lista de relaciones a incluir en la respuesta para obtener datos relacionados. Especifica los nombres de las relaciones que deseas expandir"),
    _estricto: None = Depends(estricto("evento", "find")),
) -> APIResponse[EventoRead]:

    result = await public_async_api.evento.find(
        id=id,
        includes=includes,
    )

    if result is None:
        raise RecordNotFoundException("Evento")

    return APIResponse.success(
        data=result,
        message="Evento obtenido exitosamente"
    )

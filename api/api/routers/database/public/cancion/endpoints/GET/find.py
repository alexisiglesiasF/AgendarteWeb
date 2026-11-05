from fastapi import Query, Path
from typing import Optional, List

from api.database.public import public_async_api, CancionRead
from api.resources import APIResponse, RecordNotFoundException
from .docs import FIND_RESPONSES, FIND_SUMMARY, FIND_DESCRIPTION
from ... import cancion_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@cancion_router.get("/{id:int}",
    response_model=APIResponse[CancionRead],
    response_description="Registro único de cancion obtenido exitosamente",
    operation_id="public_cancion_find",
    summary=FIND_SUMMARY,
    description=FIND_DESCRIPTION,
    responses=FIND_RESPONSES
)
async def cancion_find(
    id: int = Path(..., description="Campo id de la tabla cancion"),
    includes: List[str] = Query(None, description="Lista de relaciones a incluir en la respuesta para obtener datos relacionados. Especifica los nombres de las relaciones que deseas expandir"),
    _estricto: None = Depends(estricto("cancion", "find")),
) -> APIResponse[CancionRead]:

    result = await public_async_api.cancion.find(
        id=id,
        includes=includes,
    )

    if result is None:
        raise RecordNotFoundException("Cancion")

    return APIResponse.success(
        data=result,
        message="Cancion obtenido exitosamente"
    )

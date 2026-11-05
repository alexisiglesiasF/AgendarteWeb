from fastapi import Query, Path
from typing import Optional, List

from api.database.public import public_async_api, RepertorioRead
from api.resources import APIResponse, RecordNotFoundException
from .docs import FIND_RESPONSES, FIND_SUMMARY, FIND_DESCRIPTION
from ... import repertorio_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@repertorio_router.get("/{id:int}",
    response_model=APIResponse[RepertorioRead],
    response_description="Registro único de repertorio obtenido exitosamente",
    operation_id="public_repertorio_find",
    summary=FIND_SUMMARY,
    description=FIND_DESCRIPTION,
    responses=FIND_RESPONSES
)
async def repertorio_find(
    id: int = Path(..., description="Campo id de la tabla repertorio"),
    includes: List[str] = Query(None, description="Lista de relaciones a incluir en la respuesta para obtener datos relacionados. Especifica los nombres de las relaciones que deseas expandir"),
    _estricto: None = Depends(estricto("repertorio", "find")),
) -> APIResponse[RepertorioRead]:

    result = await public_async_api.repertorio.find(
        id=id,
        includes=includes,
    )

    if result is None:
        raise RecordNotFoundException("Repertorio")

    return APIResponse.success(
        data=result,
        message="Repertorio obtenido exitosamente"
    )

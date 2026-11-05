from fastapi import Query, Path
from typing import Optional, List

from api.database.public import public_async_api, GastoRead
from api.resources import APIResponse, RecordNotFoundException
from .docs import FIND_RESPONSES, FIND_SUMMARY, FIND_DESCRIPTION
from ... import gasto_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@gasto_router.get("/{id:int}",
    response_model=APIResponse[GastoRead],
    response_description="Registro único de gasto obtenido exitosamente",
    operation_id="public_gasto_find",
    summary=FIND_SUMMARY,
    description=FIND_DESCRIPTION,
    responses=FIND_RESPONSES
)
async def gasto_find(
    id: int = Path(..., description="Campo id de la tabla gasto"),
    includes: List[str] = Query(None, description="Lista de relaciones a incluir en la respuesta para obtener datos relacionados. Especifica los nombres de las relaciones que deseas expandir"),
    _estricto: None = Depends(estricto("gasto", "find")),
) -> APIResponse[GastoRead]:

    result = await public_async_api.gasto.find(
        id=id,
        includes=includes,
    )

    if result is None:
        raise RecordNotFoundException("Gasto")

    return APIResponse.success(
        data=result,
        message="Gasto obtenido exitosamente"
    )

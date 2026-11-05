from fastapi import Query, Path
from typing import Optional, List

from api.database.public import public_async_api, IngresoRead
from api.resources import APIResponse, RecordNotFoundException
from .docs import FIND_RESPONSES, FIND_SUMMARY, FIND_DESCRIPTION
from ... import ingreso_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@ingreso_router.get("/{id:int}",
    response_model=APIResponse[IngresoRead],
    response_description="Registro único de ingreso obtenido exitosamente",
    operation_id="public_ingreso_find",
    summary=FIND_SUMMARY,
    description=FIND_DESCRIPTION,
    responses=FIND_RESPONSES
)
async def ingreso_find(
    id: int = Path(..., description="Campo id de la tabla ingreso"),
    includes: List[str] = Query(None, description="Lista de relaciones a incluir en la respuesta para obtener datos relacionados. Especifica los nombres de las relaciones que deseas expandir"),
    _estricto: None = Depends(estricto("ingreso", "find")),
) -> APIResponse[IngresoRead]:

    result = await public_async_api.ingreso.find(
        id=id,
        includes=includes,
    )

    if result is None:
        raise RecordNotFoundException("Ingreso")

    return APIResponse.success(
        data=result,
        message="Ingreso obtenido exitosamente"
    )

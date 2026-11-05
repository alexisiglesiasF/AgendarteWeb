from fastapi import Query, Path
from typing import Optional, List

from api.database.public import public_async_api, ProyectoRead
from api.resources import APIResponse, RecordNotFoundException
from .docs import FIND_RESPONSES, FIND_SUMMARY, FIND_DESCRIPTION
from ... import proyecto_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@proyecto_router.get("/{id:int}",
    response_model=APIResponse[ProyectoRead],
    response_description="Registro único de proyecto obtenido exitosamente",
    operation_id="public_proyecto_find",
    summary=FIND_SUMMARY,
    description=FIND_DESCRIPTION,
    responses=FIND_RESPONSES
)
async def proyecto_find(
    id: int = Path(..., description="Campo id de la tabla proyecto"),
    includes: List[str] = Query(None, description="Lista de relaciones a incluir en la respuesta para obtener datos relacionados. Especifica los nombres de las relaciones que deseas expandir"),
    _estricto: None = Depends(estricto("proyecto", "find")),
) -> APIResponse[ProyectoRead]:

    result = await public_async_api.proyecto.find(
        id=id,
        includes=includes,
    )

    if result is None:
        raise RecordNotFoundException("Proyecto")

    return APIResponse.success(
        data=result,
        message="Proyecto obtenido exitosamente"
    )

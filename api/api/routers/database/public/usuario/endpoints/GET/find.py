from fastapi import Query, Path
from typing import Optional, List

from api.database.public import public_async_api, UsuarioRead
from api.resources import APIResponse, RecordNotFoundException
from .docs import FIND_RESPONSES, FIND_SUMMARY, FIND_DESCRIPTION
from ... import usuario_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@usuario_router.get("/{id:int}",
    response_model=APIResponse[UsuarioRead],
    response_description="Registro único de usuario obtenido exitosamente",
    operation_id="public_usuario_find",
    summary=FIND_SUMMARY,
    description=FIND_DESCRIPTION,
    responses=FIND_RESPONSES
)
async def usuario_find(
    id: int = Path(..., description="Campo id de la tabla usuario"),
    includes: List[str] = Query(None, description="Lista de relaciones a incluir en la respuesta para obtener datos relacionados. Especifica los nombres de las relaciones que deseas expandir"),
    _estricto: None = Depends(estricto("usuario", "find")),
) -> APIResponse[UsuarioRead]:

    result = await public_async_api.usuario.find(
        id=id,
        includes=includes,
    )

    if result is None:
        raise RecordNotFoundException("Usuario")

    return APIResponse.success(
        data=result,
        message="Usuario obtenido exitosamente"
    )

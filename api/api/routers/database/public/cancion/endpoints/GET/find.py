from fastapi import Query, Path, Depends
from typing import Optional, List
from api.routers.auth import requires_permissions, build_rls_rules, AccessToken
from api.database.public import username_context
from api.database.public._shared import get_model_by_name

from api.database.public import public_async_api, CancionRead, RLS
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
    token: AccessToken = Depends(requires_permissions("read", "cancion")),
    _estricto: None = Depends(estricto("cancion", "find")),
) -> APIResponse[CancionRead]:
    rls = build_rls_rules(token, "public", get_model_by_name, RLS)

    with username_context(token.preferred_username):
        result = await public_async_api.cancion.find(
            id=id,
            includes=includes,
            rls=rls
        )

        if result is None:
            raise RecordNotFoundException("Cancion")

        return APIResponse.success(
            data=result,
            message="Cancion obtenido exitosamente"
        )

from fastapi import Query, Path, Depends
from typing import Optional, List
from api.routers.auth import requires_permissions, build_rls_rules, AccessToken
from api.database.public import username_context
from api.database.public._shared import get_model_by_name

from api.database.public import public_async_api, EventoRead, RLS
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
    token: AccessToken = Depends(requires_permissions("read", "evento")),
    _estricto: None = Depends(estricto("evento", "find")),
) -> APIResponse[EventoRead]:
    rls = build_rls_rules(token, "public", get_model_by_name, RLS)

    with username_context(token.preferred_username):
        result = await public_async_api.evento.find(
            id=id,
            includes=includes,
            rls=rls
        )

        if result is None:
            raise RecordNotFoundException("Evento")

        return APIResponse.success(
            data=result,
            message="Evento obtenido exitosamente"
        )

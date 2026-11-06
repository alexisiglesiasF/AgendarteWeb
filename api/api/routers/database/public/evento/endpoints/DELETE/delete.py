from fastapi import Path, Depends
from api.routers.auth import requires_permissions, build_rls_rules, AccessToken
from api.database.public import username_context
from api.database.public._shared import get_model_by_name

from api.database.public import public_async_api, RLS
from api.resources import APIResponse, RecordNotFoundException
from .docs import DELETE_RESPONSES, DELETE_SUMMARY
from ... import evento_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@evento_router.delete("/{id:int}",
    response_model=APIResponse[int],
    operation_id="public_evento_delete",
    summary=DELETE_SUMMARY,
    responses=DELETE_RESPONSES
)
async def evento_delete(
    id: int = Path(..., description="Campo id de la tabla evento"),
    token: AccessToken = Depends(requires_permissions("delete", "evento")),
    _estricto: None = Depends(estricto("evento", "delete")),
) -> APIResponse[int]:
    """
    Elimina un Evento por su primary key.
    """
    rls = build_rls_rules(token, "public", get_model_by_name, RLS)

    with username_context(token.preferred_username):
        async with public_async_api.session_manager.get_session() as session:
            # La regla va también al find: si no la alcanza, para este usuario la fila no
            # existe, y el 404 de abajo es la respuesta correcta.
            existing = await public_async_api.evento.find(
                id=id,
                rls=rls,
                session=session,
            )

            if existing is None:
                raise RecordNotFoundException("Evento")

            result = await public_async_api.evento.delete(
                id=id,
                rls=rls,
                session=session,
            )

            if result == 0:
                raise RecordNotFoundException("Evento")

            return APIResponse.success(
                data=result,
                message="Evento eliminado exitosamente"
            )

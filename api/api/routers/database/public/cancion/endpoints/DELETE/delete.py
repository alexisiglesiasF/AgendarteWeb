from fastapi import Path, Depends
from api.routers.auth import requires_permissions, build_rls_rules, AccessToken
from api.database.public import username_context
from api.database.public._shared import get_model_by_name

from api.database.public import public_async_api, RLS
from api.resources import APIResponse, RecordNotFoundException
from .docs import DELETE_RESPONSES, DELETE_SUMMARY
from ... import cancion_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@cancion_router.delete("/{id:int}",
    response_model=APIResponse[int],
    operation_id="public_cancion_delete",
    summary=DELETE_SUMMARY,
    responses=DELETE_RESPONSES
)
async def cancion_delete(
    id: int = Path(..., description="Campo id de la tabla cancion"),
    token: AccessToken = Depends(requires_permissions("delete", "cancion")),
    _estricto: None = Depends(estricto("cancion", "delete")),
) -> APIResponse[int]:
    """
    Elimina un Cancion por su primary key.
    """
    rls = build_rls_rules(token, "public", get_model_by_name, RLS)

    with username_context(token.preferred_username):
        async with public_async_api.session_manager.get_session() as session:
            # La regla va también al find: si no la alcanza, para este usuario la fila no
            # existe, y el 404 de abajo es la respuesta correcta.
            existing = await public_async_api.cancion.find(
                id=id,
                rls=rls,
                session=session,
            )

            if existing is None:
                raise RecordNotFoundException("Cancion")

            result = await public_async_api.cancion.delete(
                id=id,
                rls=rls,
                session=session,
            )

            if result == 0:
                raise RecordNotFoundException("Cancion")

            return APIResponse.success(
                data=result,
                message="Cancion eliminado exitosamente"
            )

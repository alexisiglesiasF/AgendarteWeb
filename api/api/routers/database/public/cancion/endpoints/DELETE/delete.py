from fastapi import Path

from api.database.public import public_async_api
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
    _estricto: None = Depends(estricto("cancion", "delete")),
) -> APIResponse[int]:
    """
    Elimina un Cancion por su primary key.
    """

    async with public_async_api.session_manager.get_session() as session:
        existing = await public_async_api.cancion.find(
            id=id,
            session=session,
        )

        if existing is None:
            raise RecordNotFoundException("Cancion")

        result = await public_async_api.cancion.delete(
            id=id,
            session=session,
        )

        if result == 0:
            raise RecordNotFoundException("Cancion")

        return APIResponse.success(
            data=result,
            message="Cancion eliminado exitosamente"
        )

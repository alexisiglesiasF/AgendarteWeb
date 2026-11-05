from fastapi import Path

from api.database.public import public_async_api
from api.resources import APIResponse, RecordNotFoundException
from .docs import DELETE_RESPONSES, DELETE_SUMMARY
from ... import repertorio_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@repertorio_router.delete("/{id:int}",
    response_model=APIResponse[int],
    operation_id="public_repertorio_delete",
    summary=DELETE_SUMMARY,
    responses=DELETE_RESPONSES
)
async def repertorio_delete(
    id: int = Path(..., description="Campo id de la tabla repertorio"),
    _estricto: None = Depends(estricto("repertorio", "delete")),
) -> APIResponse[int]:
    """
    Elimina un Repertorio por su primary key.
    """

    async with public_async_api.session_manager.get_session() as session:
        existing = await public_async_api.repertorio.find(
            id=id,
            session=session,
        )

        if existing is None:
            raise RecordNotFoundException("Repertorio")

        result = await public_async_api.repertorio.delete(
            id=id,
            session=session,
        )

        if result == 0:
            raise RecordNotFoundException("Repertorio")

        return APIResponse.success(
            data=result,
            message="Repertorio eliminado exitosamente"
        )

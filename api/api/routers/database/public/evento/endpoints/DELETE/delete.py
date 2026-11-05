from fastapi import Path

from api.database.public import public_async_api
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
    _estricto: None = Depends(estricto("evento", "delete")),
) -> APIResponse[int]:
    """
    Elimina un Evento por su primary key.
    """

    async with public_async_api.session_manager.get_session() as session:
        existing = await public_async_api.evento.find(
            id=id,
            session=session,
        )

        if existing is None:
            raise RecordNotFoundException("Evento")

        result = await public_async_api.evento.delete(
            id=id,
            session=session,
        )

        if result == 0:
            raise RecordNotFoundException("Evento")

        return APIResponse.success(
            data=result,
            message="Evento eliminado exitosamente"
        )

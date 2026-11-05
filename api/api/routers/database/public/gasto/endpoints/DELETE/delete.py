from fastapi import Path

from api.database.public import public_async_api
from api.resources import APIResponse, RecordNotFoundException
from .docs import DELETE_RESPONSES, DELETE_SUMMARY
from ... import gasto_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@gasto_router.delete("/{id:int}",
    response_model=APIResponse[int],
    operation_id="public_gasto_delete",
    summary=DELETE_SUMMARY,
    responses=DELETE_RESPONSES
)
async def gasto_delete(
    id: int = Path(..., description="Campo id de la tabla gasto"),
    _estricto: None = Depends(estricto("gasto", "delete")),
) -> APIResponse[int]:
    """
    Elimina un Gasto por su primary key.
    """

    async with public_async_api.session_manager.get_session() as session:
        existing = await public_async_api.gasto.find(
            id=id,
            session=session,
        )

        if existing is None:
            raise RecordNotFoundException("Gasto")

        result = await public_async_api.gasto.delete(
            id=id,
            session=session,
        )

        if result == 0:
            raise RecordNotFoundException("Gasto")

        return APIResponse.success(
            data=result,
            message="Gasto eliminado exitosamente"
        )

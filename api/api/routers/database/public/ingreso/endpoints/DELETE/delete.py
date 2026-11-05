from fastapi import Path

from api.database.public import public_async_api
from api.resources import APIResponse, RecordNotFoundException
from .docs import DELETE_RESPONSES, DELETE_SUMMARY
from ... import ingreso_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@ingreso_router.delete("/{id:int}",
    response_model=APIResponse[int],
    operation_id="public_ingreso_delete",
    summary=DELETE_SUMMARY,
    responses=DELETE_RESPONSES
)
async def ingreso_delete(
    id: int = Path(..., description="Campo id de la tabla ingreso"),
    _estricto: None = Depends(estricto("ingreso", "delete")),
) -> APIResponse[int]:
    """
    Elimina un Ingreso por su primary key.
    """

    async with public_async_api.session_manager.get_session() as session:
        existing = await public_async_api.ingreso.find(
            id=id,
            session=session,
        )

        if existing is None:
            raise RecordNotFoundException("Ingreso")

        result = await public_async_api.ingreso.delete(
            id=id,
            session=session,
        )

        if result == 0:
            raise RecordNotFoundException("Ingreso")

        return APIResponse.success(
            data=result,
            message="Ingreso eliminado exitosamente"
        )

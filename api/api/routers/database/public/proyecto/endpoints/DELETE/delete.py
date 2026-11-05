from fastapi import Path

from api.database.public import public_async_api
from api.resources import APIResponse, RecordNotFoundException
from .docs import DELETE_RESPONSES, DELETE_SUMMARY
from ... import proyecto_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@proyecto_router.delete("/{id:int}",
    response_model=APIResponse[int],
    operation_id="public_proyecto_delete",
    summary=DELETE_SUMMARY,
    responses=DELETE_RESPONSES
)
async def proyecto_delete(
    id: int = Path(..., description="Campo id de la tabla proyecto"),
    _estricto: None = Depends(estricto("proyecto", "delete")),
) -> APIResponse[int]:
    """
    Elimina un Proyecto por su primary key.
    """

    async with public_async_api.session_manager.get_session() as session:
        existing = await public_async_api.proyecto.find(
            id=id,
            session=session,
        )

        if existing is None:
            raise RecordNotFoundException("Proyecto")

        result = await public_async_api.proyecto.delete(
            id=id,
            session=session,
        )

        if result == 0:
            raise RecordNotFoundException("Proyecto")

        return APIResponse.success(
            data=result,
            message="Proyecto eliminado exitosamente"
        )

from fastapi import Path

from api.database.public import public_async_api
from api.resources import APIResponse, RecordNotFoundException
from .docs import DELETE_RESPONSES, DELETE_SUMMARY
from ... import usuario_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@usuario_router.delete("/{id:int}",
    response_model=APIResponse[int],
    operation_id="public_usuario_delete",
    summary=DELETE_SUMMARY,
    responses=DELETE_RESPONSES
)
async def usuario_delete(
    id: int = Path(..., description="Campo id de la tabla usuario"),
    _estricto: None = Depends(estricto("usuario", "delete")),
) -> APIResponse[int]:
    """
    Elimina un Usuario por su primary key.
    """

    async with public_async_api.session_manager.get_session() as session:
        existing = await public_async_api.usuario.find(
            id=id,
            session=session,
        )

        if existing is None:
            raise RecordNotFoundException("Usuario")

        result = await public_async_api.usuario.delete(
            id=id,
            session=session,
        )

        if result == 0:
            raise RecordNotFoundException("Usuario")

        return APIResponse.success(
            data=result,
            message="Usuario eliminado exitosamente"
        )

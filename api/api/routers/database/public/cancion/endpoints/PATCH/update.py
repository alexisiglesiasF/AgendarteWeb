from fastapi import Path, Body, Query, Header, Response
from typing import Optional, List, Union

from api.database.public import public_async_api, CancionRead, CancionUpdateValues
from api.resources import APIResponse, RecordNotFoundException
from .docs import UPDATE_RESPONSES, UPDATE_SUMMARY, UPDATE_DESCRIPTION
from ... import cancion_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto, quiere_representacion

@cancion_router.patch("/{id:int}",
    response_model=APIResponse[Union[CancionRead, int]],
    operation_id="public_cancion_update",
    summary=UPDATE_SUMMARY,
    description=UPDATE_DESCRIPTION,
    responses=UPDATE_RESPONSES
)
async def cancion_update(
    response: Response,
    id: int = Path(..., description="Campo id de la tabla cancion"),
    values: CancionUpdateValues = Body(...),
    includes: List[str] = Query(None, description="Con `Prefer: return=representation`, las relaciones con que se devuelve el registro actualizado. Sin la cabecera no se usa."),
    prefer: Optional[str] = Header(None, description="`return=representation` para recibir en `data` el registro actualizado —leído con `includes` y con tu mismo acceso— en vez de cuántas filas cambiaron."),
    _estricto: None = Depends(estricto("cancion", "update")),
) -> APIResponse[Union[CancionRead, int]]:
    """
    Actualiza un Cancion específico.
    """

    async with public_async_api.session_manager.get_session() as session:
        existing = await public_async_api.cancion.find(
            id=id,
            session=session,
        )

        if existing is None:
            raise RecordNotFoundException("Cancion")

        result = await public_async_api.cancion.update(
            id=id,
            updated_values=values,
            session=session,
        )

        if result == 0:
            raise RecordNotFoundException("Cancion")

        if quiere_representacion(prefer):
            # Releída en la misma transacción: lo que devolvería un GET después.
            cambios = values.to_dict()
            registro = await public_async_api.cancion.find(
                id=cambios.get("id", id),
                includes=includes,
                session=session,
            )
            if registro is not None:
                response.headers["Preference-Applied"] = "return=representation"
                return APIResponse.success(
                    data=registro,
                    message="Cancion actualizado exitosamente"
                )

        return APIResponse.success(
            data=result,
            message="Cancion actualizado exitosamente"
        )

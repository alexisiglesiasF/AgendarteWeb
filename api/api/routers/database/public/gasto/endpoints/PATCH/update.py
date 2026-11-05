from fastapi import Path, Body, Query, Header, Response
from typing import Optional, List, Union

from api.database.public import public_async_api, GastoRead, GastoUpdateValues
from api.resources import APIResponse, RecordNotFoundException
from .docs import UPDATE_RESPONSES, UPDATE_SUMMARY, UPDATE_DESCRIPTION
from ... import gasto_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto, quiere_representacion

@gasto_router.patch("/{id:int}",
    response_model=APIResponse[Union[GastoRead, int]],
    operation_id="public_gasto_update",
    summary=UPDATE_SUMMARY,
    description=UPDATE_DESCRIPTION,
    responses=UPDATE_RESPONSES
)
async def gasto_update(
    response: Response,
    id: int = Path(..., description="Campo id de la tabla gasto"),
    values: GastoUpdateValues = Body(...),
    includes: List[str] = Query(None, description="Con `Prefer: return=representation`, las relaciones con que se devuelve el registro actualizado. Sin la cabecera no se usa."),
    prefer: Optional[str] = Header(None, description="`return=representation` para recibir en `data` el registro actualizado —leído con `includes` y con tu mismo acceso— en vez de cuántas filas cambiaron."),
    _estricto: None = Depends(estricto("gasto", "update")),
) -> APIResponse[Union[GastoRead, int]]:
    """
    Actualiza un Gasto específico.
    """

    async with public_async_api.session_manager.get_session() as session:
        existing = await public_async_api.gasto.find(
            id=id,
            session=session,
        )

        if existing is None:
            raise RecordNotFoundException("Gasto")

        result = await public_async_api.gasto.update(
            id=id,
            updated_values=values,
            session=session,
        )

        if result == 0:
            raise RecordNotFoundException("Gasto")

        if quiere_representacion(prefer):
            # Releída en la misma transacción: lo que devolvería un GET después.
            cambios = values.to_dict()
            registro = await public_async_api.gasto.find(
                id=cambios.get("id", id),
                includes=includes,
                session=session,
            )
            if registro is not None:
                response.headers["Preference-Applied"] = "return=representation"
                return APIResponse.success(
                    data=registro,
                    message="Gasto actualizado exitosamente"
                )

        return APIResponse.success(
            data=result,
            message="Gasto actualizado exitosamente"
        )

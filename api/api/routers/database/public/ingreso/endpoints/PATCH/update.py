from fastapi import Path, Body, Query, Header, Response
from typing import Optional, List, Union

from api.database.public import public_async_api, IngresoRead, IngresoUpdateValues
from api.resources import APIResponse, RecordNotFoundException
from .docs import UPDATE_RESPONSES, UPDATE_SUMMARY, UPDATE_DESCRIPTION
from ... import ingreso_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto, quiere_representacion

@ingreso_router.patch("/{id:int}",
    response_model=APIResponse[Union[IngresoRead, int]],
    operation_id="public_ingreso_update",
    summary=UPDATE_SUMMARY,
    description=UPDATE_DESCRIPTION,
    responses=UPDATE_RESPONSES
)
async def ingreso_update(
    response: Response,
    id: int = Path(..., description="Campo id de la tabla ingreso"),
    values: IngresoUpdateValues = Body(...),
    includes: List[str] = Query(None, description="Con `Prefer: return=representation`, las relaciones con que se devuelve el registro actualizado. Sin la cabecera no se usa."),
    prefer: Optional[str] = Header(None, description="`return=representation` para recibir en `data` el registro actualizado —leído con `includes` y con tu mismo acceso— en vez de cuántas filas cambiaron."),
    _estricto: None = Depends(estricto("ingreso", "update")),
) -> APIResponse[Union[IngresoRead, int]]:
    """
    Actualiza un Ingreso específico.
    """

    async with public_async_api.session_manager.get_session() as session:
        existing = await public_async_api.ingreso.find(
            id=id,
            session=session,
        )

        if existing is None:
            raise RecordNotFoundException("Ingreso")

        result = await public_async_api.ingreso.update(
            id=id,
            updated_values=values,
            session=session,
        )

        if result == 0:
            raise RecordNotFoundException("Ingreso")

        if quiere_representacion(prefer):
            # Releída en la misma transacción: lo que devolvería un GET después.
            cambios = values.to_dict()
            registro = await public_async_api.ingreso.find(
                id=cambios.get("id", id),
                includes=includes,
                session=session,
            )
            if registro is not None:
                response.headers["Preference-Applied"] = "return=representation"
                return APIResponse.success(
                    data=registro,
                    message="Ingreso actualizado exitosamente"
                )

        return APIResponse.success(
            data=result,
            message="Ingreso actualizado exitosamente"
        )

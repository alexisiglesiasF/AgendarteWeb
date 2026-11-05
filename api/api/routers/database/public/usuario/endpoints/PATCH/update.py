from fastapi import Path, Body, Query, Header, Response
from typing import Optional, List, Union

from api.routers.database.public._anidados import traducir_anidada
from api.database.public import public_async_api, UsuarioRead, UsuarioUpdateValues
from api.resources import APIResponse, RecordNotFoundException
from .docs import UPDATE_RESPONSES, UPDATE_SUMMARY, UPDATE_DESCRIPTION
from ... import usuario_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto, quiere_representacion

@usuario_router.patch("/{id:int}",
    response_model=APIResponse[Union[UsuarioRead, int]],
    operation_id="public_usuario_update",
    summary=UPDATE_SUMMARY,
    description=UPDATE_DESCRIPTION,
    responses=UPDATE_RESPONSES
)
async def usuario_update(
    response: Response,
    id: int = Path(..., description="Campo id de la tabla usuario"),
    values: UsuarioUpdateValues = Body(...),
    includes: List[str] = Query(None, description="Con `Prefer: return=representation`, las relaciones con que se devuelve el registro actualizado. Sin la cabecera no se usa."),
    prefer: Optional[str] = Header(None, description="`return=representation` para recibir en `data` el registro actualizado —leído con `includes` y con tu mismo acceso— en vez de cuántas filas cambiaron."),
    _estricto: None = Depends(estricto("usuario", "update")),
) -> APIResponse[Union[UsuarioRead, int]]:
    """
    Actualiza un Usuario específico.
    """

    async with public_async_api.session_manager.get_session() as session:
        existing = await public_async_api.usuario.find(
            id=id,
            session=session,
        )

        if existing is None:
            raise RecordNotFoundException("Usuario")

        try:
            result = await public_async_api.usuario.update(
                id=id,
                updated_values=values,
                session=session,
            )
        except Exception as error:
            # Lo que el DAO rechaza de las anidadas (tai-sql #218): 404 o 422, no un 500.
            traducir_anidada(error)
            raise

        if result == 0:
            raise RecordNotFoundException("Usuario")

        if quiere_representacion(prefer):
            # Releída en la misma transacción: lo que devolvería un GET después.
            cambios = values.to_dict()
            registro = await public_async_api.usuario.find(
                id=cambios.get("id", id),
                includes=includes,
                session=session,
            )
            if registro is not None:
                response.headers["Preference-Applied"] = "return=representation"
                return APIResponse.success(
                    data=registro,
                    message="Usuario actualizado exitosamente"
                )

        return APIResponse.success(
            data=result,
            message="Usuario actualizado exitosamente"
        )

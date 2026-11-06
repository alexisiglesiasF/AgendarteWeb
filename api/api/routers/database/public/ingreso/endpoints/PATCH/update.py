from fastapi import Path, Body, Query, Header, Response, Depends
from typing import Optional, List, Union
from api.routers.auth import requires_permissions, build_rls_rules, AccessToken
from api.database.public import username_context
from api.database.public._shared import get_model_by_name

from api.routers.auth import build_owner_rules, owner_violation
from api.database.public import public_async_api, IngresoRead, IngresoUpdateValues, RLS
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
    token: AccessToken = Depends(requires_permissions("update", "ingreso")),
    _estricto: None = Depends(estricto("ingreso", "update")),
) -> APIResponse[Union[IngresoRead, int]]:
    """
    Actualiza un Ingreso específico.
    """
    rls = build_rls_rules(token, "public", get_model_by_name, RLS)

    with username_context(token.preferred_username):
        async with public_async_api.session_manager.get_session() as session:
            # La regla va también al find: si no la alcanza, para este usuario la fila no
            # existe, y el 404 de abajo es la respuesta correcta.
            existing = await public_async_api.ingreso.find(
                id=id,
                rls=rls,
                session=session,
            )

            if existing is None:
                raise RecordNotFoundException("Ingreso")

            result = await public_async_api.ingreso.update(
                id=id,
                updated_values=values,
                rls=rls,
                session=session,
            )

            if result == 0:
                raise RecordNotFoundException("Ingreso")
            # La clave, por si el cambio la movió: es con la que hay que volver a leerla.
            cambios = values.to_dict()
            # Lo ajeno ya es un 404 (la regla va en el find). Lo que queda es no sacar la fila
            # de lo del usuario: cambiar su dueño, o moverla a un padre ajeno.
            propias = build_owner_rules(
                token, "public", get_model_by_name, RLS,
                model=get_model_by_name("public.ingreso"),
            )
            if propias:
                if await public_async_api.ingreso.find(
                    id=cambios.get("id", id),
                    rls=propias,
                    session=session,
                ) is None:
                    raise owner_violation()

            if quiere_representacion(prefer):
                # Releída en la misma transacción, con la misma regla que cualquier lectura: lo
                # que devuelve es lo que devolvería un GET de este usuario, hijos recién creados o
                # borrados incluidos.
                registro = await public_async_api.ingreso.find(
                    id=cambios.get("id", id),
                    includes=includes,
                    rls=rls,
                    session=session,
                )
                # Si el cambio la sacó de su alcance (el RLS ya no la ve), no se puede devolver:
                # se ignora la preferencia, como permite el RFC 7240, y va el entero de siempre
                # sin `Preference-Applied`.
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

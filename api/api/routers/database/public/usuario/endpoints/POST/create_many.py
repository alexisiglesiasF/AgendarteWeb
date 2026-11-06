from typing import Annotated, List

from fastapi import Body, Depends
from api.routers.auth import requires_permissions, build_rls_rules, AccessToken
from api.database.public import username_context
from api.database.public._shared import get_model_by_name

from api.routers.database.public._anidados import despues_de_crear_varias, en_create, exigir_permisos, traducir_anidada
from api.database.public import public_async_api, UsuarioRead, UsuarioCreate
from api.resources import APIResponse
from .docs import CREATE_MANY_LIMIT, CREATE_MANY_RESPONSES, CREATE_MANY_SUMMARY, CREATE_MANY_DESCRIPTION
from ... import usuario_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@usuario_router.post("/bulk",
    response_model=APIResponse[List[UsuarioRead]],
    status_code=201,
    operation_id="public_usuario_create_many",
    summary=CREATE_MANY_SUMMARY,
    description=CREATE_MANY_DESCRIPTION,
    responses=CREATE_MANY_RESPONSES
)
async def usuario_create_many(
    registros: Annotated[List[UsuarioCreate], Body(min_length=1, max_length=CREATE_MANY_LIMIT)],
    token: AccessToken = Depends(requires_permissions("create", "usuario")),
    _estricto: None = Depends(estricto("usuario", "create_many")),
) -> APIResponse[List[UsuarioRead]]:
    """
    Crea varios Usuario en una sola transacción: o todos, o ninguno.
    """
    # Lo que cada registro crea en otras tablas pide el permiso de cada una, antes de escribir
    # nada: `field` lleva la posición en la lista (`3.etiquetas.0`).
    for posicion, registro in enumerate(registros):
        exigir_permisos(token, en_create("usuario", registro, f"{posicion}."))
    with username_context(token.preferred_username):
        async with public_async_api.session_manager.get_session() as session:
            try:
                creados = await public_async_api.usuario.create_many(
                    registros,
                    session=session,
                )
            except Exception as error:
                # Lo que el DAO rechaza de las anidadas (tai-sql #218): 404 o 422, no un 500. El
                # `field` es el que dé el DAO: `create_many` no dice de qué registro.
                traducir_anidada(error)
                raise
            # Como en `create`: cada fila tiene que ser del usuario, y lo que se creó anidado con
            # ella también; si una no lo es, la excepción deshace todo el lote. Va en la misma
            # transacción que la escritura, y es una consulta por tabla y nivel para todo el lote,
            # no una por registro (`field` lleva la posición: `3`, `3.etiquetas`).
            await despues_de_crear_varias(token, "usuario", creados, registros, session)

            return APIResponse.success(
                data=creados,
                message=f"{len(creados)} Usuario creados exitosamente"
            )

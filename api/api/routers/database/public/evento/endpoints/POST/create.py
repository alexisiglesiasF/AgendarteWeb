from fastapi import Depends
from api.routers.auth import requires_permissions, build_rls_rules, AccessToken
from api.database.public import username_context
from api.database.public._shared import get_model_by_name

from api.routers.auth import build_owner_rules, owner_violation
from api.routers.database.public._anidados import despues_de_crear, en_create, exigir_permisos, traducir_anidada
from api.database.public import public_async_api, EventoRead, EventoCreate, RLS
from api.resources import APIResponse
from .docs import CREATE_DESCRIPTION, CREATE_RESPONSES, CREATE_SUMMARY
from ... import evento_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@evento_router.post("",
    response_model=APIResponse[EventoRead],
    status_code=201,
    operation_id="public_evento_create",
    summary=CREATE_SUMMARY,
    description=CREATE_DESCRIPTION,
    responses=CREATE_RESPONSES
)
async def evento_create(
    evento: EventoCreate,
    token: AccessToken = Depends(requires_permissions("create", "evento")),
    _estricto: None = Depends(estricto("evento", "create")),
) -> APIResponse[EventoRead]:
    """
    Crea un nuevo Evento.
    """
    # Las reglas de propietario que alcanzan a esta tabla: la fila nueva tiene que ser del
    # usuario. Se comprueba después de insertar, en la misma transacción, así que también vale
    # para una regla que llega por una relación (un mensaje en un chat ajeno) y lo que hayan
    # escrito los triggers se deshace con ella.
    propias = build_owner_rules(
        token, "public", get_model_by_name, RLS,
        model=get_model_by_name("public.evento"),
    )
    # Lo que el cuerpo crea en otras tablas pide el permiso de cada una, antes de escribir nada.
    exigir_permisos(token, en_create("evento", evento))
    with username_context(token.preferred_username):
        async with public_async_api.session_manager.get_session() as session:
            try:
                result = await public_async_api.evento.create(
                    evento,
                    session=session,
                )
            except Exception as error:
                # Lo que el DAO rechaza de las anidadas (tai-sql #218): 404 o 422, no un 500.
                traducir_anidada(error)
                raise
            if propias and await public_async_api.evento.find(
                id=result.id,
                rls=propias,
                session=session,
            ) is None:
                raise owner_violation()
            # Y lo creado anidado, también del usuario: en la misma transacción.
            await despues_de_crear(token, "evento", result, evento, session)

            return APIResponse.success(
                data=result,
                message="Evento creado exitosamente"
            )

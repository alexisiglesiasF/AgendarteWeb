from fastapi import Depends
from api.routers.auth import requires_permissions, build_rls_rules, AccessToken
from api.database.public import username_context
from api.database.public._shared import get_model_by_name

from api.routers.auth import build_owner_rules, owner_violation
from api.routers.database.public._anidados import despues_de_crear, en_create, exigir_permisos, traducir_anidada
from api.database.public import public_async_api, CancionRead, CancionCreate, RLS
from api.resources import APIResponse
from .docs import CREATE_DESCRIPTION, CREATE_RESPONSES, CREATE_SUMMARY
from ... import cancion_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@cancion_router.post("",
    response_model=APIResponse[CancionRead],
    status_code=201,
    operation_id="public_cancion_create",
    summary=CREATE_SUMMARY,
    description=CREATE_DESCRIPTION,
    responses=CREATE_RESPONSES
)
async def cancion_create(
    cancion: CancionCreate,
    token: AccessToken = Depends(requires_permissions("create", "cancion")),
    _estricto: None = Depends(estricto("cancion", "create")),
) -> APIResponse[CancionRead]:
    """
    Crea un nuevo Cancion.
    """
    # Las reglas de propietario que alcanzan a esta tabla: la fila nueva tiene que ser del
    # usuario. Se comprueba después de insertar, en la misma transacción, así que también vale
    # para una regla que llega por una relación (un mensaje en un chat ajeno) y lo que hayan
    # escrito los triggers se deshace con ella.
    propias = build_owner_rules(
        token, "public", get_model_by_name, RLS,
        model=get_model_by_name("public.cancion"),
    )
    # Lo que el cuerpo crea en otras tablas pide el permiso de cada una, antes de escribir nada.
    exigir_permisos(token, en_create("cancion", cancion))
    with username_context(token.preferred_username):
        async with public_async_api.session_manager.get_session() as session:
            try:
                result = await public_async_api.cancion.create(
                    cancion,
                    session=session,
                )
            except Exception as error:
                # Lo que el DAO rechaza de las anidadas (tai-sql #218): 404 o 422, no un 500.
                traducir_anidada(error)
                raise
            if propias and await public_async_api.cancion.find(
                id=result.id,
                rls=propias,
                session=session,
            ) is None:
                raise owner_violation()
            # Y lo creado anidado, también del usuario: en la misma transacción.
            await despues_de_crear(token, "cancion", result, cancion, session)

            return APIResponse.success(
                data=result,
                message="Cancion creado exitosamente"
            )

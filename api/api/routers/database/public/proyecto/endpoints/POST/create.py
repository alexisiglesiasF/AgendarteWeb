from fastapi import Depends
from api.routers.auth import requires_permissions, build_rls_rules, AccessToken
from api.database.public import username_context
from api.database.public._shared import get_model_by_name

from api.routers.auth import build_owner_rules, owner_violation
from api.routers.database.public._anidados import despues_de_crear, en_create, exigir_permisos, traducir_anidada
from api.database.public import public_async_api, ProyectoRead, ProyectoCreate, RLS
from api.resources import APIResponse
from .docs import CREATE_DESCRIPTION, CREATE_RESPONSES, CREATE_SUMMARY
from ... import proyecto_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@proyecto_router.post("",
    response_model=APIResponse[ProyectoRead],
    status_code=201,
    operation_id="public_proyecto_create",
    summary=CREATE_SUMMARY,
    description=CREATE_DESCRIPTION,
    responses=CREATE_RESPONSES
)
async def proyecto_create(
    proyecto: ProyectoCreate,
    token: AccessToken = Depends(requires_permissions("create", "proyecto")),
    _estricto: None = Depends(estricto("proyecto", "create")),
) -> APIResponse[ProyectoRead]:
    """
    Crea un nuevo Proyecto.
    """
    # Las reglas de propietario que alcanzan a esta tabla: la fila nueva tiene que ser del
    # usuario. Se comprueba después de insertar, en la misma transacción, así que también vale
    # para una regla que llega por una relación (un mensaje en un chat ajeno) y lo que hayan
    # escrito los triggers se deshace con ella.
    propias = build_owner_rules(
        token, "public", get_model_by_name, RLS,
        model=get_model_by_name("public.proyecto"),
    )
    # Lo que el cuerpo crea en otras tablas pide el permiso de cada una, antes de escribir nada.
    exigir_permisos(token, en_create("proyecto", proyecto))
    with username_context(token.preferred_username):
        async with public_async_api.session_manager.get_session() as session:
            try:
                result = await public_async_api.proyecto.create(
                    proyecto,
                    session=session,
                )
            except Exception as error:
                # Lo que el DAO rechaza de las anidadas (tai-sql #218): 404 o 422, no un 500.
                traducir_anidada(error)
                raise
            if propias and await public_async_api.proyecto.find(
                id=result.id,
                rls=propias,
                session=session,
            ) is None:
                raise owner_violation()
            # Y lo creado anidado, también del usuario: en la misma transacción.
            await despues_de_crear(token, "proyecto", result, proyecto, session)

            return APIResponse.success(
                data=result,
                message="Proyecto creado exitosamente"
            )

from api.routers.database.public._anidados import traducir_anidada
from api.database.public import public_async_api, EventoRead, EventoCreate
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
    _estricto: None = Depends(estricto("evento", "create")),
) -> APIResponse[EventoRead]:
    """
    Crea un nuevo Evento.
    """
    try:
        result = await public_async_api.evento.create(
            evento,
        )
    except Exception as error:
        # Lo que el DAO rechaza de las anidadas (tai-sql #218): 404 o 422, no un 500.
        traducir_anidada(error)
        raise

    return APIResponse.success(
        data=result,
        message="Evento creado exitosamente"
    )

from api.routers.database.public._anidados import traducir_anidada
from api.database.public import public_async_api, CancionRead, CancionCreate
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
    _estricto: None = Depends(estricto("cancion", "create")),
) -> APIResponse[CancionRead]:
    """
    Crea un nuevo Cancion.
    """
    try:
        result = await public_async_api.cancion.create(
            cancion,
        )
    except Exception as error:
        # Lo que el DAO rechaza de las anidadas (tai-sql #218): 404 o 422, no un 500.
        traducir_anidada(error)
        raise

    return APIResponse.success(
        data=result,
        message="Cancion creado exitosamente"
    )

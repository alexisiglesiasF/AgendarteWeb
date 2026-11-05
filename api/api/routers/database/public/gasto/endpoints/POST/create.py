from api.routers.database.public._anidados import traducir_anidada
from api.database.public import public_async_api, GastoRead, GastoCreate
from api.resources import APIResponse
from .docs import CREATE_DESCRIPTION, CREATE_RESPONSES, CREATE_SUMMARY
from ... import gasto_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@gasto_router.post("",
    response_model=APIResponse[GastoRead],
    status_code=201,
    operation_id="public_gasto_create",
    summary=CREATE_SUMMARY,
    description=CREATE_DESCRIPTION,
    responses=CREATE_RESPONSES
)
async def gasto_create(
    gasto: GastoCreate,
    _estricto: None = Depends(estricto("gasto", "create")),
) -> APIResponse[GastoRead]:
    """
    Crea un nuevo Gasto.
    """
    try:
        result = await public_async_api.gasto.create(
            gasto,
        )
    except Exception as error:
        # Lo que el DAO rechaza de las anidadas (tai-sql #218): 404 o 422, no un 500.
        traducir_anidada(error)
        raise

    return APIResponse.success(
        data=result,
        message="Gasto creado exitosamente"
    )

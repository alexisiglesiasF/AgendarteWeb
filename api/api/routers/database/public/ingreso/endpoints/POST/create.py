from api.routers.database.public._anidados import traducir_anidada
from api.database.public import public_async_api, IngresoRead, IngresoCreate
from api.resources import APIResponse
from .docs import CREATE_DESCRIPTION, CREATE_RESPONSES, CREATE_SUMMARY
from ... import ingreso_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@ingreso_router.post("",
    response_model=APIResponse[IngresoRead],
    status_code=201,
    operation_id="public_ingreso_create",
    summary=CREATE_SUMMARY,
    description=CREATE_DESCRIPTION,
    responses=CREATE_RESPONSES
)
async def ingreso_create(
    ingreso: IngresoCreate,
    _estricto: None = Depends(estricto("ingreso", "create")),
) -> APIResponse[IngresoRead]:
    """
    Crea un nuevo Ingreso.
    """
    try:
        result = await public_async_api.ingreso.create(
            ingreso,
        )
    except Exception as error:
        # Lo que el DAO rechaza de las anidadas (tai-sql #218): 404 o 422, no un 500.
        traducir_anidada(error)
        raise

    return APIResponse.success(
        data=result,
        message="Ingreso creado exitosamente"
    )

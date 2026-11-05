from api.routers.database.public._anidados import traducir_anidada
from api.database.public import public_async_api, RepertorioRead, RepertorioCreate
from api.resources import APIResponse
from .docs import CREATE_DESCRIPTION, CREATE_RESPONSES, CREATE_SUMMARY
from ... import repertorio_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@repertorio_router.post("",
    response_model=APIResponse[RepertorioRead],
    status_code=201,
    operation_id="public_repertorio_create",
    summary=CREATE_SUMMARY,
    description=CREATE_DESCRIPTION,
    responses=CREATE_RESPONSES
)
async def repertorio_create(
    repertorio: RepertorioCreate,
    _estricto: None = Depends(estricto("repertorio", "create")),
) -> APIResponse[RepertorioRead]:
    """
    Crea un nuevo Repertorio.
    """
    try:
        result = await public_async_api.repertorio.create(
            repertorio,
        )
    except Exception as error:
        # Lo que el DAO rechaza de las anidadas (tai-sql #218): 404 o 422, no un 500.
        traducir_anidada(error)
        raise

    return APIResponse.success(
        data=result,
        message="Repertorio creado exitosamente"
    )

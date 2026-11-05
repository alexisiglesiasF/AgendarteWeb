from api.routers.database.public._anidados import traducir_anidada
from api.database.public import public_async_api, ProyectoRead, ProyectoCreate
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
    _estricto: None = Depends(estricto("proyecto", "create")),
) -> APIResponse[ProyectoRead]:
    """
    Crea un nuevo Proyecto.
    """
    try:
        result = await public_async_api.proyecto.create(
            proyecto,
        )
    except Exception as error:
        # Lo que el DAO rechaza de las anidadas (tai-sql #218): 404 o 422, no un 500.
        traducir_anidada(error)
        raise

    return APIResponse.success(
        data=result,
        message="Proyecto creado exitosamente"
    )

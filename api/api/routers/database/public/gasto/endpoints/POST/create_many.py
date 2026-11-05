from typing import Annotated, List

from fastapi import Body
from api.routers.database.public._anidados import traducir_anidada
from api.database.public import public_async_api, GastoRead, GastoCreate
from api.resources import APIResponse
from .docs import CREATE_MANY_LIMIT, CREATE_MANY_RESPONSES, CREATE_MANY_SUMMARY, CREATE_MANY_DESCRIPTION
from ... import gasto_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@gasto_router.post("/bulk",
    response_model=APIResponse[List[GastoRead]],
    status_code=201,
    operation_id="public_gasto_create_many",
    summary=CREATE_MANY_SUMMARY,
    description=CREATE_MANY_DESCRIPTION,
    responses=CREATE_MANY_RESPONSES
)
async def gasto_create_many(
    registros: Annotated[List[GastoCreate], Body(min_length=1, max_length=CREATE_MANY_LIMIT)],
    _estricto: None = Depends(estricto("gasto", "create_many")),
) -> APIResponse[List[GastoRead]]:
    """
    Crea varios Gasto en una sola transacción: o todos, o ninguno.
    """
    # Sin reglas de propietario no hay nada que comprobar después de escribir, así que no hace
    # falta abrir la transacción aquí: `create_many` es atómico por sí mismo.
    try:
        creados = await public_async_api.gasto.create_many(registros)
    except Exception as error:
        # Lo que el DAO rechaza de las anidadas (tai-sql #218): 404 o 422, no un 500.
        traducir_anidada(error)
        raise

    return APIResponse.success(
        data=creados,
        message=f"{len(creados)} Gasto creados exitosamente"
    )

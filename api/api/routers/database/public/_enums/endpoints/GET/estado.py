from typing import List, Literal
from fastapi import Depends
from api.routers.auth import requires_authentication, AccessToken
from api.resources import APIResponse
from .docs import ESTADO_RESPONSES
from ... import enumerations_router

#: Los valores de la enumeración, en el tipo. El endpoint existe para decir qué valores son
#: válidos, y declarado como `List[str]` el OpenAPI —y cualquier cliente que se genere desde
#: él— solo sabía que devolvía cadenas.
Valores = Literal["realizado", "pendiente"]


@enumerations_router.get("/estado",
    response_model=APIResponse[List[Valores]],
    responses=ESTADO_RESPONSES
)
async def get_estado_enumeration(
    token: AccessToken = Depends(requires_authentication()),
) -> APIResponse[List[Valores]]:
    """
    Obtiene los valores de la enumeración estado.

    Exige un token válido, pero ningún permiso concreto: un enumerado describe la API,
    no es el dato de nadie. Antes no exigía nada y era el único endpoint accesible sin
    identidad con la autorización activada.
    """
    return APIResponse.success(
        data=["realizado", "pendiente"],
        message="Enumeración estado obtenida exitosamente"
    )
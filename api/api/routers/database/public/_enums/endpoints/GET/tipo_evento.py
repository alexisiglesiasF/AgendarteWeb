from typing import List, Literal
from api.resources import APIResponse
from .docs import TIPO_EVENTO_RESPONSES
from ... import enumerations_router

#: Los valores de la enumeración, en el tipo. El endpoint existe para decir qué valores son
#: válidos, y declarado como `List[str]` el OpenAPI —y cualquier cliente que se genere desde
#: él— solo sabía que devolvía cadenas.
Valores = Literal["show", "ensayo", "grabacion", "otros"]


@enumerations_router.get("/tipo-evento",
    response_model=APIResponse[List[Valores]],
    responses=TIPO_EVENTO_RESPONSES
)
async def get_tipo_evento_enumeration() -> APIResponse[List[Valores]]:
    """
    Obtiene los valores de la enumeración tipo_evento.
    """
    return APIResponse.success(
        data=["show", "ensayo", "grabacion", "otros"],
        message="Enumeración tipo_evento obtenida exitosamente"
    )
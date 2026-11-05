from fastapi import Query
from typing import Optional, List
from datetime import datetime

from api.database.public import public_async_api, CancionRead
from api.resources import APIResponse, RecordNotFoundException, ValidationException
from .docs import FIND_BY_RESPONSES, FIND_BY_SUMMARY, FIND_BY_DESCRIPTION
from ... import cancion_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

#: Las claves por las que se busca, una por petición.
CLAVES_UNICAS = (
    frozenset({"nombre"}),
)


@cancion_router.get("/find-by",
    response_model=APIResponse[CancionRead],
    response_description="Registro único de cancion obtenido exitosamente",
    operation_id="public_cancion_find_by",
    summary=FIND_BY_SUMMARY,
    description=FIND_BY_DESCRIPTION,
    responses=FIND_BY_RESPONSES
)
async def cancion_find_by(
    nombre: Optional[str] = Query(None, description="De la clave (nombre)"),
    includes: List[str] = Query(None, description="Lista de relaciones a incluir en la respuesta para obtener datos relacionados. Especifica los nombres de las relaciones que deseas expandir"),
    _estricto: None = Depends(estricto("cancion", "find_by")),
) -> APIResponse[CancionRead]:
    dados = {
        "nombre": nombre,
    }
    clave = {nombre: valor for nombre, valor in dados.items() if valor is not None}
    if frozenset(clave) not in CLAVES_UNICAS:
        raise ValidationException(
            "Se busca por una sola clave única, entera: (nombre)"
        )

    result = await public_async_api.cancion.find_by(**clave, includes=includes)

    if result is None:
        raise RecordNotFoundException("Cancion")

    return APIResponse.success(
        data=result,
        message="Cancion obtenido exitosamente"
    )
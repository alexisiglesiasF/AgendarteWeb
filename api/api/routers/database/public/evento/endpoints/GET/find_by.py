from fastapi import Query
from typing import Optional, List
from datetime import datetime, time

from api.database.public import public_async_api, EventoRead
from api.resources import APIResponse, RecordNotFoundException, ValidationException
from .docs import FIND_BY_RESPONSES, FIND_BY_SUMMARY, FIND_BY_DESCRIPTION
from ... import evento_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

#: Las claves por las que se busca, una por petición.
CLAVES_UNICAS = (
    frozenset({"nombre"}),
)


@evento_router.get("/find-by",
    response_model=APIResponse[EventoRead],
    response_description="Registro único de evento obtenido exitosamente",
    operation_id="public_evento_find_by",
    summary=FIND_BY_SUMMARY,
    description=FIND_BY_DESCRIPTION,
    responses=FIND_BY_RESPONSES
)
async def evento_find_by(
    nombre: Optional[str] = Query(None, description="De la clave (nombre)"),
    includes: List[str] = Query(None, description="Lista de relaciones a incluir en la respuesta para obtener datos relacionados. Especifica los nombres de las relaciones que deseas expandir"),
    _estricto: None = Depends(estricto("evento", "find_by")),
) -> APIResponse[EventoRead]:
    dados = {
        "nombre": nombre,
    }
    clave = {nombre: valor for nombre, valor in dados.items() if valor is not None}
    if frozenset(clave) not in CLAVES_UNICAS:
        raise ValidationException(
            "Se busca por una sola clave única, entera: (nombre)"
        )

    result = await public_async_api.evento.find_by(**clave, includes=includes)

    if result is None:
        raise RecordNotFoundException("Evento")

    return APIResponse.success(
        data=result,
        message="Evento obtenido exitosamente"
    )
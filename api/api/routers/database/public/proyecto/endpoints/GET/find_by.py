from fastapi import Query
from typing import Optional, List
from datetime import datetime

from api.database.public import public_async_api, ProyectoRead
from api.resources import APIResponse, RecordNotFoundException, ValidationException
from .docs import FIND_BY_RESPONSES, FIND_BY_SUMMARY, FIND_BY_DESCRIPTION
from ... import proyecto_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

#: Las claves por las que se busca, una por petición.
CLAVES_UNICAS = (
    frozenset({"nombre"}),
)


@proyecto_router.get("/find-by",
    response_model=APIResponse[ProyectoRead],
    response_description="Registro único de proyecto obtenido exitosamente",
    operation_id="public_proyecto_find_by",
    summary=FIND_BY_SUMMARY,
    description=FIND_BY_DESCRIPTION,
    responses=FIND_BY_RESPONSES
)
async def proyecto_find_by(
    nombre: Optional[str] = Query(None, description="De la clave (nombre)"),
    includes: List[str] = Query(None, description="Lista de relaciones a incluir en la respuesta para obtener datos relacionados. Especifica los nombres de las relaciones que deseas expandir"),
    _estricto: None = Depends(estricto("proyecto", "find_by")),
) -> APIResponse[ProyectoRead]:
    dados = {
        "nombre": nombre,
    }
    clave = {nombre: valor for nombre, valor in dados.items() if valor is not None}
    if frozenset(clave) not in CLAVES_UNICAS:
        raise ValidationException(
            "Se busca por una sola clave única, entera: (nombre)"
        )

    result = await public_async_api.proyecto.find_by(**clave, includes=includes)

    if result is None:
        raise RecordNotFoundException("Proyecto")

    return APIResponse.success(
        data=result,
        message="Proyecto obtenido exitosamente"
    )
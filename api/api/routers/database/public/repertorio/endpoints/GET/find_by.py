from fastapi import Query, Depends
from typing import Optional, List
from datetime import datetime
from api.routers.auth import requires_permissions, build_rls_rules, AccessToken
from api.database.public import username_context
from api.database.public._shared import get_model_by_name

from api.database.public import public_async_api, RepertorioRead, RLS
from api.resources import APIResponse, RecordNotFoundException, ValidationException
from .docs import FIND_BY_RESPONSES, FIND_BY_SUMMARY, FIND_BY_DESCRIPTION
from ... import repertorio_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

#: Las claves por las que se busca, una por petición.
CLAVES_UNICAS = (
    frozenset({"nombre"}),
)


@repertorio_router.get("/find-by",
    response_model=APIResponse[RepertorioRead],
    response_description="Registro único de repertorio obtenido exitosamente",
    operation_id="public_repertorio_find_by",
    summary=FIND_BY_SUMMARY,
    description=FIND_BY_DESCRIPTION,
    responses=FIND_BY_RESPONSES
)
async def repertorio_find_by(
    nombre: Optional[str] = Query(None, description="De la clave (nombre)"),
    includes: List[str] = Query(None, description="Lista de relaciones a incluir en la respuesta para obtener datos relacionados. Especifica los nombres de las relaciones que deseas expandir"),
    token: AccessToken = Depends(requires_permissions("read", "repertorio")),
    _estricto: None = Depends(estricto("repertorio", "find_by")),
) -> APIResponse[RepertorioRead]:
    dados = {
        "nombre": nombre,
    }
    clave = {nombre: valor for nombre, valor in dados.items() if valor is not None}
    if frozenset(clave) not in CLAVES_UNICAS:
        raise ValidationException(
            "Se busca por una sola clave única, entera: (nombre)"
        )
    rls = build_rls_rules(token, "public", get_model_by_name, RLS)

    with username_context(token.preferred_username):
        result = await public_async_api.repertorio.find_by(**clave, includes=includes, rls=rls)

    if result is None:
        raise RecordNotFoundException("Repertorio")

    return APIResponse.success(
        data=result,
        message="Repertorio obtenido exitosamente"
    )
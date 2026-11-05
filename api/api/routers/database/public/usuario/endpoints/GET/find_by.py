from fastapi import Query
from typing import Optional, List
from datetime import datetime

from api.database.public import public_async_api, UsuarioRead
from api.resources import APIResponse, RecordNotFoundException, ValidationException
from .docs import FIND_BY_RESPONSES, FIND_BY_SUMMARY, FIND_BY_DESCRIPTION
from ... import usuario_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

#: Las claves por las que se busca, una por petición.
CLAVES_UNICAS = (
    frozenset({"email"}),
)


@usuario_router.get("/find-by",
    response_model=APIResponse[UsuarioRead],
    response_description="Registro único de usuario obtenido exitosamente",
    operation_id="public_usuario_find_by",
    summary=FIND_BY_SUMMARY,
    description=FIND_BY_DESCRIPTION,
    responses=FIND_BY_RESPONSES
)
async def usuario_find_by(
    email: Optional[str] = Query(None, description="De la clave (email)"),
    includes: List[str] = Query(None, description="Lista de relaciones a incluir en la respuesta para obtener datos relacionados. Especifica los nombres de las relaciones que deseas expandir"),
    _estricto: None = Depends(estricto("usuario", "find_by")),
) -> APIResponse[UsuarioRead]:
    dados = {
        "email": email,
    }
    clave = {nombre: valor for nombre, valor in dados.items() if valor is not None}
    if frozenset(clave) not in CLAVES_UNICAS:
        raise ValidationException(
            "Se busca por una sola clave única, entera: (email)"
        )

    result = await public_async_api.usuario.find_by(**clave, includes=includes)

    if result is None:
        raise RecordNotFoundException("Usuario")

    return APIResponse.success(
        data=result,
        message="Usuario obtenido exitosamente"
    )
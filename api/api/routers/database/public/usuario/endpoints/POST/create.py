from api.routers.database.public._anidados import traducir_anidada
from api.database.public import public_async_api, UsuarioRead, UsuarioCreate
from api.resources import APIResponse
from .docs import CREATE_DESCRIPTION, CREATE_RESPONSES, CREATE_SUMMARY
from ... import usuario_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@usuario_router.post("",
    response_model=APIResponse[UsuarioRead],
    status_code=201,
    operation_id="public_usuario_create",
    summary=CREATE_SUMMARY,
    description=CREATE_DESCRIPTION,
    responses=CREATE_RESPONSES
)
async def usuario_create(
    usuario: UsuarioCreate,
    _estricto: None = Depends(estricto("usuario", "create")),
) -> APIResponse[UsuarioRead]:
    """
    Crea un nuevo Usuario.
    """
    try:
        result = await public_async_api.usuario.create(
            usuario,
        )
    except Exception as error:
        # Lo que el DAO rechaza de las anidadas (tai-sql #218): 404 o 422, no un 500.
        traducir_anidada(error)
        raise

    return APIResponse.success(
        data=result,
        message="Usuario creado exitosamente"
    )

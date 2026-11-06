from fastapi import Query, Depends
from api.routers.auth import requires_permissions, build_rls_rules, AccessToken
from api.database.public import username_context
from api.database.public._shared import get_model_by_name

from api.routers.auth import build_owner_rules, owner_locked_columns, owner_violation
from api.database.public import public_async_api, RLS
from api.routers.database.public._masivos import RepertorioUpdateMany
from api.routers.database.public._filtros import con_in_vacio
from api.resources import APIResponse, ValidationException
from .docs import UPDATE_MANY_DESCRIPTION, UPDATE_MANY_RESPONSES, UPDATE_MANY_SUMMARY
from ... import repertorio_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@repertorio_router.patch("",
    response_model=APIResponse[int],
    operation_id="public_repertorio_update_many",
    summary=UPDATE_MANY_SUMMARY,
    description=UPDATE_MANY_DESCRIPTION,
    responses=UPDATE_MANY_RESPONSES
)
async def repertorio_update_many(
    payload: RepertorioUpdateMany,
    confirm_all: bool = Query(False, description="Necesario para actualizar sin ningún filtro, es decir, todas las filas a las que alcanza tu acceso. Sin filtros y sin esto, la petición se rechaza."),
    token: AccessToken = Depends(requires_permissions("update", "repertorio")),
    _estricto: None = Depends(estricto("repertorio", "update_many")),
) -> APIResponse[int]:
    """
    Actualiza múltiples Repertorios. `values` solo lleva columnas: un masivo no tiene un
    registro del que colgar escrituras anidadas.
    """
    if not payload.filter.to_dict() and not confirm_all:
        raise ValidationException(
            "Sin filtros, esta operación alcanzaría todas las filas. "
            "Añade algún filtro, o confirm_all=true si es lo que quieres.",
            "confirm_all",
        )
    # Un `in_` con la lista vacía no casa con ninguna fila, y el DAO lo trataría como «sin filtro»:
    # actualizaría todas las que alcanza el usuario. Ninguna fila, sin llamarlo (`_filtros.py`).
    if con_in_vacio(payload.filter.to_dict()) is not None:
        return APIResponse.success(data=0, message="No se encontraron registros que coincidan con los criterios")
    carga = payload.to_dao()

    rls = build_rls_rules(token, "public", get_model_by_name, RLS)
    # Con una regla de propietario, un update masivo no puede cambiar de quién son las filas: ni
    # la columna del dueño ni, si la regla llega por una relación, las claves foráneas. Fila a
    # fila no se puede comprobar después; para eso está el PATCH por clave primaria.
    modelo = get_model_by_name("public.repertorio")
    bloqueadas = owner_locked_columns(
        build_owner_rules(token, "public", get_model_by_name, RLS, model=modelo), modelo,
    )
    if bloqueadas & set(carga.values.to_dict()):
        raise owner_violation()
    with username_context(token.preferred_username):
        result = await public_async_api.repertorio.update_many(
            carga,
            rls=rls,
        )

        message = f"{result} Repertorios actualizados exitosamente" if result > 0 else "No se encontraron registros que coincidan con los criterios"

        return APIResponse.success(
            data=result,
            message=message
        )

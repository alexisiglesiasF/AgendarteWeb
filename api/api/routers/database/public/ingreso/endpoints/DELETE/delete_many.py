from fastapi import Query, Depends
from typing import Optional, List
from datetime import datetime

from api.routers.auth import requires_permissions, build_rls_rules, AccessToken
from api.database.public import username_context
from api.database.public._shared import get_model_by_name

from api.database.public import public_async_api, IngresoFilter, RLS
from api.resources import APIResponse, ValidationException
from .docs import DELETE_MANY_RESPONSES, DELETE_MANY_SUMMARY
from ... import ingreso_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@ingreso_router.delete("",
    response_model=APIResponse[int],
    response_description="Número de registros de ingreso eliminados",
    operation_id="public_ingreso_delete_many",
    summary=DELETE_MANY_SUMMARY,
    responses=DELETE_MANY_RESPONSES
)
async def ingreso_delete_many(
    in_id: Optional[List[int]] = Query(None, description="Filtrar por múltiples valores de id"),
    id_evento: Optional[int] = Query(None, description="Filtrar por id_evento"),
    in_id_evento: Optional[List[int]] = Query(None, description="Filtrar por múltiples valores de id_evento"),
    nombre: Optional[str] = Query(None, description="Filtrar por nombre. Nombre del ingreso"),
    in_nombre: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de nombre"),
    min_importe: Optional[float] = Query(None, description="Valor mínimo para importe (incluido)"),
    max_importe: Optional[float] = Query(None, description="Valor máximo para importe (incluido)"),
    recibido: Optional[bool] = Query(None, description="Filtrar por recibido. Indica si el ingreso ha sido recibido o no"),
    concepto: Optional[str] = Query(None, description="Filtrar por concepto. Concepto del ingreso"),
    in_concepto: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de concepto"),
    min_created_at: Optional[datetime] = Query(None, description="Valor mínimo para created_at (incluido)"),
    max_created_at: Optional[datetime] = Query(None, description="Valor máximo para created_at (incluido)"),
    in_created_by: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de created_by"),
    min_updated_at: Optional[datetime] = Query(None, description="Valor mínimo para updated_at (incluido)"),
    max_updated_at: Optional[datetime] = Query(None, description="Valor máximo para updated_at (incluido)"),
    in_updated_by: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de updated_by"),
    confirm_all: bool = Query(False, description="Necesario para eliminar sin ningún filtro, es decir, todas las filas a las que alcanza tu acceso. Sin filtros y sin esto, la petición se rechaza."),
    token: AccessToken = Depends(requires_permissions("delete", "ingreso")),
    _estricto: None = Depends(estricto("ingreso", "delete_many")),
) -> APIResponse[int]:
    """
    Elimina múltiples Ingresos que coincidan con los filtros.
    """
    filtro = IngresoFilter(
        in_id=in_id,
        id_evento=id_evento,
        in_id_evento=in_id_evento,
        nombre=nombre,
        in_nombre=in_nombre,
        min_importe=min_importe,
        max_importe=max_importe,
        recibido=recibido,
        concepto=concepto,
        in_concepto=in_concepto,
        min_created_at=min_created_at,
        max_created_at=max_created_at,
        in_created_by=in_created_by,
        min_updated_at=min_updated_at,
        max_updated_at=max_updated_at,
        in_updated_by=in_updated_by,
    )
    if not filtro.to_dict() and not confirm_all:
        raise ValidationException(
            "Sin filtros, esta operación alcanzaría todas las filas. "
            "Añade algún filtro, o confirm_all=true si es lo que quieres.",
            "confirm_all",
        )

    rls = build_rls_rules(token, "public", get_model_by_name, RLS)
    with username_context(token.preferred_username):
        result = await public_async_api.ingreso.delete_many(
            in_id=in_id,
            id_evento=id_evento,
            in_id_evento=in_id_evento,
            nombre=nombre,
            in_nombre=in_nombre,
            min_importe=min_importe,
            max_importe=max_importe,
            recibido=recibido,
            concepto=concepto,
            in_concepto=in_concepto,
            min_created_at=min_created_at,
            max_created_at=max_created_at,
            in_created_by=in_created_by,
            min_updated_at=min_updated_at,
            max_updated_at=max_updated_at,
            in_updated_by=in_updated_by,
            rls=rls,
        )

        message = f"{result} Ingresos eliminados exitosamente" if result > 0 else "No se encontraron registros que coincidan con los criterios"

        return APIResponse.success(
            data=result,
            message=message
        )

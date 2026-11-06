from fastapi.exceptions import RequestValidationError
from fastapi import Query, Path, Depends
from typing import Optional, List
from datetime import datetime

from api.routers.auth import requires_permissions, build_rls_rules, AccessToken
from api.database.public import username_context
from api.database.public._shared import get_model_by_name

from api.database.public import public_async_api, AggRow, RLS
from api.resources import APIResponse
from .docs import MEAN_RESPONSES, MEAN_SUMMARY
from ... import ingreso_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@ingreso_router.get("/{field}/mean",
    response_model=APIResponse[List[AggRow]],
    operation_id="public_ingreso_mean_field",
    summary=MEAN_SUMMARY,
    responses=MEAN_RESPONSES
)
async def ingreso_mean_field(
    field: str = Path(..., description="Nombre del campo numérico para calcular la media"),
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
    token: AccessToken = Depends(requires_permissions("read", "ingreso")),
    _estricto: None = Depends(estricto("ingreso", "mean")),
) -> APIResponse[List[AggRow]]:
    """
    ## Resumen
    Calcula la media (promedio) de un campo numérico específico que coincida con los filtros.

    ## Parámetros
    - **field** (path): Nombre del campo numérico para calcular la media.

    ## Filtros Opcionales
    - **in_id**: Filtrar por múltiples valores de id (OR lógico)
    - **id_evento**: Filtrar por id_evento
    - **in_id_evento**: Filtrar por múltiples valores de id_evento (OR lógico)
    - **nombre**: Filtrar por nombre
    - **in_nombre**: Filtrar por múltiples valores de nombre (OR lógico)
    - **min_importe**: Filtrar por valor mínimo de importe (incluído)
    - **max_importe**: Filtrar por valor máximo de importe (incluído)
    - **recibido**: Filtrar por recibido
    - **concepto**: Filtrar por concepto
    - **in_concepto**: Filtrar por múltiples valores de concepto (OR lógico)
    - **min_created_at**: Filtrar por valor mínimo de created_at (incluído)
    - **max_created_at**: Filtrar por valor máximo de created_at (incluído)
    - **in_created_by**: Filtrar por múltiples valores de created_by (OR lógico)
    - **min_updated_at**: Filtrar por valor mínimo de updated_at (incluído)
    - **max_updated_at**: Filtrar por valor máximo de updated_at (incluído)
    - **in_updated_by**: Filtrar por múltiples valores de updated_by (OR lógico)

    """
    rls = build_rls_rules(token, "public", get_model_by_name, RLS)

    with username_context(token.preferred_username):
        result = await public_async_api.ingreso.mean(
            agg_fields=[field],
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
            rls=rls
        )

        if not result.success:
            raise RequestValidationError([
                {"type": "value_error", "loc": ("path", "field"), "msg": mensaje, "input": field}
                for mensaje in (result.errors or result.warnings or ["La operación no se puede aplicar"])
            ])

        return APIResponse.success(
            data=result.rows,
            message=f"Media de '{field}' calculada exitosamente",
            meta=result.metadata
        )

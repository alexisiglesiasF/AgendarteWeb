from fastapi.exceptions import RequestValidationError
from fastapi import Query, Path, Depends
from typing import Optional, List
from datetime import datetime

from api.routers.auth import requires_permissions, build_rls_rules, AccessToken
from api.database.public import username_context
from api.database.public._shared import get_model_by_name

from api.database.public import public_async_api, AggRow, RLS
from api.resources import APIResponse
from .docs import MIN_RESPONSES, MIN_SUMMARY
from ... import usuario_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@usuario_router.get("/{field}/min",
    response_model=APIResponse[List[AggRow]],
    operation_id="public_usuario_min_field",
    summary=MIN_SUMMARY,
    responses=MIN_RESPONSES
)
async def usuario_min_field(
    field: str = Path(..., description="Nombre del campo para encontrar el valor mínimo"),
    in_id: Optional[List[int]] = Query(None, description="Filtrar por múltiples valores de id"),
    nombre: Optional[str] = Query(None, description="Filtrar por nombre. Nombre visible"),
    in_nombre: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de nombre"),
    apellido: Optional[str] = Query(None, description="Filtrar por apellido. Apellido visible"),
    in_apellido: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de apellido"),
    email: Optional[str] = Query(None, description="Filtrar por email. Campo email de la tabla usuario"),
    in_email: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de email"),
    min_created_at: Optional[datetime] = Query(None, description="Valor mínimo para created_at (incluido)"),
    max_created_at: Optional[datetime] = Query(None, description="Valor máximo para created_at (incluido)"),
    in_created_by: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de created_by"),
    min_updated_at: Optional[datetime] = Query(None, description="Valor mínimo para updated_at (incluido)"),
    max_updated_at: Optional[datetime] = Query(None, description="Valor máximo para updated_at (incluido)"),
    in_updated_by: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de updated_by"),
    token: AccessToken = Depends(requires_permissions("read", "usuario")),
    _estricto: None = Depends(estricto("usuario", "min")),
) -> APIResponse[List[AggRow]]:
    """
    ## Resumen
    Encuentra el valor mínimo de un campo específico que coincida con los filtros.

    ## Parámetros
    - **field** (path): Nombre del campo para encontrar el mínimo.

    ## Filtros Opcionales
    - **in_id**: Filtrar por múltiples valores de id (OR lógico)
    - **nombre**: Filtrar por nombre
    - **in_nombre**: Filtrar por múltiples valores de nombre (OR lógico)
    - **apellido**: Filtrar por apellido
    - **in_apellido**: Filtrar por múltiples valores de apellido (OR lógico)
    - **email**: Filtrar por email
    - **in_email**: Filtrar por múltiples valores de email (OR lógico)
    - **min_created_at**: Filtrar por valor mínimo de created_at (incluído)
    - **max_created_at**: Filtrar por valor máximo de created_at (incluído)
    - **in_created_by**: Filtrar por múltiples valores de created_by (OR lógico)
    - **min_updated_at**: Filtrar por valor mínimo de updated_at (incluído)
    - **max_updated_at**: Filtrar por valor máximo de updated_at (incluído)
    - **in_updated_by**: Filtrar por múltiples valores de updated_by (OR lógico)

    """
    rls = build_rls_rules(token, "public", get_model_by_name, RLS)

    with username_context(token.preferred_username):
        result = await public_async_api.usuario.min(
            agg_fields=[field],
            in_id=in_id,
            nombre=nombre,
            in_nombre=in_nombre,
            apellido=apellido,
            in_apellido=in_apellido,
            email=email,
            in_email=in_email,
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
            message=f"Mínimo de '{field}' calculado exitosamente",
            meta=result.metadata
        )

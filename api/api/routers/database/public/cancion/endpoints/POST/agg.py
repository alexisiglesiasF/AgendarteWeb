from fastapi.exceptions import RequestValidationError
from fastapi import Body, Depends
from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel
from api.routers.auth import requires_permissions, build_rls_rules, AccessToken
from api.database.public import username_context
from api.database.public._shared import get_model_by_name

from api.database.public import public_async_api, CancionFilter, AggRow, AggRequest, RLS
from api.resources import APIResponse
from api.routers.database.public._filtros import sin_filas
from .docs import AGG_RESPONSES, AGG_SUMMARY, AGG_DESCRIPTION
from ... import cancion_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

class AggregationPayload(BaseModel):
    operations: AggRequest
    filters: Optional[CancionFilter] = None

@cancion_router.post("/agg",
    response_model=APIResponse[List[AggRow]],
    operation_id="public_cancion_aggregate",
    summary=AGG_SUMMARY,
    description=AGG_DESCRIPTION,
    responses=AGG_RESPONSES
)
async def cancion_aggregate(
    payload: AggregationPayload = Body(..., openapi_examples={"ejemplo": {"summary": "Agregar y agrupar", "value": {"operations": {"aggregations": {"count": ["id"], "max": ["created_at"], "min": ["created_at"]}, "group_by": ["nombre"]}, "filters": {"nombre": "valor"}}}}),
    token: AccessToken = Depends(requires_permissions("read", "cancion")),
    _estricto: None = Depends(estricto("cancion", "agg")),
) -> APIResponse[List[AggRow]]:
    """
    Realiza múltiples operaciones de agregación en una sola consulta sobre la tabla cancion.
    """
    # `filters` está declarado opcional y se usaba sin comprobarlo: agregar sin filtrar
    # —el uso más común del endpoint— moría con un AttributeError y salía como un 500.
    filtros = payload.filters.to_dict() if payload.filters is not None else {}
    rls = build_rls_rules(token, "public", get_model_by_name, RLS)
    with username_context(token.preferred_username):
        result = await public_async_api.cancion.agg(
            request=payload.operations,
            # Un `in_` vacío no casa con nada, y el DAO lo trataría como «sin filtro»: una regla
            # más que no alcanza ninguna fila (`_filtros.py`).
            rls=sin_filas("cancion", filtros, rls),
            **filtros
        )

        if not result.success:
            raise RequestValidationError([
                {"type": "value_error", "loc": ("body", "operations"), "msg": mensaje, "input": None}
                for mensaje in (result.errors or result.warnings or ["La operación no se puede aplicar"])
            ])

        return APIResponse.success(
            data=result.rows,
            message="Agregaciones calculadas exitosamente",
            meta=result.metadata
        )

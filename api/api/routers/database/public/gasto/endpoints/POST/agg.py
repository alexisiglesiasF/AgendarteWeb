from fastapi.exceptions import RequestValidationError
from fastapi import Body
from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel

from api.database.public import public_async_api, GastoFilter, AggRow, AggRequest
from api.resources import APIResponse
from api.routers.database.public._filtros import sin_filas
from .docs import AGG_RESPONSES, AGG_SUMMARY, AGG_DESCRIPTION
from ... import gasto_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

class AggregationPayload(BaseModel):
    operations: AggRequest
    filters: Optional[GastoFilter] = None

@gasto_router.post("/agg",
    response_model=APIResponse[List[AggRow]],
    operation_id="public_gasto_aggregate",
    summary=AGG_SUMMARY,
    description=AGG_DESCRIPTION,
    responses=AGG_RESPONSES
)
async def gasto_aggregate(
    payload: AggregationPayload = Body(..., openapi_examples={"ejemplo": {"summary": "Agregar y agrupar", "value": {"operations": {"aggregations": {"count": ["id"], "sum": ["importe"], "mean": ["importe"], "max": ["created_at"], "min": ["created_at"]}, "group_by": ["nombre"]}, "filters": {"nombre": "valor"}}}}),
    _estricto: None = Depends(estricto("gasto", "agg")),
) -> APIResponse[List[AggRow]]:
    """
    Realiza múltiples operaciones de agregación en una sola consulta sobre la tabla gasto.
    """
    # `filters` está declarado opcional y se usaba sin comprobarlo: agregar sin filtrar
    # —el uso más común del endpoint— moría con un AttributeError y salía como un 500.
    filtros = payload.filters.to_dict() if payload.filters is not None else {}

    result = await public_async_api.gasto.agg(
        request=payload.operations,
        # Un `in_` vacío no casa con nada, y el DAO lo trataría como «sin filtro»: una regla que no
        # alcanza ninguna fila (`_filtros.py`).
        rls=sin_filas("gasto", filtros, None),
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

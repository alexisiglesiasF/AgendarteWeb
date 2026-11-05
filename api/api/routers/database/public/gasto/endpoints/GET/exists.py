from fastapi import Query
from typing import Optional, List
from datetime import datetime


from api.database.public import public_async_api
from api.resources import APIResponse
from .docs import EXISTS_RESPONSES, EXISTS_SUMMARY
from ... import gasto_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@gasto_router.get("/exists",
    response_model=APIResponse[bool],
    operation_id="public_gasto_exists",
    summary=EXISTS_SUMMARY,
    responses=EXISTS_RESPONSES
)
async def gasto_exists(
    in_id: Optional[List[int]] = Query(None, description="Filtrar por múltiples valores de id"),
    id_evento: Optional[int] = Query(None, description="Filtrar por id_evento"),
    in_id_evento: Optional[List[int]] = Query(None, description="Filtrar por múltiples valores de id_evento"),
    nombre: Optional[str] = Query(None, description="Filtrar por nombre. Nombre del gasto"),
    in_nombre: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de nombre"),
    min_importe: Optional[float] = Query(None, description="Valor mínimo para importe (incluido)"),
    max_importe: Optional[float] = Query(None, description="Valor máximo para importe (incluido)"),
    pagado: Optional[bool] = Query(None, description="Filtrar por pagado. Indica si el gasto ha sido pagado o no"),
    concepto: Optional[str] = Query(None, description="Filtrar por concepto. Concepto del gasto"),
    in_concepto: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de concepto"),
    min_created_at: Optional[datetime] = Query(None, description="Valor mínimo para created_at (incluido)"),
    max_created_at: Optional[datetime] = Query(None, description="Valor máximo para created_at (incluido)"),
    in_created_by: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de created_by"),
    min_updated_at: Optional[datetime] = Query(None, description="Valor mínimo para updated_at (incluido)"),
    max_updated_at: Optional[datetime] = Query(None, description="Valor máximo para updated_at (incluido)"),
    in_updated_by: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de updated_by"),
    _estricto: None = Depends(estricto("gasto", "exists")),
) -> APIResponse[bool]:
    """
    Verifica si existe al menos un gasto que coincida con los filtros.
    """
    result = await public_async_api.gasto.exists(
        in_id=in_id,
        id_evento=id_evento,
        in_id_evento=in_id_evento,
        nombre=nombre,
        in_nombre=in_nombre,
        min_importe=min_importe,
        max_importe=max_importe,
        pagado=pagado,
        concepto=concepto,
        in_concepto=in_concepto,
        min_created_at=min_created_at,
        max_created_at=max_created_at,
        in_created_by=in_created_by,
        min_updated_at=min_updated_at,
        max_updated_at=max_updated_at,
        in_updated_by=in_updated_by,
    )

    return APIResponse.success(
        data=result,
        message="Verificación realizada exitosamente"
    )

from fastapi import Query, Depends
from typing import Optional, List, Literal
from datetime import datetime
from api.routers.auth import requires_permissions, build_rls_rules, AccessToken
from api.database.public import username_context
from api.database.public._shared import get_model_by_name

from api.database.public import public_async_api, RepertorioRead, RLS
from api.resources import APIResponse, PaginatedResponse
from .docs import FIND_MANY_RESPONSES, FIND_MANY_SUMMARY, FIND_MANY_DESCRIPTION
from ... import repertorio_router
from fastapi import Depends
from api.routers.database.public._cabeceras import estricto

@repertorio_router.get("",
    response_model=APIResponse[List[RepertorioRead]],
    response_description="Lista de registros de repertorio obtenido exitosamente",
    operation_id="public_repertorio_find_many",
    summary=FIND_MANY_SUMMARY,
    description=FIND_MANY_DESCRIPTION,
    responses=FIND_MANY_RESPONSES
)
async def repertorio_find_many(
    limit: Optional[int] = Query(None, description="Número de registros a retornar.", gt=0),
    order_by: List[str] = Query(None, description="Lista de nombres de columnas para ordenar los resultados. Si no existen serán omitidas."),
    order: Optional[Literal["ASC", "DESC"]] = Query("ASC", description="Dirección de ordenamiento: 'ASC' para ascendente (por defecto), 'DESC' para descendente. Solo aplica si order_by está definido", pattern="^(ASC|DESC)$"),
    offset: Optional[int] = Query(None, description="Número de registros a omitir desde el inicio. Útil para paginación. Debe ser un valor no negativo", ge=0),
    in_id: Optional[List[int]] = Query(None, description="Filtrar por múltiples valores de id"),
    usuario_id: Optional[int] = Query(None, description="Filtrar por usuario_id"),
    in_usuario_id: Optional[List[int]] = Query(None, description="Filtrar por múltiples valores de usuario_id"),
    id_proyecto: Optional[int] = Query(None, description="Filtrar por id_proyecto"),
    in_id_proyecto: Optional[List[int]] = Query(None, description="Filtrar por múltiples valores de id_proyecto"),
    nombre: Optional[str] = Query(None, description="Filtrar por nombre. Nombre del repertorio"),
    in_nombre: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de nombre"),
    descripcion: Optional[str] = Query(None, description="Filtrar por descripcion. Descripción del repertorio"),
    in_descripcion: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de descripcion"),
    min_created_at: Optional[datetime] = Query(None, description="Valor mínimo para created_at (incluido)"),
    max_created_at: Optional[datetime] = Query(None, description="Valor máximo para created_at (incluido)"),
    in_created_by: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de created_by"),
    min_updated_at: Optional[datetime] = Query(None, description="Valor mínimo para updated_at (incluido)"),
    max_updated_at: Optional[datetime] = Query(None, description="Valor máximo para updated_at (incluido)"),
    in_updated_by: Optional[List[str]] = Query(None, description="Filtrar por múltiples valores de updated_by"),
    includes: List[str] = Query(None, description="Lista de relaciones a incluir en la respuesta para obtener datos relacionados. Especifica los nombres de las relaciones que deseas expandir"),
    token: AccessToken = Depends(requires_permissions("read", "repertorio")),
    _estricto: None = Depends(estricto("repertorio", "find_many")),
) -> APIResponse[List[RepertorioRead]]:
    rls = build_rls_rules(token, "public", get_model_by_name, RLS)

    with username_context(token.preferred_username):
        # La página y su total, en una sola transacción. Cada llamada al DAO abre la suya
        # si no se le pasa ninguna: eran dos conexiones, dos BEGIN/COMMIT y dos pings del
        # pool para responder una petición, y además el total se leía en otro instante que
        # las filas, así que una escritura concurrente devolvía una respuesta que no
        # cuadraba consigo misma.
        async with public_async_api.session_manager.get_session() as session:
            result = await public_async_api.repertorio.find_many(
                limit=limit,
                offset=offset,
                order_by=order_by,
                order=order,
                in_id=in_id,
                usuario_id=usuario_id,
                in_usuario_id=in_usuario_id,
                id_proyecto=id_proyecto,
                in_id_proyecto=in_id_proyecto,
                nombre=nombre,
                in_nombre=in_nombre,
                descripcion=descripcion,
                in_descripcion=in_descripcion,
                min_created_at=min_created_at,
                max_created_at=max_created_at,
                in_created_by=in_created_by,
                min_updated_at=min_updated_at,
                max_updated_at=max_updated_at,
                in_updated_by=in_updated_by,
                includes=includes,
                rls=rls,
                session=session
            )

            total = None
            if limit is not None or offset is not None:
                # Sin `try`: cuenta con los mismos filtros y la misma sesión que la
                # consulta que acaba de funcionar, así que un fallo aquí es un fallo de
                # verdad. Taparlo devolvía un `total` nulo como si fuera normal — y ahora
                # además dejaría la transacción abortada para el commit de salida.
                total = await public_async_api.repertorio.count(
                    in_id=in_id,
                    usuario_id=usuario_id,
                    in_usuario_id=in_usuario_id,
                    id_proyecto=id_proyecto,
                    in_id_proyecto=in_id_proyecto,
                    nombre=nombre,
                    in_nombre=in_nombre,
                    descripcion=descripcion,
                    in_descripcion=in_descripcion,
                    min_created_at=min_created_at,
                    max_created_at=max_created_at,
                    in_created_by=in_created_by,
                    min_updated_at=min_updated_at,
                    max_updated_at=max_updated_at,
                    in_updated_by=in_updated_by,
                    rls=rls,
                    session=session
                )

            return PaginatedResponse.success_paginated(
                data=result,
                total=total,
                limit=limit,
                offset=offset,
                message=f"Repertorios obtenidos exitosamente"
            )

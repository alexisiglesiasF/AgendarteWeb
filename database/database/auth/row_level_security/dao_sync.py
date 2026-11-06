# Este archivo ha sido generado automáticamente por tai-sql
# No modifiques este archivo directamente

from __future__ import annotations
from typing import (
    List,
    Optional,
    Dict,
    Union,
    Literal,
    Any,
    TYPE_CHECKING,
)
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import (
    select,
    update,
    delete,
    func,
    text,
    literal_column,
    or_,
    and_,
)
from .model import RowLevelSecurity
from .dtos import *
from .._shared import (
    sync_error_handler,
    get_loading_options,
    get_included_relations,
    get_username,
    RLSQueryApplicator,
    ExpressionParser,
    RLS,
    _log_tx,
    _log_commit,
    AGG_OPERATIONS,
    agg_field_error,
    agg_expression_error,
    agg_value,
    OPERATION_FUNCTIONS,
    GROUP_BY_FORBIDDEN_TYPES,
    GROUP_BY_DATETIME_TYPES,
    AggregationResult,
    AggRow,
    AggRequest,
    AggField,
    GroupByField
)
from .._session import sync_session_manager
from tai_alphi import Alphi

if TYPE_CHECKING:
    from pandas import DataFrame  # type: ignore[import-untyped]

# Logger
logger = Alphi.get_logger_by_name("tai-sql")


# Qué agregaciones admite cada columna, {columna: (tipo, operaciones)}. Sale del tipo del
# schema: el SQLAlchemy no distingue un enumerado ni una columna cifrada de un texto. Lo
# que no está aquí no se agrega, y pedirlo es un error con su motivo (`agg_field_error`).
_AGG_COLUMNS = {
    'id': ('bigint', ('count', 'sum', 'mean', 'max', 'min')),
    'realm_id': ('bigint', ('count', 'sum', 'mean', 'max', 'min')),
    'schema_name': ('str', ('count', 'max', 'min')),
    'table_name': ('str', ('count', 'max', 'min')),
    'column_name': ('str', ('count', 'max', 'min')),
    'created_at': ('datetime', ('count', 'max', 'min')),
    'created_by': ('str', ('count', 'max', 'min')),
    'updated_at': ('datetime', ('count', 'max', 'min')),
    'updated_by': ('str', ('count', 'max', 'min')),
}


class RowLevelSecuritySyncDAO:
    """
    DAO síncrono de acceso a datos para el modelo ``RowLevelSecurity``.

    Encapsula la lógica de persistencia del esquema ``auth``,
    exponiendo una API tipada y completa sobre SQLAlchemy síncrono.
    Soporta sesión automática (commit/rollback gestionados internamente)
    y sesión compartida para agrupar operaciones en una misma transacción.

    Gestión de sesiones:
        - ``session=None``      → sesión automática: se abre, se hace commit
          y se cierra en cada llamada. Errores hacen rollback automáticamente.
        - ``session=<Session>`` → sesión compartida: la operación participa en
          la transacción del llamador (ej. dentro de un bloque
          ``with session_manager.transaction() as session``).

    Características:
        - Carga eager declarativa de relaciones mediante ``includes``
        - Row Level Security integrado mediante ``rls``
        - Hooks de trigger antes/después de cada escritura (create/update/delete)
        - Motor de agregaciones multi-operación con GROUP BY opcional
        - Integración nativa con pandas DataFrames
        - Upsert nativo para PostgreSQL, SQLite y MySQL con fallback automático

    Attributes:
        session_manager (SyncSessionManager):
            Fuente de todas las sesiones síncronas de este DAO.
        _df_validator (RowLevelSecurityDataFrameValidator):
            Validador y normalizador de DataFrames para carga masiva.

    Métodos de lectura:
        find(*pk_fields, includes, rls, session) → Optional[RowLevelSecurityRead]:
            Busca un registro por su clave primaria. Acepta ``includes`` para
            carga eager de relaciones anidadas (ej. ``["autor", "autor.perfil"]``)
            y ``rls`` para filtros de seguridad por fila. Retorna ``None`` si
            el registro no existe.

        find_many(limit, offset, order_by, order, *filters, includes, rls, session)
                → List[RowLevelSecurityRead]:
            Lista registros con filtros opcionales, paginación (``limit``,
            ``offset``) y ordenamiento multi-columna (``order_by``, ``order``).
            Admite ``includes`` para relaciones y ``rls`` para seguridad.

        count(*filters, session) → int:
            Cuenta registros que satisfacen los filtros. Útil para obtener
            totales sin cargar los datos completos.

        exists(*filters, session) → bool:
            Devuelve ``True`` si existe al menos un registro coincidente.
            Internamente delega en ``count``.

    Métodos de escritura:
        create(row_level_security, *operative_fields, session) → RowLevelSecurityRead:
            Inserta un registro ejecutando ``_on_create_before`` antes del
            ``flush`` y ``_on_create_after`` después. Retorna el DTO del
            registro con los valores generados por la BD (IDs, timestamps...).

        create_many(records, *operative_fields, session) → List[Read]:
            Inserción masiva con hooks de trigger por instancia.
            Retorna los DTO de los registros creados, en el mismo orden, con
            los valores que haya generado la BD — como ``create``.

        update(*pk_fields, updated_values, *operative_fields, session) → int:
            Actualiza un registro por PK ejecutando ``_on_update_before/after``.
            Soporta actualización en cascada de las relaciones anidadas cuyo
            destino es el dependiente —one-to-many y one-to-one implícita—
            mediante el payload ``updated_values`` (create / update / delete):
            en lista para la one-to-many y en singular para la one-to-one.
            Retorna ``1`` si fue actualizado, ``0`` si no se encontró.

        update_many(payload, *operative_fields, session) → int:
            Actualización masiva con filtros. Si el modelo tiene triggers de
            update itera registro a registro; si no, aplica un UPDATE masivo.
            Retorna el número de registros actualizados.

        delete(*pk_fields, *operative_fields, session) → int:
            Elimina un registro por PK ejecutando ``_on_delete_before/after``.
            Retorna ``1`` si fue eliminado, ``0`` si no se encontró.

        delete_many(filters_list, *operative_fields, session) → int:
            Eliminación masiva. Con triggers itera registro a registro y
            dispara hooks individuales; sin triggers aplica DELETE masivo.
            Retorna el número total de registros eliminados.

    Métodos de upsert:
        upsert(row_level_security, match_fields, session) → RowLevelSecurityRead:
            INSERT con ON CONFLICT nativo para PostgreSQL/SQLite/MySQL, o
            fallback SELECT + INSERT/UPDATE para dialectos no soportados.
            ``match_fields`` especifica los campos de coincidencia (por defecto
            PKs no-autoincrement y columnas UNIQUE del modelo).

        upsert_many(records, match_fields, batch_size, session) → int:
            Upsert masivo procesando registros en lotes de ``batch_size``
            (por defecto 1 000). Usa upsert nativo por dialecto o fallback
            bulk. Retorna el número total de registros procesados.

    Métodos de agregación:
        sum(agg_fields, *filters, session) → AggregationResult:
            Suma campos numéricos filtrados. ``result.data`` contiene
            ``{"sum_<campo>": float | None}`` por cada campo solicitado.

        mean(agg_fields, *filters, session) → AggregationResult:
            Media aritmética de campos numéricos filtrados.
            ``result.data`` → ``{"mean_<campo>": float | None}``.

        max(agg_fields, *filters, session) → AggregationResult:
            Valor máximo de campos numéricos, de fecha (ISO 8601) o de texto.
            ``result.data`` → ``{"max_<campo>": float | str | None}``.

        min(agg_fields, *filters, session) → AggregationResult:
            Valor mínimo de campos numéricos, de fecha (ISO 8601) o de texto.
            ``result.data`` → ``{"min_<campo>": float | str | None}``.

        Lo que el tipo de una columna no admite (``_AGG_COLUMNS``) es un error:
        ``success=False``, sin consultar, y ``errors`` dice por qué.

        agg(request, *filters, verbose, session) → AggregationResult:
            Motor de agregaciones multi-operación. Acepta un ``AggRequest``
            con múltiples operaciones (sum, mean, max, min, count),
            expresiones aritméticas mediante ``AggField``, GROUP BY con
            truncado temporal (``GroupByField + DatetimeTrunc``),
            ordenamiento por resultado y límite de grupos.
            ``result.rows: List[AggRow]`` — cada AggRow expone ``group``
            (valores de agrupación) y ``data`` (valores agregados).

    Métodos de DataFrame:
        as_dataframe(limit, offset, *filters) → pandas.DataFrame:
            Equivalente a ``find_many`` devolviendo un ``DataFrame`` de pandas.
            Los tipos de columnas se optimizan automáticamente: enteros a
            ``Int64``, decimales a ``float64``, booleanos a ``boolean``,
            fechas a ``datetime64[ns]`` y cadenas a ``string``.
            Requiere ``pandas`` instalado.

        from_dataframe(df, mode, match_fields, validate_types,
                       ignore_extra_columns, fill_missing_nullable) → int:
            Ingesta un ``DataFrame`` de pandas. ``mode='create'`` inserta todos
            los registros; ``mode='upsert'`` aplica upsert usando ``match_fields``.
            Valida el esquema, normaliza tipos y limpia NaN/None antes de
            insertar. Retorna el número de registros procesados.

    Ejemplos de uso:
        ```python
        from .._shared import AggRequest, AggField, GroupByField, DatetimeTrunc, AggOrderBy

        dao = RowLevelSecuritySyncDAO

        # ── Lectura ───────────────────────────────────────────────────────────
        registro  = dao.find(id=1)
        pagina    = dao.find_many(limit=20, offset=0, order_by=["created_at"], order="DESC")
        total     = dao.count()
        hay_datos = dao.exists()

        # Con carga de relaciones
        registros = dao.find_many(limit=10, includes=["relacion_a", "relacion_a.anidada_b"])

        # ── Escritura ─────────────────────────────────────────────────────────
        nuevo = dao.create(RowLevelSecurityCreate(...))
        dao.update(id=nuevo.id, updated_values=RowLevelSecurityUpdateValues(...))
        dao.delete(id=nuevo.id)

        # Transacción multi-paso (rollback automático ante cualquier error)
        with session_manager.transaction() as session:
            a = dao.create(RowLevelSecurityCreate(...), session=session)
            b = dao.create(RowLevelSecurityCreate(...), session=session)

        # ── Agregaciones ──────────────────────────────────────────────────────
        r = dao.sum(agg_fields=["importe"])
        print(r.data)  # {"sum_importe": 1234.56}

        # Multipropósito con GROUP BY mensual y orden descendente
        r = dao.agg(
            AggRequest(
                aggregations={
                    "sum":   [AggField(expr="ingresos - costes", alias="beneficio")],
                    "count": ["id"],
                    "mean":  ["precio"],
                },
                group_by=[GroupByField(field="created_at", trunc=DatetimeTrunc.month)],
                order_by=[AggOrderBy(operation="sum", field="beneficio", direction="desc")],
                limit=12,
            ),
        )
        for fila in r.rows:
            print(fila.group, fila.data)

        # ── DataFrame ─────────────────────────────────────────────────────────
        df = dao.as_dataframe(limit=5000)
        df.to_csv("row_level_security.csv", index=False)

        import pandas as pd
        df_nuevos = pd.read_csv("datos.csv")
        n = dao.from_dataframe(df_nuevos, ignore_extra_columns=True)
        print(f"{n} registros procesados")
        ```
    """

    _df_validator = RowLevelSecurityDataFrameValidator()

    # =================== Trigger Hooks ===================

    @classmethod
    def _on_create_before(cls, new_row_level_security: RowLevelSecurity, included: List[str], session: Session):
        pass

    @classmethod
    def _on_create_after(cls, new_row_level_security: RowLevelSecurity, included: List[str], session: Session):
        pass

    @classmethod
    def _on_update_before(cls, new_row_level_security: RowLevelSecurity, old_row_level_security: RowLevelSecurityRead, update_data: dict, session: Session):
        pass

    @classmethod
    def _on_update_after(cls, new_row_level_security: RowLevelSecurity, old_row_level_security: RowLevelSecurityRead, update_data: dict, session: Session):
        pass

    @classmethod
    def _on_delete_before(cls, old_row_level_security: RowLevelSecurityRead, session: Session):
        pass

    @classmethod
    def _on_delete_after(cls, old_row_level_security: RowLevelSecurityRead, session: Session):
        pass

    @classmethod
    @sync_error_handler
    def find(
        cls,
        id: int,
        includes: Optional[List[str]] = None,
        rls: Optional[Union[List[RLS], RLS]] = None,
        session: Optional[Session] = None
    ) -> Optional[RowLevelSecurityRead]:
        """
        Busca un único registro por primary key con carga optimizada de relaciones.
        
        Args:
            id: Filtrar por id
            includes: Lista de relaciones a incluir  (formato: 'relation' o 'relation.nested')
            session: Sesión existente (opcional)
            
        Returns:
            Instancia del modelo o None si no se encuentra

        Examples:
            Incluir relación simple

            dao.find(id=1, includes=['author'])
            
            Incluir relaciones anidadas

            dao.find(id=1, includes=['author', 'author.posts'])
            
            Múltiples relaciones

            dao.find(id=1, includes=['author', 'comments', 'tags'])
        """
        _log_tx(session, f"[auth] 🔍 Buscando RowLevelSecurity:")
        _log_tx(session, f"[auth]     id={id}")
        _log_tx(session, f"[auth]     includes={includes}")

        # Construir query base
        query = select(RowLevelSecurity)
        
        query = query.where(RowLevelSecurity.id == id)

        # Aplicar regla RLS (si existe)
        if rls is not None:
            query = RLSQueryApplicator.apply_rls(query, RowLevelSecurity, rls)

        # Aplicar opciones de carga optimizada
        if includes:
            loading_options = get_loading_options(RowLevelSecurity, includes)
            if loading_options:
                query = query.options(*loading_options)


        # Ejecutar query
        def execute_query(session: Session) -> Optional[RowLevelSecurityRead]:
            result = session.execute(query)
            instance = result.scalars().first()
            
            if instance:
                _log_commit(session, f"[auth] ✅ RowLevelSecurity encontrado exitosamente")
                return RowLevelSecurityRead.from_instance(
                    instance,
 
                    includes=includes, 
                    max_depth=5,
                )
            else:
                _log_commit(session, f"[auth] 📭 RowLevelSecurity no encontrado")
                return None

        if session is not None:
            return execute_query(session)
        else:
            with sync_session_manager.get_session() as session:
                return execute_query(session)

    #: Las claves únicas por las que `find_by()` encuentra un registro, además de la primaria.
    _CLAVES_UNICAS = (
        frozenset({"realm_id", "schema_name", "table_name", "column_name"}),
    )

    @classmethod
    @sync_error_handler
    def find_by(
        cls,
        *,
        realm_id: Optional[int] = None,
        schema_name: Optional[str] = None,
        table_name: Optional[str] = None,
        column_name: Optional[str] = None,
        includes: Optional[List[str]] = None,
        rls: Optional[Union[List[RLS], RLS]] = None,
        session: Optional[Session] = None
    ) -> Optional[RowLevelSecurityRead]:
        """
        Busca un único registro por una de sus claves únicas, como `find()` por la primaria.

        Cada llamada busca por **una** clave, con todas sus columnas y solo ellas:

            find_by(realm_id=..., schema_name=..., table_name=..., column_name=...)

        Media clave no: no sería un solo registro.
        Un valor `None` no es un valor de la clave: varios `NULL` no chocan con un `UNIQUE`.

        Args:
            realm_id: De la clave (realm_id, schema_name, table_name, column_name)
            schema_name: De la clave (realm_id, schema_name, table_name, column_name)
            table_name: De la clave (realm_id, schema_name, table_name, column_name)
            column_name: De la clave (realm_id, schema_name, table_name, column_name)
            includes: Lista de relaciones a incluir  (formato: 'relation' o 'relation.nested')
            rls: Reglas de seguridad por fila que se añaden a la búsqueda
            session: Sesión existente (opcional)

        Returns:
            El registro, o None si ninguno tiene esa clave

        Raises:
            ValueError: Si lo dado no es exactamente una clave: (realm_id, schema_name, table_name, column_name)
        """
        valores = {
            'realm_id': realm_id,
            'schema_name': schema_name,
            'table_name': table_name,
            'column_name': column_name,
        }
        dados = {nombre: valor for nombre, valor in valores.items() if valor is not None}
        if frozenset(dados) not in cls._CLAVES_UNICAS:
            raise ValueError(
                "find_by() de RowLevelSecurity busca por una sola clave única, entera y sin valores None: "
                "(realm_id, schema_name, table_name, column_name)"
            )
        _log_tx(session, f"[auth] 🔍 Buscando RowLevelSecurity por {dados}")

        query = select(RowLevelSecurity)
        for nombre, valor in dados.items():
            query = query.where(getattr(RowLevelSecurity, nombre) == valor)

        if rls is not None:
            query = RLSQueryApplicator.apply_rls(query, RowLevelSecurity, rls)

        if includes:
            loading_options = get_loading_options(RowLevelSecurity, includes)
            if loading_options:
                query = query.options(*loading_options)

        def execute_query(session: Session) -> Optional[RowLevelSecurityRead]:
            result = session.execute(query)
            instance = result.scalars().first()
            if instance is None:
                _log_commit(session, f"[auth] 📭 RowLevelSecurity no encontrado")
                return None
            _log_commit(session, f"[auth] ✅ RowLevelSecurity encontrado exitosamente")
            return RowLevelSecurityRead.from_instance(
                instance,
                includes=includes,
                max_depth=5,
            )

        if session is not None:
            return execute_query(session)
        else:
            with sync_session_manager.get_session() as session:
                return execute_query(session)

    @classmethod
    @sync_error_handler
    def find_many(
        cls,
        limit: Optional[int] = None, 
        offset: Optional[int] = None,
        order_by: Optional[List[str]] = None,
        order: Literal["ASC", "DESC"] = "ASC",
        in_id: Optional[List[int]] = None,
        realm_id: Optional[int] = None,
        in_realm_id: Optional[List[int]] = None,
        min_realm_id: Optional[int] = None,
        max_realm_id: Optional[int] = None,
        schema_name: Optional[str] = None,
        in_schema_name: Optional[List[str]] = None,
        table_name: Optional[str] = None,
        in_table_name: Optional[List[str]] = None,
        column_name: Optional[str] = None,
        in_column_name: Optional[List[str]] = None,
        min_created_at: Optional[datetime] = None,
        max_created_at: Optional[datetime] = None,
        created_by: Optional[str] = None,
        in_created_by: Optional[List[str]] = None,
        min_updated_at: Optional[datetime] = None,
        max_updated_at: Optional[datetime] = None,
        updated_by: Optional[str] = None,
        in_updated_by: Optional[List[str]] = None,
        includes: Optional[List[str]] = None,
        rls: Optional[Union[List[RLS], RLS]] = None,
        session: Optional[Session] = None
    ) -> List[RowLevelSecurityRead]:
        """
        Busca múltiples registros, filtrados, con carga optimizada de relaciones.
        
        Args:
        - limit: Límite de registros a retornar
        - offset: Número de registros a saltar
        - order_by: Lista de nombres de columnas para ordenar los resultados
        - order: ASC/DESC (por defecto ASC). Solo se aplica si se especifica order_by.
        - in_id: Filtrar por múltiples valores de id (OR lógico)
        - realm_id: Filtrar por realm_id
        - in_realm_id: Filtrar por múltiples valores de realm_id (OR lógico)
        - min_realm_id: Filtrar por valor mínimo de realm_id (incluído)
        - max_realm_id: Filtrar por valor máximo de realm_id (incluído)
        - schema_name: Filtrar por schema_name
        - in_schema_name: Filtrar por múltiples valores de schema_name (OR lógico)
        - table_name: Filtrar por table_name
        - in_table_name: Filtrar por múltiples valores de table_name (OR lógico)
        - column_name: Filtrar por column_name
        - in_column_name: Filtrar por múltiples valores de column_name (OR lógico)
        - min_created_at: Filtrar por valor mínimo de created_at (incluído)
        - max_created_at: Filtrar por valor máximo de created_at (incluído)
        - created_by: Filtrar por created_by
        - in_created_by: Filtrar por múltiples valores de created_by (OR lógico)
        - min_updated_at: Filtrar por valor mínimo de updated_at (incluído)
        - max_updated_at: Filtrar por valor máximo de updated_at (incluído)
        - updated_by: Filtrar por updated_by
        - in_updated_by: Filtrar por múltiples valores de updated_by (OR lógico)
        
        
        - includes: Lista de relaciones a incluir (formato: 'relation' o 'relation.nested')
        - session: Sesión existente (opcional)
            
        Returns:
            Lista de instancias del modelo

        Examples:
            Búsqueda simple con relaciones

            dao.find_many(limit=10, includes=['author'])
            
            Relaciones anidadas

            dao.find_many(
                ..., 
                includes=['author', 'author.profile', 'comments']
            )
            
            Ordenamiento ascendente por columnas

            dao.find_many(order_by=['created_at', 'name'], order='ASC')
            
            Ordenamiento descendente por columnas

            dao.find_many(order_by=['created_at', 'name'], order='DESC')
            
            Paginación

            # Obtener los primeros 10 registros
            dao.find_many(limit=10)
            
            # Obtener los últimos 5 registros ordenados por fecha
            dao.find_many(limit=5, order_by=['created_at'], order='DESC')
            
            # Paginación con offset
            dao.find_many(limit=10, offset=20)
        """
        _log_tx(session, f"[auth] 🔍 Buscando múltiples RowLevelSecurity:")
        if limit is not None:
            _log_tx(session, f"[auth]     limit={limit}")
        if offset is not None:
            _log_tx(session, f"[auth]     offset={offset}")
        if order_by:
            _log_tx(session, f"[auth]     order_by={order_by}")
            _log_tx(session, f"[auth]     order={order}")
        if includes:
            _log_tx(session, f"[auth]     includes={includes}")

        # Construir query base
        query = select(RowLevelSecurity)
        
        # Aplicar filtros de búsqueda
        _filter = RowLevelSecurityFilter(
            in_id=in_id,
            realm_id=realm_id,
            in_realm_id=in_realm_id,
            min_realm_id=min_realm_id,
            max_realm_id=max_realm_id,
            schema_name=schema_name,
            in_schema_name=in_schema_name,
            table_name=table_name,
            in_table_name=in_table_name,
            column_name=column_name,
            in_column_name=in_column_name,
            min_created_at=min_created_at,
            max_created_at=max_created_at,
            created_by=created_by,
            in_created_by=in_created_by,
            min_updated_at=min_updated_at,
            max_updated_at=max_updated_at,
            updated_by=updated_by,
            in_updated_by=in_updated_by,
        )
        query = _filter.apply_to_query(query)
        filters = _filter.to_dict()



        # Log de parámetros aplicados
        if filters:
            _log_tx(session, f"[auth]     filters={filters}")

        # Aplicar regla RLS (si existe)
        if rls is not None:
            query = RLSQueryApplicator.apply_rls(query, RowLevelSecurity, rls)


        
        # Aplicar opciones de carga optimizada
        if includes:
            loading_options = get_loading_options(RowLevelSecurity, includes)
            if loading_options:
                query = query.options(*loading_options)

        
        # Aplicar ordenamiento
        if order_by:
            for column_name in order_by:
                if hasattr(RowLevelSecurity, column_name):
                    column = getattr(RowLevelSecurity, column_name)
                    if order.upper() == "DESC":
                        query = query.order_by(column.desc())
                    elif order.upper() == "ASC":
                        query = query.order_by(column.asc())
                else:
                    logger.warning(f"[auth] ⚠️ Columna '{column_name}' no existe en modelo RowLevelSecurity, ignorando en order_by")

        # Aplicar límite (solo valores positivos)
        if limit is not None and limit > 0:
            query = query.limit(limit)

        # Aplicar paginación
        if offset is not None:
            query = query.offset(offset)

        # Ejecutar query
        def execute_query(session: Session) -> List[RowLevelSecurityRead]:
            results = session.execute(query)
            instances = results.scalars().all()
            
            _log_commit(session, f"[auth] ✅ Encontrados {len(instances)} registros RowLevelSecurity")

            return [
                RowLevelSecurityRead.from_instance(
                    instance, 
                    includes=includes, 
                    max_depth=5
                ) 
                for instance in instances
            ]
        
        if session is not None:
            return execute_query(session)
        else:
            with sync_session_manager.get_session() as session:
                return execute_query(session)

    @classmethod
    def count(
        cls,
        in_id: Optional[List[int]] = None,
        realm_id: Optional[int] = None,
        in_realm_id: Optional[List[int]] = None,
        min_realm_id: Optional[int] = None,
        max_realm_id: Optional[int] = None,
        schema_name: Optional[str] = None,
        in_schema_name: Optional[List[str]] = None,
        table_name: Optional[str] = None,
        in_table_name: Optional[List[str]] = None,
        column_name: Optional[str] = None,
        in_column_name: Optional[List[str]] = None,
        min_created_at: Optional[datetime] = None,
        max_created_at: Optional[datetime] = None,
        created_by: Optional[str] = None,
        in_created_by: Optional[List[str]] = None,
        min_updated_at: Optional[datetime] = None,
        max_updated_at: Optional[datetime] = None,
        updated_by: Optional[str] = None,
        in_updated_by: Optional[List[str]] = None,
        rls: Optional[Union[List[RLS], RLS]] = None,
        session: Optional[Session] = None
    ) -> int:
        """
        Cuenta registros que coincidan con los filtros.
        
        Args:
        - in_id: Filtrar por múltiples valores de id (OR lógico)
            - realm_id: Filtrar por realm_id
            - in_realm_id: Filtrar por múltiples valores de realm_id (OR lógico)
            - min_realm_id: Filtrar por valor mínimo de realm_id (incluído)
            - max_realm_id: Filtrar por valor máximo de realm_id (incluído)
            - schema_name: Filtrar por schema_name
            - in_schema_name: Filtrar por múltiples valores de schema_name (OR lógico)
            - table_name: Filtrar por table_name
            - in_table_name: Filtrar por múltiples valores de table_name (OR lógico)
            - column_name: Filtrar por column_name
            - in_column_name: Filtrar por múltiples valores de column_name (OR lógico)
            - min_created_at: Filtrar por valor mínimo de created_at (incluído)
            - max_created_at: Filtrar por valor máximo de created_at (incluído)
            - created_by: Filtrar por created_by
            - in_created_by: Filtrar por múltiples valores de created_by (OR lógico)
            - min_updated_at: Filtrar por valor mínimo de updated_at (incluído)
            - max_updated_at: Filtrar por valor máximo de updated_at (incluído)
            - updated_by: Filtrar por updated_by
            - in_updated_by: Filtrar por múltiples valores de updated_by (OR lógico)
        - rls: Reglas de seguridad a aplicar (opcional)
        - session: Sesión existente (opcional)
            
        Returns:
            Número de registros que coinciden con los filtros
        """
        _log_tx(session, f"[auth] 🔢 Contando registros RowLevelSecurity con filtros aplicados")
        
        query = select(func.count()).select_from(RowLevelSecurity)
        
        _filter = RowLevelSecurityFilter(
            in_id=in_id,
            realm_id=realm_id,
            in_realm_id=in_realm_id,
            min_realm_id=min_realm_id,
            max_realm_id=max_realm_id,
            schema_name=schema_name,
            in_schema_name=in_schema_name,
            table_name=table_name,
            in_table_name=in_table_name,
            column_name=column_name,
            in_column_name=in_column_name,
            min_created_at=min_created_at,
            max_created_at=max_created_at,
            created_by=created_by,
            in_created_by=in_created_by,
            min_updated_at=min_updated_at,
            max_updated_at=max_updated_at,
            updated_by=updated_by,
            in_updated_by=in_updated_by,
        )
        query = _filter.apply_to_query(query)
        filters = _filter.to_dict()
        
        # Log de parámetros aplicados
        if filters:
            _log_tx(session, f"[auth]     filters={filters}")

        # Aplicar regla RLS (si existe)
        if rls is not None:
            query = RLSQueryApplicator.apply_rls(query, RowLevelSecurity, rls)

        if session is not None:
            result = session.execute(query)
        else:
            with sync_session_manager.get_session() as session:
                result = session.execute(query)

        count_result = result.scalar() or 0
        _log_commit(session, f"[auth] ✅ Conteo RowLevelSecurity completado: {count_result} registros")
        return count_result

    @classmethod
    @sync_error_handler
    def exists(
        cls,
        in_id: Optional[List[int]] = None,
        realm_id: Optional[int] = None,
        in_realm_id: Optional[List[int]] = None,
        min_realm_id: Optional[int] = None,
        max_realm_id: Optional[int] = None,
        schema_name: Optional[str] = None,
        in_schema_name: Optional[List[str]] = None,
        table_name: Optional[str] = None,
        in_table_name: Optional[List[str]] = None,
        column_name: Optional[str] = None,
        in_column_name: Optional[List[str]] = None,
        min_created_at: Optional[datetime] = None,
        max_created_at: Optional[datetime] = None,
        created_by: Optional[str] = None,
        in_created_by: Optional[List[str]] = None,
        min_updated_at: Optional[datetime] = None,
        max_updated_at: Optional[datetime] = None,
        updated_by: Optional[str] = None,
        in_updated_by: Optional[List[str]] = None,
        rls: Optional[Union[List[RLS], RLS]] = None,
        session: Optional[Session] = None
    ) -> bool:
        """
        Verifica si existe al menos un registro que coincida con los filtros.
        
        Args:
            - in_id: Filtrar por múltiples valores de id (OR lógico)
            - realm_id: Filtrar por realm_id
            - in_realm_id: Filtrar por múltiples valores de realm_id (OR lógico)
            - min_realm_id: Filtrar por valor mínimo de realm_id (incluído)
            - max_realm_id: Filtrar por valor máximo de realm_id (incluído)
            - schema_name: Filtrar por schema_name
            - in_schema_name: Filtrar por múltiples valores de schema_name (OR lógico)
            - table_name: Filtrar por table_name
            - in_table_name: Filtrar por múltiples valores de table_name (OR lógico)
            - column_name: Filtrar por column_name
            - in_column_name: Filtrar por múltiples valores de column_name (OR lógico)
            - min_created_at: Filtrar por valor mínimo de created_at (incluído)
            - max_created_at: Filtrar por valor máximo de created_at (incluído)
            - created_by: Filtrar por created_by
            - in_created_by: Filtrar por múltiples valores de created_by (OR lógico)
            - min_updated_at: Filtrar por valor mínimo de updated_at (incluído)
            - max_updated_at: Filtrar por valor máximo de updated_at (incluído)
            - updated_by: Filtrar por updated_by
            - in_updated_by: Filtrar por múltiples valores de updated_by (OR lógico)
            - rls: Reglas de seguridad a aplicar (opcional)
            - session: Sesión existente (opcional)
            
        Returns:
            True si existe al menos un registro, False en caso contrario
        """
        _log_tx(session, f"[auth] ❓ Verificando existencia de registros RowLevelSecurity")
        records = cls.count(
            in_id=in_id,
            realm_id=realm_id,
            in_realm_id=in_realm_id,
            min_realm_id=min_realm_id,
            max_realm_id=max_realm_id,
            schema_name=schema_name,
            in_schema_name=in_schema_name,
            table_name=table_name,
            in_table_name=in_table_name,
            column_name=column_name,
            in_column_name=in_column_name,
            min_created_at=min_created_at,
            max_created_at=max_created_at,
            created_by=created_by,
            in_created_by=in_created_by,
            min_updated_at=min_updated_at,
            max_updated_at=max_updated_at,
            updated_by=updated_by,
            in_updated_by=in_updated_by,
            rls=rls,
            session=session
        )
        exists_result = records > 0
        _log_commit(session, f"[auth] ✅ Verificación RowLevelSecurity completada: {'existe' if exists_result else 'no existe'}")
        return exists_result
    


    @classmethod
    def as_dataframe(
        cls,
        limit: Optional[int] = None, 
        offset: Optional[int] = None,
        in_id: Optional[List[int]] = None,
        realm_id: Optional[int] = None,
        in_realm_id: Optional[List[int]] = None,
        min_realm_id: Optional[int] = None,
        max_realm_id: Optional[int] = None,
        schema_name: Optional[str] = None,
        in_schema_name: Optional[List[str]] = None,
        table_name: Optional[str] = None,
        in_table_name: Optional[List[str]] = None,
        column_name: Optional[str] = None,
        in_column_name: Optional[List[str]] = None,
        min_created_at: Optional[datetime] = None,
        max_created_at: Optional[datetime] = None,
        created_by: Optional[str] = None,
        in_created_by: Optional[List[str]] = None,
        min_updated_at: Optional[datetime] = None,
        max_updated_at: Optional[datetime] = None,
        updated_by: Optional[str] = None,
        in_updated_by: Optional[List[str]] = None,
    ) -> DataFrame:
        """
        Busca múltiples registros estableciendo filtros y devuelve el resultado como pandas DataFrame.
        
        Args:
            limit: Límite de registros a retornar (positivo para primeros n, negativo para últimos n - requiere order_by)
            offset: Número de registros a saltar
            - in_id: Filtrar por múltiples valores de id (OR lógico)
            - realm_id: Filtrar por realm_id
            - in_realm_id: Filtrar por múltiples valores de realm_id (OR lógico)
            - min_realm_id: Filtrar por valor mínimo de realm_id (incluído)
            - max_realm_id: Filtrar por valor máximo de realm_id (incluído)
            - schema_name: Filtrar por schema_name
            - in_schema_name: Filtrar por múltiples valores de schema_name (OR lógico)
            - table_name: Filtrar por table_name
            - in_table_name: Filtrar por múltiples valores de table_name (OR lógico)
            - column_name: Filtrar por column_name
            - in_column_name: Filtrar por múltiples valores de column_name (OR lógico)
            - min_created_at: Filtrar por valor mínimo de created_at (incluído)
            - max_created_at: Filtrar por valor máximo de created_at (incluído)
            - created_by: Filtrar por created_by
            - in_created_by: Filtrar por múltiples valores de created_by (OR lógico)
            - min_updated_at: Filtrar por valor mínimo de updated_at (incluído)
            - max_updated_at: Filtrar por valor máximo de updated_at (incluído)
            - updated_by: Filtrar por updated_by
            - in_updated_by: Filtrar por múltiples valores de updated_by (OR lógico)
            
        Returns:
            pandas.DataFrame con los registros encontrados
            
        Raises:
            ImportError: Si pandas no está instalado
            
        Example:
            ```python
            
            # Obtener todos los registros como DataFrame
            df = db_api.rowlevelsecurity.as_dataframe()
            
            # Con filtros y límites
            df = db_api.rowlevelsecurity.as_dataframe(
                limit=100,
                id="valor_filtro"
            )
            
            # Análisis de datos
            print(df.describe())
            print(df.head())
            
            # Exportar a CSV
            df.to_csv('rowlevelsecurity_data.csv', index=False)
            ```
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "pandas no está instalado. Para usar find_as_dataframe(), instala pandas:\n"
                "pip install pandas\n"
                "o si usas poetry:\n"
                "poetry add pandas"
            )
        
        # Obtener los registros usando find_many
        records = cls.find_many(
            limit=limit,
            offset=offset,
            in_id=in_id,
            realm_id=realm_id,
            in_realm_id=in_realm_id,
            min_realm_id=min_realm_id,
            max_realm_id=max_realm_id,
            schema_name=schema_name,
            in_schema_name=in_schema_name,
            table_name=table_name,
            in_table_name=in_table_name,
            column_name=column_name,
            in_column_name=in_column_name,
            min_created_at=min_created_at,
            max_created_at=max_created_at,
            created_by=created_by,
            in_created_by=in_created_by,
            min_updated_at=min_updated_at,
            max_updated_at=max_updated_at,
            updated_by=updated_by,
            in_updated_by=in_updated_by,
        )

        # Si no hay registros, devolver DataFrame vacío con las columnas del modelo
        if not records:
            return pd.DataFrame(columns=[
                'id',
                'realm_id',
                'schema_name',
                'table_name',
                'column_name',
                'created_at',
                'created_by',
                'updated_at',
                'updated_by'
            ])

        data = [record.to_dict() for record in records]
        
        # Crear DataFrame
        df = pd.DataFrame(data)
        
        # Optimizar tipos de datos si es posible
        return cls._optimize_dataframe_dtypes(df)

    @classmethod
    def _optimize_dataframe_dtypes(cls, df: DataFrame) -> DataFrame:
        """
        Optimiza los tipos de datos del DataFrame basándose en las columnas del modelo.
        
        Args:
            df: DataFrame a optimizar
            
        Returns:
            DataFrame con tipos de datos optimizados
        """
        try:
            import pandas as pd
        except ImportError:
            # Si pandas no está disponible, devolver el DataFrame tal como está
            return df
        
        if df.empty:
            return df
        
        # Mapeo de tipos SQLAlchemy a tipos pandas optimizados
        type_mapping = {
            'id': 'int64',
            'realm_id': 'int64',
            'schema_name': 'string',
            'table_name': 'string',
            'column_name': 'string',
            'created_at': 'datetime64[ns]',
            'created_by': 'string',
            'updated_at': 'datetime64[ns]',
            'updated_by': 'string'
        }
        
        # Aplicar conversiones de tipo de forma segura
        for column, target_type in type_mapping.items():
            if column in df.columns:
                try:
                    if target_type == 'int64':
                        # Manejar valores nulos en columnas enteras
                        df[column] = pd.to_numeric(df[column], errors='coerce').astype('Int64')
                    elif target_type == 'float64':
                        df[column] = pd.to_numeric(df[column], errors='coerce')
                    elif target_type == 'boolean':
                        df[column] = df[column].astype('boolean')
                    elif target_type == 'datetime64[ns]':
                        df[column] = pd.to_datetime(df[column], errors='coerce')
                    elif target_type == 'string':
                        df[column] = df[column].astype('string')
                    # 'object' se deja como está
                except Exception:
                    # Si falla la conversión, mantener el tipo original
                    continue
        
        return df

    @classmethod
    def from_dataframe(
        cls,
        df: DataFrame,
        mode: Literal['create', 'upsert'] = "upsert",
        match_fields: List[str] = ['realm_id', 'schema_name', 'table_name', 'column_name'],
        validate_types: bool = False,
        ignore_extra_columns: bool = False,
        fill_missing_nullable: bool = True
    ) -> int:
        """
        Ingesta un DataFrame de pandas en la tabla correspondiente.
        
        Realiza validaciones de esquema y tipos de datos antes de la inserción,
        y permite diferentes modos de inserción (create o upsert).
        
        Args:
            df: DataFrame de pandas con los datos a insertar
            mode ('upsert'): Modo de inserción - 'create' o 'upsert'
            validate_types (False): Si True, valida tipos de datos del DataFrame
            ignore_extra_columns (False): Si True, ignora columnas extra del DataFrame
            fill_missing_nullable (True): Si True, llena con None las columnas nullable faltantes
            
        Returns:
            Número de registros creados o actualizados
            
        Raises:
            ImportError: Si pandas no está instalado
            ValueError: Si el DataFrame no cumple con el esquema requerido
            TypeError: Si los tipos de datos no son compatibles
            
        Example:
            ```python
            import pandas as pd
            
            crud = RowLevelSecuritySyncDAO
            
            # Crear DataFrame
            df = pd.DataFrame({
                'id': [1, 2, 3],
                'realm_id': [1, 2, 3],
                'schema_name': ['valor1', 'valor2', 'valor3'],
                'table_name': ['valor1', 'valor2', 'valor3'],
                'column_name': ['valor1', 'valor2', 'valor3'],
                'created_at': [None, None, None],
                'created_by': ['valor1', 'valor2', 'valor3'],
                'updated_at': [None, None, None],
                'updated_by': ['valor1', 'valor2', 'valor3']
            })
            
            # Inserción simple
            records = crud.from_df(df)
            
            # Upsert con validaciones relajadas
            records = crud.from_df(
                df, 
                mode='upsert',
                ignore_extra_columns=True
            )
            ```
        """
        
        if df.empty:
            return []

        # Validar modo
        if mode not in ['create', 'upsert']:
            raise ValueError("mode debe ser 'create' o 'upsert'")
        
        # Realizar validaciones del esquema
        cls._df_validator.validate_dataframe_schema(df, ignore_extra_columns, fill_missing_nullable)
        
        # Validar tipos de datos si se solicita
        if validate_types:
            cls._df_validator.validate_dataframe_types(df)
        
        # Preparar DataFrame para inserción
        cleaned_df = cls._df_validator.prepare_dataframe_for_insertion(df, ignore_extra_columns, fill_missing_nullable)
        
        # Convertir DataFrame a lista de diccionarios
        records_data = cleaned_df.to_dict('records')
        
        # Limpiar valores NaN/None problemáticos
        records_data = cls._df_validator.clean_records_data(records_data)
        
        # Ejecutar inserción según el modo
        if mode == 'create':
            # `create_many` devuelve los registros creados; aquí el contrato es cuántos
            return len(cls.create_many([RowLevelSecurityCreate.from_dict(record) for record in records_data]))
        else:  # upsert
            return cls.upsert_many([RowLevelSecurityCreate.from_dict(record) for record in records_data], match_fields=match_fields)

    @classmethod
    @sync_error_handler
    def create(
        cls, 
        row_level_security: RowLevelSecurityCreate,
        session: Optional[Session] = None
    ) -> RowLevelSecurityRead:
        """
        Crea un nuevo registro.
        
        Args:
            row_level_security: Datos del row_level_security a crear
            session: Sesión existente (opcional)
            
        Returns:
            Instancia del modelo creado
        """
        _log_tx(session, f"[auth] 🆕 Creando nuevo RowLevelSecurity")
        new_instance = row_level_security.to_instance()

        def _execute_create(session: Session):
            included = get_included_relations(new_instance, row_level_security)
            cls._on_create_before(new_instance, included, session)
            session.add(new_instance)
            session.flush()
            cls._on_create_after(new_instance, included, session)
            return RowLevelSecurityRead.from_created_instance(new_instance, included)

        if session is not None:
            data = _execute_create(session)
        else:
            with sync_session_manager.get_session() as session:
                data = _execute_create(session)

        _log_commit(session, f"[auth] ✅ RowLevelSecurity creado exitosamente con id={data.id}")
        return data
    
    @classmethod
    @sync_error_handler
    def create_many(
        cls, 
        records: List[RowLevelSecurityCreate], 
        session: Optional[Session] = None
    ) -> List[RowLevelSecurityRead]:
        """
        Crea múltiples registros en la tabla row_level_security.
        
        Args:
            records: Lista de RowLevelSecurityCreate con los datos de los registros
            session: Sesión existente (opcional)
            
        Returns:
            Los registros creados, en el mismo orden que `records`. Como en `create`: quien
            inserta necesita la fila que ha quedado —su clave autogenerada, sus defaults, lo
            que hayan escrito los triggers—, y contar las filas no se lo da.

        """
        _log_tx(session, f"[auth] 🔢 Creando {len(records)} registros RowLevelSecurity")

        def _execute_create_many(session: Session) -> List[RowLevelSecurityRead]:
            # Cada instancia con sus relaciones incluidas: los triggers de después reciben las de
            # su registro, como en `create`, y no las del último de la lista
            creadas = []
            for record in records:
                instance = record.to_instance()
                included = get_included_relations(instance, record)
                cls._on_create_before(instance, included, session)
                creadas.append((instance, included))
            session.add_all([instance for instance, _ in creadas])
            session.flush()
            for instance, included in creadas:
                cls._on_create_after(instance, included, session)
            # Los DTO se construyen después de los triggers `after`, como en `create`: lo que
            # escriban en la fila tiene que salir en lo que se devuelve
            return [
                RowLevelSecurityRead.from_created_instance(instance, included)
                for instance, included in creadas
            ]

        if session is not None:
            result = _execute_create_many(session)
        else:
            with sync_session_manager.get_session() as session:
                result = _execute_create_many(session)

        _log_commit(session, f"[auth] ✅ {len(result)} registros RowLevelSecurity creados exitosamente")

        return result
    
    @classmethod
    @sync_error_handler
    def update(
        cls, 
        id: int,
        updated_values: RowLevelSecurityUpdateValues,
        rls: Optional[Union[List[RLS], RLS]] = None,
        session: Optional[Session] = None
    ) -> int:
        """
        Actualiza registros que coincidan con los filtros.
        
        Args:
            id: Identificador del registro
            updated_values: Datos a actualizar
            rls: Reglas de seguridad a aplicar. Acotan la operación igual que acotan
                una consulta: lo que la regla no alcanza, no se modifica.
            session: Sesión existente (opcional)
            
        Returns:
            Número de registros actualizados
        """

        update_data = updated_values.to_dict()
        update_data['updated_at'] = datetime.now()
        update_data['updated_by'] = get_username()

        _log_tx(session, f"[auth] 🔄 Actualizando RowLevelSecurity:")
        _log_tx(session, f"[auth]     id={id}")
        _log_tx(session, f"[auth]     valores={updated_values.to_dict()}")

        query = select(RowLevelSecurity)

        query = query.where(RowLevelSecurity.id == id)

        # La regla acota la fila igual que acota una consulta: si no la alcanza, para esta
        # llamada no existe y se devuelve 0, que es lo que un endpoint traduce a un 404.
        query = RLSQueryApplicator.apply_rls(query, RowLevelSecurity, rls)

        def _execute_update(session: Session) -> int:
            result = session.execute(query)
            record = result.scalar_one_or_none()
            if record is None:
                _log_tx(session, f"[auth] ⚠️ No se encontró ningún registro RowLevelSecurity para actualizar con los identificadores proporcionados.")
                return 0

            old_dto = RowLevelSecurityRead.from_instance(record)
            for key, value in update_data.items():
                setattr(record, key, value)
            new_instance = record

            cls._on_update_before(new_instance, old_dto, update_data, session)
            session.flush()
            cls._on_update_after(new_instance, old_dto, update_data, session)

            return 1

        if session is not None:
            result = _execute_update(session)
        else:
            with sync_session_manager.get_session() as session:
                result = _execute_update(session)

        if result > 0:
            _log_commit(session, f"[auth] ✅ 1 registros RowLevelSecurity actualizados exitosamente")
        else:
            _log_tx(session, f"[auth] ⚠️ No se encontró ningún registro RowLevelSecurity para actualizar con los identificadores proporcionados.")

        return result
    
    @classmethod
    @sync_error_handler
    def update_many(
        cls,
        payload: RowLevelSecurityUpdate, 
        rls: Optional[Union[List[RLS], RLS]] = None,
        session: Optional[Session] = None
    ) -> int:
        """
        Actualiza múltiples registros basándose en campos de coincidencia.
        
        Args:
            payload: Datos de actualización y filtros
            rls: Reglas de seguridad a aplicar. Acotan la operación igual que acotan
                una consulta: lo que la regla no alcanza, no se modifica.
            session: Sesión existente (opcional)
            
        Returns:
            Número total de registros actualizados
        """
        _log_tx(session, f"[auth] 🔄 Actualizando múltiples RowLevelSecurity con filtros: {payload.filter.to_dict()}, valores: {payload.values.to_dict()}")

        filters = payload.filter.to_dict()
        values = payload.values.to_dict()
        values['updated_at'] = datetime.now()
        values['updated_by'] = get_username()
        
        if not filters and not values:  # Solo actualizar si hay filtros y valores
            return 0

        query = update(RowLevelSecurity)
        query = payload.filter.apply_to_query(query)
        query = RLSQueryApplicator.apply_rls(query, RowLevelSecurity, rls)
        
        query = query.values(**values)
                
        if session is not None:
            result = session.execute(query)
        else:
            with sync_session_manager.get_session() as session:
                result = session.execute(query)
        
        _log_commit(session, f"[auth] ✅ {result.rowcount} registros RowLevelSecurity actualizados masivamente exitosamente")

        return result.rowcount

    @classmethod
    @sync_error_handler
    def delete(
        cls, 
        id: int,
        rls: Optional[Union[List[RLS], RLS]] = None,
        session: Optional[Session] = None
    ) -> int:
        """
        Elimina un registro atentiendo a su primary key.
        
        Args:
            id: Filtrar por id para eliminar
            rls: Reglas de seguridad a aplicar. Acotan la operación igual que acotan
                una consulta: lo que la regla no alcanza, no se modifica.
            session: Sesión existente (opcional)
            
        Returns:
            Número de registros eliminados
        """
        _log_tx(session, f"[auth] 🗑️ Eliminando RowLevelSecurity:")
        _log_tx(session, f"[auth]    id={id}")

        def _execute_delete(session: Session) -> int:
            fetch_query = select(RowLevelSecurity)
            fetch_query = fetch_query.where(RowLevelSecurity.id == id)
            fetch_query = RLSQueryApplicator.apply_rls(fetch_query, RowLevelSecurity, rls)
            result = session.execute(fetch_query)
            record = result.scalar_one_or_none()
            
            if record is None:
                return 0
            
            old_dto = RowLevelSecurityRead.from_instance(record)

            cls._on_delete_before(old_dto, session)

            del_query = delete(RowLevelSecurity)
            del_query = del_query.where(RowLevelSecurity.id == id)
            del_query = RLSQueryApplicator.apply_rls(del_query, RowLevelSecurity, rls)
            result = session.execute(del_query)

            cls._on_delete_after(old_dto, session)

            return result.rowcount

        if session is not None:
            deleted = _execute_delete(session)
        else:
            with sync_session_manager.get_session() as session:
                deleted = _execute_delete(session)

        _log_commit(session, f"[auth] ✅ {deleted} registros RowLevelSecurity eliminados exitosamente")

        return deleted
    
    @classmethod
    @sync_error_handler
    def delete_many(
        cls,
        in_id: Optional[List[int]] = None,
        realm_id: Optional[int] = None,
        in_realm_id: Optional[List[int]] = None,
        min_realm_id: Optional[int] = None,
        max_realm_id: Optional[int] = None,
        schema_name: Optional[str] = None,
        in_schema_name: Optional[List[str]] = None,
        table_name: Optional[str] = None,
        in_table_name: Optional[List[str]] = None,
        column_name: Optional[str] = None,
        in_column_name: Optional[List[str]] = None,
        min_created_at: Optional[datetime] = None,
        max_created_at: Optional[datetime] = None,
        in_created_by: Optional[List[str]] = None,
        min_updated_at: Optional[datetime] = None,
        max_updated_at: Optional[datetime] = None,
        in_updated_by: Optional[List[str]] = None,
        rls: Optional[Union[List[RLS], RLS]] = None,
        session: Optional[Session] = None
    ) -> int:
        """
        Elimina múltiples registros basándose en filtros.
        
        Args:
        - in_id: Filtrar por múltiples valores de id (OR lógico)
            - realm_id: Filtrar por realm_id
            - in_realm_id: Filtrar por múltiples valores de realm_id (OR lógico)
            - min_realm_id: Filtrar por valor mínimo de realm_id (incluído)
            - max_realm_id: Filtrar por valor máximo de realm_id (incluído)
            - schema_name: Filtrar por schema_name
            - in_schema_name: Filtrar por múltiples valores de schema_name (OR lógico)
            - table_name: Filtrar por table_name
            - in_table_name: Filtrar por múltiples valores de table_name (OR lógico)
            - column_name: Filtrar por column_name
            - in_column_name: Filtrar por múltiples valores de column_name (OR lógico)
            - min_created_at: Filtrar por valor mínimo de created_at (incluído)
            - max_created_at: Filtrar por valor máximo de created_at (incluído)
            - in_created_by: Filtrar por múltiples valores de created_by (OR lógico)
            - min_updated_at: Filtrar por valor mínimo de updated_at (incluído)
            - max_updated_at: Filtrar por valor máximo de updated_at (incluído)
            - in_updated_by: Filtrar por múltiples valores de updated_by (OR lógico)
        - rls: Reglas de seguridad a aplicar (opcional)
        - session: Sesión existente (opcional)
            
        Returns:
            Número total de registros eliminados
        """


        def execute_query(session: Session) -> int:
            query = delete(RowLevelSecurity)

            _filter = RowLevelSecurityFilter(
                in_id=in_id,
                realm_id=realm_id,
                in_realm_id=in_realm_id,
                min_realm_id=min_realm_id,
                max_realm_id=max_realm_id,
                schema_name=schema_name,
                in_schema_name=in_schema_name,
                table_name=table_name,
                in_table_name=in_table_name,
                column_name=column_name,
                in_column_name=in_column_name,
                min_created_at=min_created_at,
                max_created_at=max_created_at,
                in_created_by=in_created_by,
                min_updated_at=min_updated_at,
                max_updated_at=max_updated_at,
                in_updated_by=in_updated_by,
            )
            query = _filter.apply_to_query(query)
            filters = _filter.to_dict()
            query = RLSQueryApplicator.apply_rls(query, RowLevelSecurity, rls)

            _log_tx(session, f"[auth] 🗑️  Eliminando múltiples RowLevelSecurity con filtros: {filters}")

            result = session.execute(query)
            return result.rowcount
        
        if session is not None:
            total_deleted = execute_query(session)
        else:
            with sync_session_manager.get_session() as session:
                total_deleted = execute_query(session)
        
        _log_commit(session, f"[auth] ✅ {total_deleted} registros RowLevelSecurity eliminados masivamente exitosamente")

        return total_deleted

    @classmethod
    def _build_native_upsert_stmt(cls, dialect_name: str, values: Union[Dict[str, Any], List[Dict[str, Any]]], match_fields: List[str], update_columns: List[str]):
        """
        Construye un statement INSERT ... ON CONFLICT nativo según el dialecto.
        
        Args:
            dialect_name: Nombre del dialecto de la base de datos
            values: Diccionario o lista de diccionarios con los datos a insertar
            match_fields: Campos de coincidencia para detectar conflictos
            update_columns: Columnas a actualizar en caso de conflicto
            
        Returns:
            Statement de upsert nativo o None si el dialecto no es soportado
        """
        # Normalizar todas las filas para que tengan exactamente las mismas claves
        if isinstance(values, list) and values:
            all_keys = set().union(*[row.keys() for row in values])
            values = [{k: row.get(k, None) for k in all_keys} for row in values]

        if dialect_name in ('postgresql', 'sqlite'):
            from sqlalchemy.dialects import postgresql, sqlite
            dialect_insert = postgresql.insert if dialect_name == 'postgresql' else sqlite.insert

            stmt = dialect_insert(RowLevelSecurity).values(values)
            if update_columns:
                stmt = stmt.on_conflict_do_update(
                    index_elements=match_fields,
                    set_={col: stmt.excluded[col] for col in update_columns}
                )
            else:
                stmt = stmt.on_conflict_do_nothing(index_elements=match_fields)
            return stmt

        elif dialect_name in ('mysql', 'mariadb'):
            from sqlalchemy.dialects.mysql import insert as mysql_insert

            stmt = mysql_insert(RowLevelSecurity).values(values)
            if update_columns:
                stmt = stmt.on_duplicate_key_update(
                    **{col: getattr(stmt.inserted, col) for col in update_columns}
                )
            return stmt

        return None

    @classmethod
    @sync_error_handler
    def upsert(
        cls,
        row_level_security: RowLevelSecurityCreate,
        match_fields: List[str] = ['realm_id', 'schema_name', 'table_name', 'column_name'],
        session: Optional[Session] = None
    ) -> RowLevelSecurityRead:
        """
        Inserta o actualiza un registro (upsert).
        
        Verifica si el registro existe por match_fields y delega a create() o update()
        según corresponda, garantizando la ejecución de hooks y triggers.
        
        Args:
            row_level_security: Datos del registro a insertar o actualizar
            match_fields: Campos a usar para verificar si el registro existe. 
                         Por defecto usa las claves primarias.
            session: Sesión existente (opcional)
            
        Returns:
            Instancia del modelo (creada o actualizada)
        """
        _log_tx(session, f"[auth] 🔄 Upsert RowLevelSecurity con campos de coincidencia: {match_fields}, datos: {row_level_security.to_dict()}")

        record_dict = row_level_security.to_dict()

        if not match_fields:
            raise ValueError("match_fields no puede estar vacío. Debe contener al menos un campo para identificar registros.")

        for field in match_fields:
            if field not in record_dict:
                raise ValueError(f"El campo '{field}' debe estar presente en 'row_level_security' para upsert.")
            if record_dict[field] is None:
                raise ValueError(f"El campo '{field}' no puede ser None. Debe tener un valor para upsert.")

        update_columns = [k for k in record_dict if k not in match_fields]

        def execute_query(session: Session) -> RowLevelSecurityRead:
            # SELECT para determinar si es create o update
            query = select(RowLevelSecurity)
            for field in match_fields:
                query = query.where(getattr(RowLevelSecurity, field) == record_dict[field])
            query_result = session.execute(query)
            existing = query_result.scalars().first()

            if existing:
                update_values = RowLevelSecurityUpdateValues(**{k: record_dict[k] for k in update_columns if k in record_dict})
                cls.update(
                    id=existing.id,
                    updated_values=update_values,
                    session=session
                )
                # Re-fetch para devolver el registro actualizado
                query_result = session.execute(query)
                result = query_result.scalars().first()
                return RowLevelSecurityRead.from_instance(result)
            else:
                return cls.create(row_level_security, session=session)

        if session is not None:
            result = execute_query(session)
            _log_commit(session, f"[auth] ✅ Upsert RowLevelSecurity completado exitosamente")
            return result
        else:
            with sync_session_manager.get_session() as session:
                result = execute_query(session)
            _log_commit(session, f"[auth] ✅ Upsert RowLevelSecurity completado exitosamente")
            return result

    @classmethod
    @sync_error_handler
    def upsert_many(
        cls,
        records: List[RowLevelSecurityCreate],
        match_fields: List[str] = ['realm_id', 'schema_name', 'table_name', 'column_name'],
        batch_size: int = 1000,
        session: Optional[Session] = None
    ) -> int:
        """
        Inserta o actualiza múltiples registros de forma optimizada.
        
        Sin triggers, utiliza operaciones bulk nativas del motor de base de datos
        (INSERT ... ON CONFLICT para PostgreSQL/SQLite, INSERT ... ON DUPLICATE KEY
        para MySQL) procesando registros en lotes para máxima eficiencia.
        Con triggers, separa registros nuevos y existentes por lotes, delegando a
        create_many() y update() para garantizar la ejecución de hooks y triggers.
        
        Args:
            records: Lista de registros a insertar o actualizar
            match_fields: Campos a usar para verificar si los registros existen.
                         Por defecto usa las claves primarias.
            batch_size: Tamaño del lote para procesamiento por lotes (default: 1000)
            session: Sesión existente (opcional)
            
        Returns:
            Número de registros procesados
        """
        if not records:
            return 0

        _log_tx(session, f"[auth] 🔄 Upsert masivo RowLevelSecurity con {len(records)} registros, campos de coincidencia: {match_fields}")

        if not match_fields:
            raise ValueError("match_fields no puede estar vacío. Debe contener al menos un campo para identificar registros.")

        records_data = [record.to_dict() for record in records]
        update_columns = [k for k in records_data[0] if k not in match_fields]

        def execute_query(session: Session) -> int:
            dialect_name = session.bind.dialect.name
            total = 0

            for i in range(0, len(records_data), batch_size):
                batch = records_data[i:i + batch_size]

                # Intentar upsert nativo con batch completo
                stmt = cls._build_native_upsert_stmt(dialect_name, batch, match_fields, update_columns)
                
                if stmt is not None:
                    session.execute(stmt)
                else:
                    # Fallback: batch SELECT + separar inserts/updates
                            
                    conditions = []
                    for record in batch:
                        if len(match_fields) == 1:
                            field = match_fields[0]
                            conditions.append(getattr(RowLevelSecurity, field) == record[field])
                        else:
                            record_conds = [getattr(RowLevelSecurity, f) == record[f] for f in match_fields]
                            conditions.append(and_(*record_conds))
                    
                    query = select(RowLevelSecurity).where(or_(*conditions))
                    query_result = session.execute(query)
                    existing_records = query_result.scalars().all()
                    
                    existing_keys = set()
                    for existing in existing_records:
                        key = tuple(getattr(existing, f) for f in match_fields)
                        existing_keys.add(key)
                    
                    to_insert = []
                    to_update = []
                    for record in batch:
                        key = tuple(record[f] for f in match_fields)
                        if key in existing_keys:
                            to_update.append(record)
                        else:
                            to_insert.append(record)
                    
                    # Bulk insert de registros nuevos
                    if to_insert:
                        session.execute(RowLevelSecurity.__table__.insert(), to_insert)
                    
                    # Bulk update de registros existentes
                    for record in to_update:
                        update_stmt = update(RowLevelSecurity)
                        for field in match_fields:
                            update_stmt = update_stmt.where(getattr(RowLevelSecurity, field) == record[field])
                        update_values = {k: v for k, v in record.items() if k not in match_fields}
                        if update_values:
                            session.execute(update_stmt.values(**update_values))
                
                total += len(batch)
            
            session.flush()
            return total

        if session is not None:
            result = execute_query(session)
        else:
            with sync_session_manager.get_session() as session:
                result = execute_query(session)

        _log_commit(session, f"[auth] ✅ Upsert masivo RowLevelSecurity completado: {result} registros procesados")

        return result
    

    @classmethod
    @sync_error_handler
    def sum(
        cls,
        agg_fields: List[str],
        in_id: Optional[List[int]] = None,
        realm_id: Optional[int] = None,
        in_realm_id: Optional[List[int]] = None,
        min_realm_id: Optional[int] = None,
        max_realm_id: Optional[int] = None,
        schema_name: Optional[str] = None,
        in_schema_name: Optional[List[str]] = None,
        table_name: Optional[str] = None,
        in_table_name: Optional[List[str]] = None,
        column_name: Optional[str] = None,
        in_column_name: Optional[List[str]] = None,
        min_created_at: Optional[datetime] = None,
        max_created_at: Optional[datetime] = None,
        created_by: Optional[str] = None,
        in_created_by: Optional[List[str]] = None,
        min_updated_at: Optional[datetime] = None,
        max_updated_at: Optional[datetime] = None,
        updated_by: Optional[str] = None,
        in_updated_by: Optional[List[str]] = None,
        rls: Optional[Union[List[RLS], RLS]] = None,
        session: Optional[Session] = None
    ) -> AggregationResult:
        """
        Suma los valores de campos específicos que coincidan con los filtros.

        Args:
            - agg_fields: Lista de nombres de campos para sumar
            - in_id: Filtrar por múltiples valores de id (OR lógico)
            - realm_id: Filtrar por realm_id
            - in_realm_id: Filtrar por múltiples valores de realm_id (OR lógico)
            - min_realm_id: Filtrar por valor mínimo de realm_id (incluído)
            - max_realm_id: Filtrar por valor máximo de realm_id (incluído)
            - schema_name: Filtrar por schema_name
            - in_schema_name: Filtrar por múltiples valores de schema_name (OR lógico)
            - table_name: Filtrar por table_name
            - in_table_name: Filtrar por múltiples valores de table_name (OR lógico)
            - column_name: Filtrar por column_name
            - in_column_name: Filtrar por múltiples valores de column_name (OR lógico)
            - min_created_at: Filtrar por valor mínimo de created_at (incluído)
            - max_created_at: Filtrar por valor máximo de created_at (incluído)
            - created_by: Filtrar por created_by
            - in_created_by: Filtrar por múltiples valores de created_by (OR lógico)
            - min_updated_at: Filtrar por valor mínimo de updated_at (incluído)
            - max_updated_at: Filtrar por valor máximo de updated_at (incluído)
            - updated_by: Filtrar por updated_by
            - in_updated_by: Filtrar por múltiples valores de updated_by (OR lógico)
            - rls: Reglas de seguridad a aplicar (opcional)
            - session: Sesión existente (opcional)

        Returns:
            AggregationResult con información detallada de la operación:
            - success: False si algún campo no existe o su tipo no admite 'sum'. Es
              todo o nada: entonces no se consulta nada y `errors` dice por qué.
            - rows: Lista con una fila AggRow {"sum_<field>": value}
            - processed_fields: Los campos agregados
            - errors: Por qué no se pudo (campos inexistentes o de un tipo que no la admite)
            - metadata: Información adicional sobre la operación
        """
        _log_tx(session, f"[auth] 🧮 Suma de campos {agg_fields} de registros RowLevelSecurity con filtros aplicados")

        fields = list(dict.fromkeys(agg_fields))
        if fields:
            errors = [
                error for error in (
                    agg_field_error("RowLevelSecurity", _AGG_COLUMNS, field, "sum") for field in fields
                ) if error
            ]
        else:
            errors = ["No se proporcionaron campos para sumar"]

        if errors:
            for error in errors:
                logger.warning(f"[auth] ⚠️ {error}")
            return AggregationResult(
                success=False,
                rows=[],
                processed_fields=[],
                errors=errors,
                metadata={
                    "total_requested_fields": len(agg_fields),
                    "valid_fields_count": 0,
                    "operation": "sum"
                }
            )

        query = select(*[
            OPERATION_FUNCTIONS["sum"](getattr(RowLevelSecurity, field)).label(f"sum_{field}")
            for field in fields
        ])

        _filter = RowLevelSecurityFilter(
            in_id=in_id,
            realm_id=realm_id,
            in_realm_id=in_realm_id,
            min_realm_id=min_realm_id,
            max_realm_id=max_realm_id,
            schema_name=schema_name,
            in_schema_name=in_schema_name,
            table_name=table_name,
            in_table_name=in_table_name,
            column_name=column_name,
            in_column_name=in_column_name,
            min_created_at=min_created_at,
            max_created_at=max_created_at,
            created_by=created_by,
            in_created_by=in_created_by,
            min_updated_at=min_updated_at,
            max_updated_at=max_updated_at,
            updated_by=updated_by,
            in_updated_by=in_updated_by,
        )
        query = _filter.apply_to_query(query)
        filters = _filter.to_dict()

        # Log de parámetros aplicados
        if filters:
            _log_tx(session, f"[auth]     filters={filters}")

        # Aplicar regla RLS (si existe)
        if rls is not None:
            query = RLSQueryApplicator.apply_rls(query, RowLevelSecurity, rls)

        if session is not None:
            result = session.execute(query)
        else:
            with sync_session_manager.get_session() as session:
                result = session.execute(query)

        row = result.first()
        data = {
            f"sum_{field}": agg_value("sum", getattr(row, f"sum_{field}") if row else None)
            for field in fields
        }

        _log_commit(session, f"[auth] ✅ Suma RowLevelSecurity: {data}")

        return AggregationResult(
            success=True,
            rows=[AggRow(group={}, data=data)],
            processed_fields=fields,
            metadata={
                "total_requested_fields": len(agg_fields),
                "valid_fields_count": len(fields),
                "operation": "sum"
            }
        )

    @classmethod
    @sync_error_handler
    def mean(
        cls,
        agg_fields: List[str],
        in_id: Optional[List[int]] = None,
        realm_id: Optional[int] = None,
        in_realm_id: Optional[List[int]] = None,
        min_realm_id: Optional[int] = None,
        max_realm_id: Optional[int] = None,
        schema_name: Optional[str] = None,
        in_schema_name: Optional[List[str]] = None,
        table_name: Optional[str] = None,
        in_table_name: Optional[List[str]] = None,
        column_name: Optional[str] = None,
        in_column_name: Optional[List[str]] = None,
        min_created_at: Optional[datetime] = None,
        max_created_at: Optional[datetime] = None,
        created_by: Optional[str] = None,
        in_created_by: Optional[List[str]] = None,
        min_updated_at: Optional[datetime] = None,
        max_updated_at: Optional[datetime] = None,
        updated_by: Optional[str] = None,
        in_updated_by: Optional[List[str]] = None,
        rls: Optional[Union[List[RLS], RLS]] = None,
        session: Optional[Session] = None
    ) -> AggregationResult:
        """
        Calcula la media de los valores de campos específicos que coincidan con los filtros.

        Args:
            - agg_fields: Lista de nombres de campos para calcular la media
            - in_id: Filtrar por múltiples valores de id (OR lógico)
            - realm_id: Filtrar por realm_id
            - in_realm_id: Filtrar por múltiples valores de realm_id (OR lógico)
            - min_realm_id: Filtrar por valor mínimo de realm_id (incluído)
            - max_realm_id: Filtrar por valor máximo de realm_id (incluído)
            - schema_name: Filtrar por schema_name
            - in_schema_name: Filtrar por múltiples valores de schema_name (OR lógico)
            - table_name: Filtrar por table_name
            - in_table_name: Filtrar por múltiples valores de table_name (OR lógico)
            - column_name: Filtrar por column_name
            - in_column_name: Filtrar por múltiples valores de column_name (OR lógico)
            - min_created_at: Filtrar por valor mínimo de created_at (incluído)
            - max_created_at: Filtrar por valor máximo de created_at (incluído)
            - created_by: Filtrar por created_by
            - in_created_by: Filtrar por múltiples valores de created_by (OR lógico)
            - min_updated_at: Filtrar por valor mínimo de updated_at (incluído)
            - max_updated_at: Filtrar por valor máximo de updated_at (incluído)
            - updated_by: Filtrar por updated_by
            - in_updated_by: Filtrar por múltiples valores de updated_by (OR lógico)
            - rls: Reglas de seguridad a aplicar (opcional)
            - session: Sesión existente (opcional)

        Returns:
            AggregationResult con información detallada de la operación:
            - success: False si algún campo no existe o su tipo no admite 'mean'. Es
              todo o nada: entonces no se consulta nada y `errors` dice por qué.
            - rows: Lista con una fila AggRow {"mean_<field>": value}
            - processed_fields: Los campos agregados
            - errors: Por qué no se pudo (campos inexistentes o de un tipo que no la admite)
            - metadata: Información adicional sobre la operación
        """
        _log_tx(session, f"[auth] 📊 Media de campos {agg_fields} de registros RowLevelSecurity con filtros aplicados")

        fields = list(dict.fromkeys(agg_fields))
        if fields:
            errors = [
                error for error in (
                    agg_field_error("RowLevelSecurity", _AGG_COLUMNS, field, "mean") for field in fields
                ) if error
            ]
        else:
            errors = ["No se proporcionaron campos para calcular la media"]

        if errors:
            for error in errors:
                logger.warning(f"[auth] ⚠️ {error}")
            return AggregationResult(
                success=False,
                rows=[],
                processed_fields=[],
                errors=errors,
                metadata={
                    "total_requested_fields": len(agg_fields),
                    "valid_fields_count": 0,
                    "operation": "mean"
                }
            )

        query = select(*[
            OPERATION_FUNCTIONS["mean"](getattr(RowLevelSecurity, field)).label(f"mean_{field}")
            for field in fields
        ])

        _filter = RowLevelSecurityFilter(
            in_id=in_id,
            realm_id=realm_id,
            in_realm_id=in_realm_id,
            min_realm_id=min_realm_id,
            max_realm_id=max_realm_id,
            schema_name=schema_name,
            in_schema_name=in_schema_name,
            table_name=table_name,
            in_table_name=in_table_name,
            column_name=column_name,
            in_column_name=in_column_name,
            min_created_at=min_created_at,
            max_created_at=max_created_at,
            created_by=created_by,
            in_created_by=in_created_by,
            min_updated_at=min_updated_at,
            max_updated_at=max_updated_at,
            updated_by=updated_by,
            in_updated_by=in_updated_by,
        )
        query = _filter.apply_to_query(query)
        filters = _filter.to_dict()

        # Log de parámetros aplicados
        if filters:
            _log_tx(session, f"[auth]     filters={filters}")

        # Aplicar regla RLS (si existe)
        if rls is not None:
            query = RLSQueryApplicator.apply_rls(query, RowLevelSecurity, rls)

        if session is not None:
            result = session.execute(query)
        else:
            with sync_session_manager.get_session() as session:
                result = session.execute(query)

        row = result.first()
        data = {
            f"mean_{field}": agg_value("mean", getattr(row, f"mean_{field}") if row else None)
            for field in fields
        }

        _log_commit(session, f"[auth] ✅ Media RowLevelSecurity: {data}")

        return AggregationResult(
            success=True,
            rows=[AggRow(group={}, data=data)],
            processed_fields=fields,
            metadata={
                "total_requested_fields": len(agg_fields),
                "valid_fields_count": len(fields),
                "operation": "mean"
            }
        )

    @classmethod
    @sync_error_handler
    def max(
        cls,
        agg_fields: List[str],
        in_id: Optional[List[int]] = None,
        realm_id: Optional[int] = None,
        in_realm_id: Optional[List[int]] = None,
        min_realm_id: Optional[int] = None,
        max_realm_id: Optional[int] = None,
        schema_name: Optional[str] = None,
        in_schema_name: Optional[List[str]] = None,
        table_name: Optional[str] = None,
        in_table_name: Optional[List[str]] = None,
        column_name: Optional[str] = None,
        in_column_name: Optional[List[str]] = None,
        min_created_at: Optional[datetime] = None,
        max_created_at: Optional[datetime] = None,
        created_by: Optional[str] = None,
        in_created_by: Optional[List[str]] = None,
        min_updated_at: Optional[datetime] = None,
        max_updated_at: Optional[datetime] = None,
        updated_by: Optional[str] = None,
        in_updated_by: Optional[List[str]] = None,
        rls: Optional[Union[List[RLS], RLS]] = None,
        session: Optional[Session] = None
    ) -> AggregationResult:
        """
        Encuentra el valor máximo de campos específicos que coincidan con los filtros.

        Args:
            - agg_fields: Lista de nombres de campos para calcular el máximo
            - in_id: Filtrar por múltiples valores de id (OR lógico)
            - realm_id: Filtrar por realm_id
            - in_realm_id: Filtrar por múltiples valores de realm_id (OR lógico)
            - min_realm_id: Filtrar por valor mínimo de realm_id (incluído)
            - max_realm_id: Filtrar por valor máximo de realm_id (incluído)
            - schema_name: Filtrar por schema_name
            - in_schema_name: Filtrar por múltiples valores de schema_name (OR lógico)
            - table_name: Filtrar por table_name
            - in_table_name: Filtrar por múltiples valores de table_name (OR lógico)
            - column_name: Filtrar por column_name
            - in_column_name: Filtrar por múltiples valores de column_name (OR lógico)
            - min_created_at: Filtrar por valor mínimo de created_at (incluído)
            - max_created_at: Filtrar por valor máximo de created_at (incluído)
            - created_by: Filtrar por created_by
            - in_created_by: Filtrar por múltiples valores de created_by (OR lógico)
            - min_updated_at: Filtrar por valor mínimo de updated_at (incluído)
            - max_updated_at: Filtrar por valor máximo de updated_at (incluído)
            - updated_by: Filtrar por updated_by
            - in_updated_by: Filtrar por múltiples valores de updated_by (OR lógico)
            - rls: Reglas de seguridad a aplicar (opcional)
            - session: Sesión existente (opcional)

        Returns:
            AggregationResult con información detallada de la operación:
            - success: False si algún campo no existe o su tipo no admite 'max'. Es
              todo o nada: entonces no se consulta nada y `errors` dice por qué.
            - rows: Lista con una fila AggRow {"max_<field>": value}
            - processed_fields: Los campos agregados
            - errors: Por qué no se pudo (campos inexistentes o de un tipo que no la admite)
            - metadata: Información adicional sobre la operación
        """
        _log_tx(session, f"[auth] 🔺 Máximo de campos {agg_fields} de registros RowLevelSecurity con filtros aplicados")

        fields = list(dict.fromkeys(agg_fields))
        if fields:
            errors = [
                error for error in (
                    agg_field_error("RowLevelSecurity", _AGG_COLUMNS, field, "max") for field in fields
                ) if error
            ]
        else:
            errors = ["No se proporcionaron campos para calcular el máximo"]

        if errors:
            for error in errors:
                logger.warning(f"[auth] ⚠️ {error}")
            return AggregationResult(
                success=False,
                rows=[],
                processed_fields=[],
                errors=errors,
                metadata={
                    "total_requested_fields": len(agg_fields),
                    "valid_fields_count": 0,
                    "operation": "max"
                }
            )

        query = select(*[
            OPERATION_FUNCTIONS["max"](getattr(RowLevelSecurity, field)).label(f"max_{field}")
            for field in fields
        ])

        _filter = RowLevelSecurityFilter(
            in_id=in_id,
            realm_id=realm_id,
            in_realm_id=in_realm_id,
            min_realm_id=min_realm_id,
            max_realm_id=max_realm_id,
            schema_name=schema_name,
            in_schema_name=in_schema_name,
            table_name=table_name,
            in_table_name=in_table_name,
            column_name=column_name,
            in_column_name=in_column_name,
            min_created_at=min_created_at,
            max_created_at=max_created_at,
            created_by=created_by,
            in_created_by=in_created_by,
            min_updated_at=min_updated_at,
            max_updated_at=max_updated_at,
            updated_by=updated_by,
            in_updated_by=in_updated_by,
        )
        query = _filter.apply_to_query(query)
        filters = _filter.to_dict()

        # Log de parámetros aplicados
        if filters:
            _log_tx(session, f"[auth]     filters={filters}")

        # Aplicar regla RLS (si existe)
        if rls is not None:
            query = RLSQueryApplicator.apply_rls(query, RowLevelSecurity, rls)

        if session is not None:
            result = session.execute(query)
        else:
            with sync_session_manager.get_session() as session:
                result = session.execute(query)

        row = result.first()
        data = {
            f"max_{field}": agg_value("max", getattr(row, f"max_{field}") if row else None)
            for field in fields
        }

        _log_commit(session, f"[auth] ✅ Máximo RowLevelSecurity: {data}")

        return AggregationResult(
            success=True,
            rows=[AggRow(group={}, data=data)],
            processed_fields=fields,
            metadata={
                "total_requested_fields": len(agg_fields),
                "valid_fields_count": len(fields),
                "operation": "max"
            }
        )

    @classmethod
    @sync_error_handler
    def min(
        cls,
        agg_fields: List[str],
        in_id: Optional[List[int]] = None,
        realm_id: Optional[int] = None,
        in_realm_id: Optional[List[int]] = None,
        min_realm_id: Optional[int] = None,
        max_realm_id: Optional[int] = None,
        schema_name: Optional[str] = None,
        in_schema_name: Optional[List[str]] = None,
        table_name: Optional[str] = None,
        in_table_name: Optional[List[str]] = None,
        column_name: Optional[str] = None,
        in_column_name: Optional[List[str]] = None,
        min_created_at: Optional[datetime] = None,
        max_created_at: Optional[datetime] = None,
        created_by: Optional[str] = None,
        in_created_by: Optional[List[str]] = None,
        min_updated_at: Optional[datetime] = None,
        max_updated_at: Optional[datetime] = None,
        updated_by: Optional[str] = None,
        in_updated_by: Optional[List[str]] = None,
        rls: Optional[Union[List[RLS], RLS]] = None,
        session: Optional[Session] = None
    ) -> AggregationResult:
        """
        Encuentra el valor mínimo de campos específicos que coincidan con los filtros.

        Args:
            - agg_fields: Lista de nombres de campos para calcular el mínimo
            - in_id: Filtrar por múltiples valores de id (OR lógico)
            - realm_id: Filtrar por realm_id
            - in_realm_id: Filtrar por múltiples valores de realm_id (OR lógico)
            - min_realm_id: Filtrar por valor mínimo de realm_id (incluído)
            - max_realm_id: Filtrar por valor máximo de realm_id (incluído)
            - schema_name: Filtrar por schema_name
            - in_schema_name: Filtrar por múltiples valores de schema_name (OR lógico)
            - table_name: Filtrar por table_name
            - in_table_name: Filtrar por múltiples valores de table_name (OR lógico)
            - column_name: Filtrar por column_name
            - in_column_name: Filtrar por múltiples valores de column_name (OR lógico)
            - min_created_at: Filtrar por valor mínimo de created_at (incluído)
            - max_created_at: Filtrar por valor máximo de created_at (incluído)
            - created_by: Filtrar por created_by
            - in_created_by: Filtrar por múltiples valores de created_by (OR lógico)
            - min_updated_at: Filtrar por valor mínimo de updated_at (incluído)
            - max_updated_at: Filtrar por valor máximo de updated_at (incluído)
            - updated_by: Filtrar por updated_by
            - in_updated_by: Filtrar por múltiples valores de updated_by (OR lógico)
            - rls: Reglas de seguridad a aplicar (opcional)
            - session: Sesión existente (opcional)

        Returns:
            AggregationResult con información detallada de la operación:
            - success: False si algún campo no existe o su tipo no admite 'min'. Es
              todo o nada: entonces no se consulta nada y `errors` dice por qué.
            - rows: Lista con una fila AggRow {"min_<field>": value}
            - processed_fields: Los campos agregados
            - errors: Por qué no se pudo (campos inexistentes o de un tipo que no la admite)
            - metadata: Información adicional sobre la operación
        """
        _log_tx(session, f"[auth] 🔻 Mínimo de campos {agg_fields} de registros RowLevelSecurity con filtros aplicados")

        fields = list(dict.fromkeys(agg_fields))
        if fields:
            errors = [
                error for error in (
                    agg_field_error("RowLevelSecurity", _AGG_COLUMNS, field, "min") for field in fields
                ) if error
            ]
        else:
            errors = ["No se proporcionaron campos para calcular el mínimo"]

        if errors:
            for error in errors:
                logger.warning(f"[auth] ⚠️ {error}")
            return AggregationResult(
                success=False,
                rows=[],
                processed_fields=[],
                errors=errors,
                metadata={
                    "total_requested_fields": len(agg_fields),
                    "valid_fields_count": 0,
                    "operation": "min"
                }
            )

        query = select(*[
            OPERATION_FUNCTIONS["min"](getattr(RowLevelSecurity, field)).label(f"min_{field}")
            for field in fields
        ])

        _filter = RowLevelSecurityFilter(
            in_id=in_id,
            realm_id=realm_id,
            in_realm_id=in_realm_id,
            min_realm_id=min_realm_id,
            max_realm_id=max_realm_id,
            schema_name=schema_name,
            in_schema_name=in_schema_name,
            table_name=table_name,
            in_table_name=in_table_name,
            column_name=column_name,
            in_column_name=in_column_name,
            min_created_at=min_created_at,
            max_created_at=max_created_at,
            created_by=created_by,
            in_created_by=in_created_by,
            min_updated_at=min_updated_at,
            max_updated_at=max_updated_at,
            updated_by=updated_by,
            in_updated_by=in_updated_by,
        )
        query = _filter.apply_to_query(query)
        filters = _filter.to_dict()

        # Log de parámetros aplicados
        if filters:
            _log_tx(session, f"[auth]     filters={filters}")

        # Aplicar regla RLS (si existe)
        if rls is not None:
            query = RLSQueryApplicator.apply_rls(query, RowLevelSecurity, rls)

        if session is not None:
            result = session.execute(query)
        else:
            with sync_session_manager.get_session() as session:
                result = session.execute(query)

        row = result.first()
        data = {
            f"min_{field}": agg_value("min", getattr(row, f"min_{field}") if row else None)
            for field in fields
        }

        _log_commit(session, f"[auth] ✅ Mínimo RowLevelSecurity: {data}")

        return AggregationResult(
            success=True,
            rows=[AggRow(group={}, data=data)],
            processed_fields=fields,
            metadata={
                "total_requested_fields": len(agg_fields),
                "valid_fields_count": len(fields),
                "operation": "min"
            }
        )

    @classmethod
    @sync_error_handler
    def agg(
        cls,
        request: AggRequest,
        in_id: Optional[List[int]] = None,
        realm_id: Optional[int] = None,
        in_realm_id: Optional[List[int]] = None,
        min_realm_id: Optional[int] = None,
        max_realm_id: Optional[int] = None,
        schema_name: Optional[str] = None,
        in_schema_name: Optional[List[str]] = None,
        table_name: Optional[str] = None,
        in_table_name: Optional[List[str]] = None,
        column_name: Optional[str] = None,
        in_column_name: Optional[List[str]] = None,
        min_created_at: Optional[datetime] = None,
        max_created_at: Optional[datetime] = None,
        created_by: Optional[str] = None,
        in_created_by: Optional[List[str]] = None,
        min_updated_at: Optional[datetime] = None,
        max_updated_at: Optional[datetime] = None,
        updated_by: Optional[str] = None,
        in_updated_by: Optional[List[str]] = None,
        verbose: bool = False,
        rls: Optional[Union[List[RLS], RLS]] = None,
        session: Optional[Session] = None
    ) -> AggregationResult:
        """
        Realiza múltiples operaciones de agregación en una sola consulta, con GROUP BY opcional.

        Args:
            - request: AggRequest con las operaciones a calcular y los campos de agrupación.
                       Ejemplo sin GROUP BY:
                           AggRequest(aggregations={"sum": ["price"], "count": ["id"]})
                       Ejemplo con GROUP BY:
                           AggRequest(
                               aggregations={"sum": [AggField(expr="revenue-cost", alias="profit")]},
                               group_by=["status", GroupByField(field="created_at", trunc=DatetimeTrunc.month)]
                           )
            - in_id: Filtrar por múltiples valores de id (OR lógico)
            - realm_id: Filtrar por realm_id
            - in_realm_id: Filtrar por múltiples valores de realm_id (OR lógico)
            - min_realm_id: Filtrar por valor mínimo de realm_id (incluído)
            - max_realm_id: Filtrar por valor máximo de realm_id (incluído)
            - schema_name: Filtrar por schema_name
            - in_schema_name: Filtrar por múltiples valores de schema_name (OR lógico)
            - table_name: Filtrar por table_name
            - in_table_name: Filtrar por múltiples valores de table_name (OR lógico)
            - column_name: Filtrar por column_name
            - in_column_name: Filtrar por múltiples valores de column_name (OR lógico)
            - min_created_at: Filtrar por valor mínimo de created_at (incluído)
            - max_created_at: Filtrar por valor máximo de created_at (incluído)
            - created_by: Filtrar por created_by
            - in_created_by: Filtrar por múltiples valores de created_by (OR lógico)
            - min_updated_at: Filtrar por valor mínimo de updated_at (incluído)
            - max_updated_at: Filtrar por valor máximo de updated_at (incluído)
            - updated_by: Filtrar por updated_by
            - in_updated_by: Filtrar por múltiples valores de updated_by (OR lógico)
            - verbose: Si True, emite logs detallados de cada campo, expresión y fila procesada.
            - rls: Reglas de seguridad a aplicar (opcional)
            - session: Sesión existente (opcional).

        Returns:
            AggregationResult:
            - Sin GROUP BY: rows contiene una sola fila con group={}.
            - Con GROUP BY: rows contiene una fila por combinación de valores de agrupación.

        Examples:
            ```python
            # Agregación global
            result = dao.agg(
                AggRequest(aggregations={"sum": ["price"], "count": ["id"]}),
                status="active"
            )
            result.rows[0].data  # {"sum_price": 1000.0, "count_id": 50}

            # Con GROUP BY por campo discreto
            result = dao.agg(AggRequest(
                aggregations={"sum": ["revenue"], "count": ["id"]},
                group_by=["status"]
            ))
            for row in result.rows:
                print(row.group, row.data)

            # Con GROUP BY por datetime truncado al mes
            result = dao.agg(AggRequest(
                aggregations={"sum": [AggField(expr="revenue-cost", alias="profit")]},
                group_by=[GroupByField(field="created_at", trunc=DatetimeTrunc.month)]
            ))
            ```
        """
        _log_tx(session, f"[auth] 🎯 Realizando agregaciones en RowLevelSecurity: {list(request.aggregations.keys())}")
        if verbose:
            _log_tx(session, f"[auth]   aggregations={dict(request.aggregations)}, group_by={request.group_by}")

        warnings = []
        errors = []
        all_valid_fields = []
        operations_metadata = {}

        if not request.aggregations:
            logger.warning(f"[auth] ⚠️ No se proporcionaron operaciones de agregación")
            return AggregationResult(
                success=False,
                rows=[],
                group_by=[],
                processed_fields=[],
                errors=["No se proporcionaron operaciones de agregación"],
                metadata={"total_operations": 0}
            )

        # ── 1. Construir expresiones de agregación ────────────────────────────
        agg_expressions = []

        for operation, fields in request.aggregations.items():
            if operation not in AGG_OPERATIONS:
                error_msg = f"Operación '{operation}' no soportada. Válidas: {list(AGG_OPERATIONS)}"
                errors.append(error_msg)
                logger.warning(f"[auth] ⚠️ {error_msg}")
                continue

            if not fields:
                warnings.append(f"No se proporcionaron campos para la operación '{operation}'")
                continue

            valid_fields_for_operation = []
            field_label_mapping        = {}

            for field in fields:
                try:
                    # Normalizar a (expression, alias)
                    if isinstance(field, AggField):
                        expression = field.expr
                        alias      = field.alias
                    else:
                        expression = str(field)
                        alias      = None

                    is_expression = any(op in expression for op in ['+', '-', '*', '/', '%', '(', ')'])

                    if is_expression:
                        try:
                            column_expr = ExpressionParser.parse(expression, RowLevelSecurity)
                            expression_error = agg_expression_error("RowLevelSecurity", _AGG_COLUMNS, expression)
                            if expression_error:
                                errors.append(expression_error)
                                continue
                            if alias:
                                field_key  = alias
                                label_name = f"{operation}_{alias}"
                            else:
                                clean_expr = ExpressionParser.get_field_name(expression)
                                field_key  = clean_expr
                                label_name = f"{operation}_{clean_expr}"

                            valid_fields_for_operation.append(field_key)
                            all_valid_fields.append(field_key)
                            field_label_mapping[field_key] = label_name
                            sql_func = OPERATION_FUNCTIONS[operation]
                            agg_expressions.append(sql_func(column_expr).label(label_name))
                            if verbose:
                                _log_tx(session, f"[auth]   ✓ [{operation}] expr='{expression}' → label='{label_name}'")
                        except ValueError as e:
                            error_msg = f"Error al parsear expresión '{expression}': {str(e)}"
                            errors.append(error_msg)
                            logger.warning(f"[auth] ⚠️ {error_msg}")
                    else:
                        field_error = agg_field_error("RowLevelSecurity", _AGG_COLUMNS, expression, operation)
                        if field_error:
                            errors.append(field_error)
                            if verbose:
                                _log_tx(session, f"[auth]   ✗ [{operation}] {field_error}")
                        else:
                            column = getattr(RowLevelSecurity, expression)
                            if alias:
                                field_key  = alias
                                label_name = f"{operation}_{alias}"
                            else:
                                field_key  = expression
                                label_name = f"{operation}_{expression}"

                            valid_fields_for_operation.append(field_key)
                            all_valid_fields.append(field_key)
                            field_label_mapping[field_key] = label_name

                            sql_func = OPERATION_FUNCTIONS[operation]
                            agg_expressions.append(sql_func(column).label(label_name))
                            if verbose:
                                _log_tx(session, f"[auth]   ✓ [{operation}] campo='{expression}' → label='{label_name}'")

                except Exception as e:
                    errors.append(f"Error inesperado procesando campo '{field}': {str(e)}")

            if valid_fields_for_operation:
                operations_metadata[operation] = {
                    "requested_fields": [f.expr if isinstance(f, AggField) else str(f) for f in fields],
                    "valid_fields":      valid_fields_for_operation,
                    "field_label_mapping": field_label_mapping,
                    "valid_count":       len(valid_fields_for_operation),
                    "invalid_count":     len(fields) - len(valid_fields_for_operation),
                }

        if not agg_expressions:
            logger.warning(f"[auth] ⚠️ No hay operaciones de agregación válidas")
            return AggregationResult(
                success=False,
                rows=[],
                group_by=[],
                processed_fields=[],
                warnings=warnings,
                errors=errors,
                metadata={"total_operations": len(request.aggregations), "valid_operations": 0, "total_expressions": 0, "operations_summary": operations_metadata}
            )

        # ── 2. Validar y construir expresiones de GROUP BY ────────────────────
        group_select_exprs = []   # van al SELECT con label
        group_raw_exprs    = []   # van al GROUP BY sin label
        group_keys         = []   # claves en AggRow.group
        group_field_names  = []   # nombres de campo originales para AggregationResult.group_by

        if request.group_by:
            for gb_item in request.group_by:
                gb_field = gb_item if isinstance(gb_item, GroupByField) else GroupByField(field=gb_item)
                field_name = gb_field.field

                if not hasattr(RowLevelSecurity, field_name):
                    errors.append(f"Campo de group_by '{field_name}' no existe en modelo RowLevelSecurity")
                    continue

                column      = getattr(RowLevelSecurity, field_name)
                column_type = str(column.type).upper()

                if any(t in column_type for t in GROUP_BY_FORBIDDEN_TYPES):
                    errors.append(f"Campo '{field_name}' es de tipo '{column_type}': los tipos continuos no están permitidos en group_by")
                    continue

                is_datetime = any(t in column_type for t in GROUP_BY_DATETIME_TYPES)

                # Ignorarlo agruparía por otra cosa de la que se pidió: un DATE truncado al mes
                # salía agrupado por día, con un aviso que nadie leía.
                if gb_field.trunc is not None and not is_datetime:
                    errors.append(f"Campo '{field_name}' es de tipo '{column_type}': 'trunc' solo se aplica a DATETIME/TIMESTAMP")
                    continue

                if is_datetime:
                    if gb_field.trunc is None:
                        errors.append(f"Campo '{field_name}' es de tipo DATETIME/TIMESTAMP: 'trunc' es obligatorio en GroupByField")
                        continue
                    trunc_value  = gb_field.trunc.value
                    group_key    = f"{field_name}_{trunc_value}"
                    # Intervalos personalizados usan date_bin; estándar usan date_trunc
                    _CUSTOM_TRUNC_INTERVALS = {
                        "15min": "15 minutes",
                        "30min": "30 minutes",
                        "3h":    "3 hours",
                        "6h":    "6 hours",
                        "12h":   "12 hours",
                    }
                    if trunc_value in _CUSTOM_TRUNC_INTERVALS:
                        interval_str = _CUSTOM_TRUNC_INTERVALS[trunc_value]
                        raw_expr = func.date_bin(
                            text(f"interval '{interval_str}'"),
                            column,
                            text("timestamp '2001-01-01'")
                        )
                    else:
                        raw_expr = func.date_trunc(trunc_value, column)
                    select_expr  = raw_expr.label(group_key)
                else:
                    group_key    = field_name
                    raw_expr     = column
                    select_expr  = column.label(group_key)

                group_select_exprs.append(select_expr)
                group_raw_exprs.append(raw_expr)
                group_keys.append(group_key)
                group_field_names.append(field_name)
                if verbose:
                    if is_datetime:
                        _log_tx(session, f"[auth]   GROUP BY '{field_name}' (datetime, trunc='{trunc_value}') → key='{group_key}'")
                    else:
                        _log_tx(session, f"[auth]   GROUP BY '{field_name}' (tipo={column_type}) → key='{group_key}'")

        # ── 3. Validar ORDER BY ──────────────────────────────────────────────
        # Un order_by que no se puede aplicar es un error: ignorarlo, con un `limit`, daría
        # «los N primeros» de un orden que no es el pedido.
        order_clauses = []
        for order_item in request.order_by or []:
            op_meta = operations_metadata.get(order_item.operation)
            if op_meta is None:
                errors.append(f"order_by: operación '{order_item.operation}' no está en las agregaciones solicitadas")
                continue
            label_name = op_meta.get("field_label_mapping", {}).get(order_item.field)
            if label_name is None:
                errors.append(f"order_by: campo '{order_item.field}' no encontrado en operación '{order_item.operation}'")
                continue
            col = literal_column(label_name)
            order_clauses.append(col.desc() if order_item.direction == "desc" else col.asc())
            if verbose:
                _log_tx(session, f"[auth]   ORDER BY '{label_name}' {order_item.direction.upper()}")

        # Todo o nada: si una sola parte de la petición no se puede hacer, no se consulta.
        # Antes se ejecutaba lo que sí valía y los errores viajaban al lado con success=True,
        # así que quien solo miraba `rows` recibía un resultado al que le faltaban claves.
        if errors:
            for error in errors:
                logger.warning(f"[auth] ⚠️ {error}")
            return AggregationResult(
                success=False,
                rows=[],
                group_by=[],
                processed_fields=[],
                warnings=warnings,
                errors=errors,
                metadata={"total_operations": len(request.aggregations), "valid_operations": 0, "total_expressions": 0, "operations_summary": operations_metadata}
            )

        # ── 4. Construir y ejecutar query ─────────────────────────────────────
        query = select(*agg_expressions, *group_select_exprs)

        # Filters
        _filter = RowLevelSecurityFilter(
            in_id=in_id,
            realm_id=realm_id,
            in_realm_id=in_realm_id,
            min_realm_id=min_realm_id,
            max_realm_id=max_realm_id,
            schema_name=schema_name,
            in_schema_name=in_schema_name,
            table_name=table_name,
            in_table_name=in_table_name,
            column_name=column_name,
            in_column_name=in_column_name,
            min_created_at=min_created_at,
            max_created_at=max_created_at,
            created_by=created_by,
            in_created_by=in_created_by,
            min_updated_at=min_updated_at,
            max_updated_at=max_updated_at,
            updated_by=updated_by,
            in_updated_by=in_updated_by,
        )
        query = _filter.apply_to_query(query)
        filters = _filter.to_dict()

        if filters:
            _log_tx(session, f"[auth]     filters={filters}")
        
        # Aplicar regla RLS (si existe)
        if rls is not None:
            query = RLSQueryApplicator.apply_rls(query, RowLevelSecurity, rls)

        if group_raw_exprs:
            query = query.group_by(*group_raw_exprs)

        if order_clauses:
            query = query.order_by(*order_clauses)

        if request.limit is not None:
            query = query.limit(request.limit)
            if verbose:
                _log_tx(session, f"[auth]   LIMIT {request.limit}")

        if session is not None:
            result = session.execute(query)
        else:
            with sync_session_manager.get_session() as session:
                result = session.execute(query)

        # ── 5. Construir AggRow por cada fila del resultado ───────────────────
        db_rows  = result.all()
        agg_rows = []

        def _extract_row_data(row) -> Dict[str, Any]:
            row_data = {}
            for operation, op_meta in operations_metadata.items():
                lmap = op_meta.get("field_label_mapping", {})
                for field in op_meta["valid_fields"]:
                    label_name = lmap.get(field, f"{operation}_{field}")
                    row_data[f"{operation}_{field}"] = agg_value(operation, getattr(row, label_name, None))
            return row_data

        if db_rows:
            for row in db_rows:
                group_data = {key: getattr(row, key, None) for key in group_keys}
                agg_row = AggRow(group=group_data, data=_extract_row_data(row))
                agg_rows.append(agg_row)
                if verbose:
                    _log_tx(session, f"[auth]   → AggRow group={agg_row.group} data={agg_row.data}")
        else:
            # Sin resultados: una fila vacía para queries sin group_by, ninguna para grouped
            if not group_raw_exprs:
                empty_data = {f"{op}_{f}": (0 if op == 'count' else None) for op, m in operations_metadata.items() for f in m["valid_fields"]}
                agg_rows.append(AggRow(group={}, data=empty_data))

        _log_commit(session, f"[auth] ✅ Agregaciones RowLevelSecurity completadas: {len(agg_expressions)} expresiones, {len(agg_rows)} filas")

        return AggregationResult(
            success=True,
            rows=agg_rows,
            group_by=group_field_names,
            processed_fields=all_valid_fields,
            warnings=warnings,
            errors=errors,
            metadata={
                "total_operations":  len(request.aggregations),
                "valid_operations":  len(operations_metadata),
                "total_expressions": len(agg_expressions),
                "operations_summary": operations_metadata,
            }
        )

"""
# utils.py
# Módulo de utilidades para DAOs generados por tai-sql
# Contiene decoradores para manejo de errores (sync/async), carga de relaciones y opciones de carga optimizadas
"""
import functools
from pydantic import BaseModel
from typing import (
    Any,
    List,
    Union,
    Dict,
    Optional
)
from sqlalchemy import exc
from sqlalchemy.orm import (
    Session,
    Mapper,
    class_mapper,
    selectinload,
    joinedload,
)
from sqlalchemy.ext.asyncio import AsyncSession
from tai_alphi import Alphi

from ..._base import Base

# Logger
logger = Alphi.get_logger_by_name("agendarte-api")

class PrettyModel(BaseModel):
    def __str__(self):
        try:
            from rich.console import Console
            from rich.syntax import Syntax
            console = Console()
            json_str = self.model_dump_json(indent=2)
            syntax = Syntax(json_str, "json", theme="ansi_dark", line_numbers=False)
            with console.capture() as capture:
                console.print(syntax)
            return capture.get()
        except ImportError:
            # Fallback si rich no está disponible
            return self.model_dump_json(indent=2)
        except Exception as e:
            return str(e)

def _log_tx(session: Union[Session, AsyncSession, None], msg: str) -> None:
    """Emite log inmediato. En sesión compartida usa prefijo [tx]; en standalone emite directamente."""
    if session is not None:
        logger.info(f"   ↳ [tx] {msg}")
    else:
        logger.info(msg)


def _log_commit(session: Union[Session, AsyncSession, None], msg: str) -> None:
    """Buferea un log de éxito en sesión compartida para emitirlo tras el commit.
    En standalone (session=None) emite directamente."""
    if session is None:
        logger.info(msg)
    elif session.in_transaction():
        session.info.setdefault('_log_buffer', []).append(msg)
    else:
        logger.info(msg)


def _discard_log_buffer(session: Union[Session, AsyncSession, None]) -> None:
    """Descarta logs de éxito buffereados tras un error."""
    if session is not None and hasattr(session, 'info'):
        session.info.pop('_log_buffer', None)


# ═══════════════════════════════════════════════════════════════════════════════
# Error handling — DBAPI-aware error classification
# ═══════════════════════════════════════════════════════════════════════════════
#
# SQLAlchemy wraps the raw DBAPI exceptions (psycopg2, asyncpg, pymysql, pyodbc…)
# in its own hierarchy.  The original DBAPI error lives in `e.orig`.
# We extract and classify that to produce actionable log messages.

def _extract_dbapi_detail(e: exc.SQLAlchemyError) -> str:
    """
    Extract the most useful error message from a SQLAlchemy-wrapped DBAPI exception.

    Prefers `e.orig` (the raw driver exception) for clarity.
    Falls back to the SQLAlchemy wrapper message if `orig` is not available.
    """
    if hasattr(e, 'orig') and e.orig is not None:
        # asyncpg stores structured info in .detail / .message
        orig = e.orig
        if hasattr(orig, 'detail') and orig.detail:
            return f"{orig} — {orig.detail}"
        return str(orig)
    return str(e)


def _classify_integrity_error(dbapi_msg: str) -> str:
    """
    Classify an IntegrityError by inspecting the DBAPI message.

    Returns a human-readable tag for the violation type.
    Works across PostgreSQL (psycopg2/asyncpg), MySQL, and SQLite.
    """
    msg = dbapi_msg.lower()

    # Unique / duplicate key
    if any(k in msg for k in ('unique', 'duplicate key', 'duplicate entry')):
        return 'duplicate'

    # Foreign key
    if any(k in msg for k in ('foreign key', 'foreign_key', 'fk constraint',
                               'violates foreign key', 'cannot add or update a child row')):
        return 'foreign_key'

    # Not-null
    if any(k in msg for k in ('not null', 'not-null', 'null value in column',
                               'cannot be null')):
        return 'not_null'

    # Check constraint
    if any(k in msg for k in ('check constraint', 'check_violation',
                               'violates check constraint')):
        return 'check'

    # Exclusion constraint (PostgreSQL)
    if 'exclusion' in msg:
        return 'exclusion'

    return 'unknown'


_INTEGRITY_LABELS = {
    'duplicate':   'registro duplicado',
    'foreign_key': 'violación de clave foránea',
    'not_null':    'campo obligatorio sin valor',
    'check':       'violación de restricción CHECK',
    'exclusion':   'violación de restricción de exclusión',
    'unknown':     'error de integridad',
}


def _handle_dao_error(
    e: Exception,
    operation: str,
    model: str,
    session=None,
) -> None:
    """
    Unified error handler for both sync and async DAO decorators.

    Classifies DBAPI-level errors (integrity, operational, data, programming)
    and emits structured log messages.  Always discards the buffered success logs.

    This function does NOT re-raise — the caller re-raises after calling it.
    """
    _discard_log_buffer(session)
    prefix = f"[auth]"

    # ── ORM-level: no rows ──────────────────────────────────────────────────
    if isinstance(e, exc.NoResultFound):
        logger.warning(f"{prefix} ⚠️ {model}.{operation}: registro no encontrado")
        return

    # ── IntegrityError — constraint violations ──────────────────────────────
    if isinstance(e, exc.IntegrityError):
        detail = _extract_dbapi_detail(e)
        tag = _classify_integrity_error(detail)
        label = _INTEGRITY_LABELS[tag]
        logger.error(f"{prefix} ❌ {model}.{operation}: {label} — {detail}")
        return

    # ── OperationalError — connection / deadlock / timeout ──────────────────
    if isinstance(e, exc.OperationalError):
        detail = _extract_dbapi_detail(e)
        msg_lower = detail.lower()

        if any(k in msg_lower for k in ('deadlock', 'lock timeout', 'lock wait')):
            logger.error(f"{prefix} 🔒 {model}.{operation}: deadlock detectado — {detail}")
        elif any(k in msg_lower for k in ('timeout', 'canceling statement', 'statement_timeout')):
            logger.error(f"{prefix} ⏱️ {model}.{operation}: timeout — {detail}")
        elif any(k in msg_lower for k in ('connection', 'server closed', 'broken pipe',
                                           'connection refused', 'connection reset',
                                           'ssl', 'could not connect')):
            logger.error(f"{prefix} 🔌 {model}.{operation}: error de conexión — {detail}")
        else:
            logger.error(f"{prefix} ❌ {model}.{operation}: error operacional — {detail}")
        return

    # ── DataError — bad values from the driver ──────────────────────────────
    if isinstance(e, exc.DataError):
        detail = _extract_dbapi_detail(e)
        logger.error(f"{prefix} 📊 {model}.{operation}: datos inválidos — {detail}")
        return

    # ── ProgrammingError — SQL / schema problems ───────────────────────────
    if isinstance(e, exc.ProgrammingError):
        detail = _extract_dbapi_detail(e)
        logger.error(f"{prefix} 🐛 {model}.{operation}: error de programación — {detail}")
        return

    # ── Catch-all SQLAlchemy ────────────────────────────────────────────────
    if isinstance(e, exc.SQLAlchemyError):
        detail = _extract_dbapi_detail(e)
        logger.error(f"{prefix} ❌ {model}.{operation}: {detail}")
        return

    # ── Escritura anidada que no casa con su padre ──────────────────────────
    # Es la petición la que no vale, no un fallo: un aviso, y no un error en cada uno de
    # los niveles por los que sube.
    if getattr(e, 'tai_nested_write', False):
        logger.warning(f"{prefix} ⚠️ {model}.{operation}: {e.field}: {e}")
        return

    # ── Non-DB exception ────────────────────────────────────────────────────
    logger.error(f"{prefix} ❌ {model}.{operation}: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# Decorators
# ═══════════════════════════════════════════════════════════════════════════════

def sync_error_handler(func):
    """Decorador de errores para métodos DAO síncronos (@classmethod)."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            cls = args[0] if args else None
            model = (cls.__name__ if cls else 'Unknown').removesuffix('SyncDAO')
            _handle_dao_error(e, func.__name__, model, kwargs.get('session'))
            raise e from None

    return wrapper


def async_error_handler(func):
    """Decorador de errores para métodos DAO asíncronos (@classmethod)."""

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            cls = args[0] if args else None
            model = (cls.__name__ if cls else 'Unknown').removesuffix('AsyncDAO')
            _handle_dao_error(e, func.__name__, model, kwargs.get('session'))
            raise e from None

    return wrapper

def should_include_relation(relation_name: str, includes: List[str]) -> bool:
    """
    Determina si una relación debe ser incluida basándose en la lista de includes.
    
    Args:
        relation_name: Nombre de la relación a verificar
        includes: Lista de relaciones a incluir
        
    Returns:
        bool: True si la relación debe incluirse
    """
    return any(
        include == relation_name or include.startswith(f"{relation_name}.")
        for include in includes
    )

def get_nested_includes(relation_name: str, includes: List[str]) -> List[str]:
    """
    Extrae las relaciones anidadas para una relación específica.
    
    Args:
        relation_name: Nombre de la relación padre
        includes: Lista completa de includes
        
    Returns:
        List[str]: Lista de includes anidados para la relación
        
    Example:
        includes = ['author', 'author.posts', 'author.posts.comments']
        get_nested_includes('author', includes) -> ['posts', 'posts.comments']
    """
    nested = []
    prefix = f"{relation_name}."
    
    for include in includes:
        if include.startswith(prefix):
            # Remover el prefijo y añadir a nested
            nested_path = include[len(prefix):]
            nested.append(nested_path)
    
    return nested

def get_loading_options(model_class, includes: Optional[List[str]] = None) -> List[Any]:
    """
    Genera las opciones de carga optimizadas para SQLAlchemy basándose en los includes.
    
    Usa RELATION_LOADING_STRATEGIES (generado estáticamente desde las definiciones del esquema)
    para decidir la estrategia de carga óptima:
      - one-to-many / many-to-many → selectinload (evita multiplicación de filas)
      - many-to-one / one-to-one   → joinedload  (un solo JOIN, más eficiente)
    
    Args:
        model_class: Clase del modelo SQLAlchemy base
        includes: Lista de relaciones a incluir (formato: 'relation' o 'relation.nested')
        
    Returns:
        List[Any]: Lista de opciones de carga (joinedload/selectinload)
    """
    if not includes:
        return []
    
    model_name = model_class.__name__
    
    options = []
    processed = set()
    
    for include_path in includes:
        if include_path in processed:
            continue
        
        parts = include_path.split('.')
        current_model = model_class
        current_model_name = model_name
        current_option = None
        
        for i, part in enumerate(parts):
            if not hasattr(current_model, part):
                break
            
            relation_attr = getattr(current_model, part)
            current_strategies = RELATION_LOADING_STRATEGIES.get(current_model_name, {})
            direction = current_strategies.get(part, 'one-to-many')
            
            # selectinload para 1:N/M:N, joinedload para N:1/1:1
            use_selectin = direction in ('one-to-many', 'many-to-many')
            
            if i == 0:
                current_option = selectinload(relation_attr) if use_selectin else joinedload(relation_attr)
            else:
                if current_option is not None:
                    current_option = current_option.selectinload(relation_attr) if use_selectin else current_option.joinedload(relation_attr)
            
            # Avanzar al modelo destino para relaciones anidadas
            if hasattr(relation_attr, 'mapper'):
                current_model = relation_attr.mapper.class_
                current_model_name = current_model.__name__
        
        if current_option is not None:
            options.append(current_option)
            processed.add(include_path)
    
    return options

def _collect_included_from_mapper(mapper: Mapper, dto: BaseModel, included: set[str]) -> None:
    """
    Recorre recursivamente el mapper y el DTO para recolectar nombres de relaciones
    incluidas, sin acceder a atributos de instancias ORM.
    """
    for attr in mapper.relationships:
        relation_name = attr.key

        if not hasattr(dto, relation_name):
            continue

        subdto = getattr(dto, relation_name)
        if subdto is None:
            continue

        included.add(relation_name)

        target_mapper = attr.mapper
        if isinstance(subdto, list):
            for child_dto in subdto:
                _collect_included_from_mapper(target_mapper, child_dto, included)
        elif isinstance(subdto, BaseModel):
            _collect_included_from_mapper(target_mapper, subdto, included)


def get_included_relations(instance: Any, dto: BaseModel, included: Optional[set[str]] = None) -> set[str]:
    """
    Inspecciona las relaciones presentes en el DTO para construir el set de relaciones
    que fueron proporcionadas en la creación (y por tanto ya están en memoria tras flush).

    No accede a atributos de relación de la instancia ORM, evitando lazy loading.

    Args:
        instance: Objeto ORM (se usa solo para determinar el modelo/mapper).
        dto: DTO que representa los datos creados.
    
    Returns:
        set[str]: Nombres de relaciones incluidas en el DTO.
    """
    if included is None:
        included = set()

    mapper = class_mapper(type(instance))
    _collect_included_from_mapper(mapper, dto, included)

    return included


def get_model_by_name(name: str):
    for mapper in Base.registry.mappers:
        schema_name = mapper.local_table.schema
        table_name = mapper.local_table.name
        full_name = f"{schema_name}.{table_name}"
        if full_name == name:
            return mapper.class_


# Mapa estático de estrategias de carga por modelo y relación
# Generado desde las definiciones del esquema (Relation.info().direction)
RELATION_LOADING_STRATEGIES: Dict[str, Dict[str, str]] = {
    "Realm": {
        "users": "one-to-many",
        "roles": "one-to-many",
        "permissions": "one-to-many",
        "rls_rules": "one-to-many",
    },
    "User": {
        "realm": "many-to-one",
        "user_roles": "one-to-many",
    },
    "Role": {
        "realm": "many-to-one",
        "parent": "many-to-one",
        "subroles": "one-to-many",
        "role_permissions": "one-to-many",
        "user_roles": "one-to-many",
    },
    "Permission": {
        "realm": "many-to-one",
        "role_permissions": "one-to-many",
    },
    "UserRole": {
        "user": "many-to-one",
        "role": "many-to-one",
    },
    "RolePermission": {
        "role": "many-to-one",
        "permission": "many-to-one",
    },
    "RowLevelSecurity": {
        "realm": "many-to-one",
    },
}
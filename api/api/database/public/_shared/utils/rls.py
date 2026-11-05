"""
# rls.py
# Módulo de utilidades para RLS (Row Level Security) en DAOs síncronos
# Implementa reglas RLS robustas, tipadas y optimizadas
"""
import functools
from collections import deque
from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import Decimal, InvalidOperation
from enum import Enum
from uuid import UUID
from typing import (
    Any,
    List,
    Optional,
    Union,
    Type,
    Protocol,
    TypeVar,
    Dict,
    Tuple,
    runtime_checkable
)
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy import and_, false
from sqlalchemy.orm import class_mapper

# Type variables para mejor tipado
ModelType = TypeVar('ModelType')
QueryType = TypeVar('QueryType')

from tai_alphi import Alphi

# Logger
logger = Alphi.get_logger_by_name("agendarte-api")

# ===============================================
# 🔒 RLS (Row Level Security) utilities for DAOs
# ===============================================

class RLSOperator(str, Enum):
    """Operadores soportados para reglas RLS."""
    IN = "in"
    EQ = "eq" 
    NE = "ne"
    GT = "gt"
    GE = "ge"
    LT = "lt"
    LE = "le"
    LIKE = "like"
    ILIKE = "ilike"

@dataclass(frozen=True, slots=True)
class RelationshipPath:
    """
    Representa un camino de relaciones entre dos modelos.
    Inmutable y cacheable por ser frozen y con slots.
    """
    source_model: Type[ModelType]
    target_model: Type[ModelType]
    path: Tuple[str, ...]  # Tupla para ser hashable
    depth: int
    is_direct: bool  # True si source_model == target_model
    
    @property
    def path_str(self) -> str:
        """Representación string del path para debugging."""
        return " → ".join(self.path) if self.path else "DIRECT"
    
    def __str__(self) -> str:
        return f"{self.source_model.__name__} → {self.target_model.__name__} ({self.path_str})"

@runtime_checkable
class RLSRule(Protocol):
    """Protocol que define la interfaz para reglas RLS."""
    
    def applies_to(self, model_cls: Type[ModelType]) -> bool:
        """Determina si esta regla se aplica al modelo dado."""
        ...
    
    def build_predicate(self, model_cls: Type[ModelType]) -> Optional[ColumnElement]:
        """Construye el predicado SQLAlchemy para el modelo."""
        ...
    
    def __str__(self) -> str:
        """Representación string para debugging."""
        ...

@dataclass
class RLS:
    """
    Implementación simple y robusta de RLS.
    
    Características:
    - Tipado fuerte y validación temprana
    - Soporte para múltiples operadores
    - Cacheo automático de paths
    - API clara y extensible
    """
    target_model: Type[ModelType]
    target_column: str
    values: List[Any] | Any
    operator: RLSOperator = RLSOperator.IN
    
    def __post_init__(self):
        """Validación y normalización después de la inicialización."""
            
        # Normalizar valores a lista si es necesario
        if not isinstance(self.values, list):
            if isinstance(self.values, (tuple, set)):
                self.values = list(self.values)
            else:
                self.values = [self.values]

        # NOTA: los valores NO se convierten aquí. La coerción de tipos se hace en
        # RLSPredicateBuilder, donde ya se conoce el tipo real de la columna objetivo.
        # Convertir a ciegas rompía valores como "01" sobre columnas de texto.

    def applies_to(self, model_cls: Type[ModelType]) -> bool:
        """Determina si esta regla se aplica al modelo dado."""
        path = RelationshipPathFinder.find_path(model_cls, self.target_model)
        return path is not None
    
    def build_predicate(self, model_cls: Type[ModelType]) -> Optional[ColumnElement]:
        """Construye el predicado SQLAlchemy para el modelo."""
        return RLSPredicateBuilder.build_predicate(
            model_cls, 
            self.target_model, 
            self.target_column,
            self.values, 
            self.operator
        )
    
    def __str__(self) -> str:
        return f"{self.target_model.__name__}.{self.target_column} {self.operator.value} {self.values}"

@dataclass(frozen=True)
class ParentScope:
    """
    Acota una escritura anidada a los hijos de **un** registro: `<fk> = <valor>` por cada
    columna de la unión, sobre la propia tabla del hijo.

    Es una regla más de la lista `rls`, y por eso vale igual para el `select` que busca la
    fila y para el `UPDATE`/`DELETE` que la escribe, por los dos caminos y en los dos
    paradigmas, sin un parámetro nuevo en `update()` ni en `delete()`. A diferencia de
    `RLS`, **no sigue relaciones**: solo se aplica a su modelo exacto, así que no acota a
    los nietos (que reciben la suya) ni, en una relación de una tabla consigo misma, a
    la fila equivocada.
    """
    model: Type[ModelType]
    values: Tuple[Tuple[str, Any], ...]

    def applies_to(self, model_cls: Type[ModelType]) -> bool:
        return model_cls is self.model

    def build_predicate(self, model_cls: Type[ModelType]) -> Optional[ColumnElement]:
        return and_(*(getattr(model_cls, column) == value for column, value in self.values))

    def __str__(self) -> str:
        joined = ', '.join(f'{column}={value!r}' for column, value in self.values)
        return f"{self.model.__name__} bajo ({joined})"


def scope_to_parent(
    rls: Union[RLSRule, List[RLSRule], None],
    model: Type[ModelType],
    values: Dict[str, Any],
) -> List[RLSRule]:
    """
    Las reglas con las que un DAO escribe un hijo anidado: las del usuario, que bajan
    intactas, y el `ParentScope` de este padre en lugar del que trajera el nivel de arriba.
    """
    rules = [] if rls is None else (list(rls) if isinstance(rls, list) else [rls])
    rules = [rule for rule in rules if not isinstance(rule, ParentScope)]
    rules.append(ParentScope(model, tuple(values.items())))
    return rules


class RelationshipPathFinder:
    """
    Buscador optimizado de caminos entre modelos con cacheo inteligente.
    """
    
    _path_cache: Dict[Tuple[Type, Type], Optional[RelationshipPath]] = {}
    
    @classmethod
    @functools.lru_cache(maxsize=1024)
    def find_path(
        cls, 
        source_model: Type[ModelType], 
        target_model: Type[ModelType],
        max_depth: int = 20
    ) -> Optional[RelationshipPath]:
        """
        Encuentra el camino más corto entre dos modelos usando BFS.
        
        Args:
            source_model: Modelo origen
            target_model: Modelo destino  
            max_depth: Profundidad máxima de búsqueda
            
        Returns:
            RelationshipPath si existe conexión, None caso contrario
        """
        # Caso directo: mismo modelo
        if source_model is target_model:
            return RelationshipPath(
                source_model=source_model,
                target_model=target_model,
                path=(),
                depth=0,
                is_direct=True
            )
        
        # Búsqueda BFS para encontrar el camino más corto
        queue = deque([(source_model, ())])
        visited = {source_model}
        
        while queue:
            current_model, current_path = queue.popleft()
            
            # Límite de profundidad
            if len(current_path) >= max_depth:
                continue
                
            try:
                mapper = class_mapper(current_model)
            except Exception:
                # Modelo no válido para SQLAlchemy
                continue
            
            for relationship in mapper.relationships:
                # Solo se atraviesan relaciones escalares (many-to-one / one-to-one).
                # Una colección invierte el sentido de la pertenencia: cruzarla
                # convierte «pertenece a X» en «tiene algún hijo relacionado con X»,
                # que en vez de acotar el resultado lo ensancha.
                if relationship.uselist:
                    continue

                next_model = relationship.mapper.class_

                # Evitar ciclos
                if next_model in visited:
                    continue
                    
                next_path = current_path + (relationship.key,)
                
                # ¿Llegamos al destino?
                if next_model is target_model:
                    return RelationshipPath(
                        source_model=source_model,
                        target_model=target_model,
                        path=next_path,
                        depth=len(next_path),
                        is_direct=False
                    )
                
                visited.add(next_model)
                queue.append((next_model, next_path))
        
        # No hay camino
        return None

class RLSPredicateBuilder:
    """
    Constructor de predicados SQLAlchemy con soporte para múltiples operadores.
    """
    
    @staticmethod
    def build_predicate(
        source_model: Type[ModelType],
        target_model: Type[ModelType], 
        target_column: str,
        values: List[Any],
        operator: RLSOperator
    ) -> Optional[ColumnElement]:
        """
        Construye un predicado SQLAlchemy optimizado.
        
        Args:
            source_model: Modelo sobre el que se aplica el filtro
            target_model: Modelo que contiene la columna objetivo
            target_column: Nombre de la columna objetivo
            values: Valores para el filtro
            operator: Operador a aplicar
            
        Returns:
            ColumnElement con el predicado o None si no es posible
        """
        if not values:
            return false()
            
        # Buscar el camino
        path = RelationshipPathFinder.find_path(source_model, target_model)
        if path is None:
            return None
            
        # Obtener la columna objetivo
        try:
            target_col = getattr(target_model, target_column)
        except AttributeError:
            logger.error(f"[public] Column {target_column} not found in {target_model.__name__}")
            return None

        # Adaptar los valores al tipo real de la columna
        values = RLSPredicateBuilder._coerce_values(target_col, values)

        # Construir predicado base según el operador
        base_predicate = RLSPredicateBuilder._build_base_predicate(
            target_col, values, operator
        )
        if base_predicate is None:
            return None
            
        # Si es directo (mismo modelo), devolver predicado base
        if path.is_direct:
            return base_predicate
            
        # Construir predicado con relaciones
        return RLSPredicateBuilder._build_relationship_predicate(
            source_model, path.path, base_predicate
        )
    
    @staticmethod
    def _column_python_type(column: ColumnElement) -> Optional[type]:
        """Obtiene el tipo Python de la columna, o None si no se puede determinar."""
        try:
            return column.type.python_type
        except (AttributeError, NotImplementedError):
            return None

    @staticmethod
    def _coerce_values(column: ColumnElement, values: List[Any]) -> List[Any]:
        """
        Adapta los valores al tipo Python de la columna objetivo.

        Los valores suelen llegar como strings (atributos del token), así que una
        columna Integer necesita "1" → 1. Lo que no debe ocurrir es la conversión a la
        inversa: sobre una columna de texto, "01" tiene que seguir siendo "01".
        """
        python_type = RLSPredicateBuilder._column_python_type(column)
        if python_type is None:
            return values

        coerced = [RLSPredicateBuilder._coerce_value(value, python_type) for value in values]
        if coerced != values:
            logger.debug(f"[public] RLS values coerced to {python_type.__name__}: {values} → {coerced}")
        return coerced

    @staticmethod
    def _coerce_value(value: Any, python_type: type) -> Any:
        """Convierte un valor al tipo Python indicado; lo deja intacto si no es posible."""
        if value is None:
            return value

        try:
            if python_type is bool:
                if isinstance(value, bool):
                    return value
                if isinstance(value, str):
                    normalized = value.strip().lower()
                    if normalized in ("true", "t", "yes", "y", "1"):
                        return True
                    if normalized in ("false", "f", "no", "n", "0"):
                        return False
                    return value
                return bool(value) if isinstance(value, int) else value

            # Ya es del tipo esperado: no tocar (p.ej. "01" sobre una columna de texto)
            if isinstance(value, python_type):
                return value

            if python_type is str:
                return str(value)
            if python_type is int:
                return int(str(value).strip())
            if python_type is float:
                return float(str(value).strip())
            if python_type is Decimal:
                return Decimal(str(value).strip())
            if python_type is UUID:
                return UUID(str(value).strip())
            if python_type is datetime:
                return datetime.fromisoformat(str(value).strip())
            if python_type is date:
                return date.fromisoformat(str(value).strip())
            if python_type is time:
                return time.fromisoformat(str(value).strip())
        except (TypeError, ValueError, InvalidOperation):
            logger.warning(f"[public] Could not coerce RLS value {value!r} to {python_type.__name__}")

        return value

    @staticmethod
    def _build_base_predicate(
        column: ColumnElement,
        values: List[Any],
        operator: RLSOperator
    ) -> Optional[ColumnElement]:
        """Construye el predicado base según el operador."""
        try:
            if operator == RLSOperator.IN:
                return column.in_(values)
            elif operator == RLSOperator.EQ:
                return column == values[0] if len(values) == 1 else column.in_(values)
            elif operator == RLSOperator.NE:
                return column != values[0] if len(values) == 1 else ~column.in_(values)
            elif operator == RLSOperator.GT:
                return column > values[0]
            elif operator == RLSOperator.GE:
                return column >= values[0]
            elif operator == RLSOperator.LT:
                return column < values[0]
            elif operator == RLSOperator.LE:
                return column <= values[0]
            elif operator == RLSOperator.LIKE:
                return column.like(values[0])
            elif operator == RLSOperator.ILIKE:
                return column.ilike(values[0])
            else:
                logger.error(f"[public] Unsupported RLS operator: {operator}")
                return None
        except Exception as e:
            logger.error(f"[public] Error building base predicate: {e}")
            return None
    
    @staticmethod
    def _build_relationship_predicate(
        source_model: Type[ModelType],
        path: Tuple[str, ...], 
        base_predicate: ColumnElement
    ) -> Optional[ColumnElement]:
        """
        Construye predicado siguiendo el camino de relaciones.
        
        Algoritmo más simple: construir desde el final hacia el inicio
        sin necesidad de reverse, navegando correctamente los modelos.
        """
        try:
            # Construir desde el final del path hacia el inicio
            current_predicate = base_predicate
            
            # Para path ("company", "department"):
            # 1. Empezar desde Company.department.has(base_predicate) 
            # 2. Luego User.company.has(resultado_anterior)
            
            for i in range(len(path)):
                # Índice desde el final: len-1, len-2, ..., 0
                path_index = len(path) - 1 - i
                relation_key = path[path_index]
                
                # Determinar el modelo actual navegando desde source_model
                current_model = source_model
                for j in range(path_index):
                    rel_attr = getattr(current_model, path[j])
                    current_model = rel_attr.property.mapper.class_
                
                # Obtener la relación y aplicar .has() / .any()
                # `has()` no está implementado para colecciones. Hoy `find_path` ya
                # no devuelve caminos con colecciones, así que esta rama no debería
                # dispararse; se deja porque una excepción aquí se traduce en un
                # `None` que antes dejaba la consulta sin filtrar.
                relation_attr = getattr(current_model, relation_key)
                if relation_attr.property.uselist:
                    current_predicate = relation_attr.any(current_predicate)
                else:
                    current_predicate = relation_attr.has(current_predicate)
                    
            return current_predicate
            
        except Exception as e:
            logger.error(f"[public] Error building relationship predicate: {e}")
            return None

class RLSQueryApplicator:
    """
    Aplicador de reglas RLS a queries con soporte para múltiples reglas y debugging.
    """
    
    @staticmethod
    def apply_rls(
        query: QueryType, 
        model_cls: Type[ModelType], 
        rls_rules: Union[RLSRule, List[RLSRule], None]
    ) -> QueryType:
        """
        Aplica una o múltiples reglas RLS a una query.
        
        Args:
            query: Query SQLAlchemy
            model_cls: Modelo sobre el que se aplica
            rls_rules: Regla(s) RLS a aplicar
            
        Returns:
            Query modificada con las reglas RLS aplicadas
        """
        if rls_rules is None:
            return query
            
        # Normalizar a lista
        rules = rls_rules if isinstance(rls_rules, list) else [rls_rules]
        
        # Aplicar cada regla
        for rule in rules:
            if not rule.applies_to(model_cls):
                continue
                
            predicate = rule.build_predicate(model_cls)

            # Si la regla aplica pero no se puede traducir a SQL, se deniega.
            # Ignorarla dejaba la consulta sin ese filtro y devolvía filas de más
            # sin que nada fallase: un filtro de seguridad falla en cerrado.
            if predicate is None:
                logger.error(
                    f"[public] RLS rule ({rule}) applies to {model_cls.__name__} "
                    f"but could not be built — denying"
                )
                return query.where(false())

            logger.info(f"[public] Applying RLS to {model_cls.__name__}")
            logger.info(f"[public]     Rule: {rule}")
            query = query.where(predicate)

        return query
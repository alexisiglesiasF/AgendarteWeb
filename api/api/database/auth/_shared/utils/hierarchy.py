# Este archivo ha sido generado automáticamente por tai-sql
# No modifiques este archivo directamente

"""
Hierarchy utilities — CTE-based recursive queries for self-referencing tables.

Provides `HierarchyResolver`, a reusable engine that builds WITH RECURSIVE queries
and assembles nested tree structures from flat results.

A node is identified by its key, which may span several columns: in a tree whose
parent is `(message_id, padre) → (message_id, call_id)`, the key of a node is
`(message_id, call_id)`. Internally every key is a tuple, also when it has a
single column.

Las reglas `rls` del `find_many` se aplican a cada nodo, en las dos partes del CTE: lo que
la regla no alcanza no sale y no se atraviesa, así que tampoco se llega a lo que cuelga de
ello. Una raíz fuera de la regla da un árbol vacío.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from sqlalchemy import and_, literal, or_, select
from sqlalchemy.orm import Session, aliased
from sqlalchemy.ext.asyncio import AsyncSession
from .funcs import get_loading_options
from .rls import RLSQueryApplicator

from tai_alphi import Alphi

logger = Alphi.get_logger_by_name("agendarte-api")


#: Hasta dónde baja una consulta en árbol cuando no se pide `tree_depth`. Es holgado para
#: cualquier jerarquía real y corta pronto un ciclo —una fila que acaba colgando de sí
#: misma—, que una clave ajena no impide y con el que la consulta no terminaría nunca.
DEFAULT_TREE_DEPTH = 100


# ─────────────────────────────────────────────────────────────────────────────
# Types
# ─────────────────────────────────────────────────────────────────────────────

T = TypeVar("T")  # SQLAlchemy model type
D = TypeVar("D")  # DTO type

Key = Tuple[Any, ...]


class TreeMode(str, Enum):
    """Modos de consulta jerárquica."""
    FLAT = "flat"
    DESCENDANTS = "descendants"
    ANCESTORS = "ancestors"
    FULL_TREE = "full_tree"


@dataclass(frozen=True)
class HierarchyConfig:
    """
    Configuración inmutable de la jerarquía para un modelo.

    Attributes:
        model_class: La clase SQLAlchemy del modelo.
        key_columns: Columnas que identifican un nodo (ej: ('message_id', 'call_id')).
        parent_columns: Columnas que apuntan al padre, en el mismo orden
            (ej: ('message_id', 'padre')). Una fila con alguna vacía es una raíz.
    """
    model_class: Any
    key_columns: Tuple[str, ...]
    parent_columns: Tuple[str, ...]

    # ── Claves ───────────────────────────────────────────────────────────

    def key(self, obj: Any) -> Key:
        """La clave de un nodo, de una instancia o de un DTO."""
        return tuple(getattr(obj, c) for c in self.key_columns)

    def parent_key(self, obj: Any) -> Optional[Key]:
        """La clave del padre, o None si la fila es una raíz."""
        values = tuple(getattr(obj, c) for c in self.parent_columns)
        return None if any(v is None for v in values) else values

    def root_key(self, value: Any) -> Key:
        """
        La clave de un `tree_root`, en la forma que la use quien llama.

        Un valor suelto si la clave es de una columna; una tupla en el orden de
        `key_columns` o un dict por nombre si es compuesta.
        """
        columns = ', '.join(self.key_columns)
        if isinstance(value, dict):
            missing = [c for c in self.key_columns if c not in value]
            if missing:
                raise ValueError(
                    f"tree_root necesita las columnas ({columns}); falta: {', '.join(missing)}"
                )
            return tuple(value[c] for c in self.key_columns)
        if isinstance(value, (tuple, list)):
            if len(value) != len(self.key_columns):
                raise ValueError(
                    f"tree_root necesita {len(self.key_columns)} valores, uno por columna "
                    f"({columns}); se pasaron {len(value)}"
                )
            return tuple(value)
        if len(self.key_columns) == 1:
            return (value,)
        raise ValueError(
            f"La clave de un nodo es compuesta: pasa tree_root como una tupla ({columns}) "
            f"o como un dict con esas claves"
        )

    # ── Condiciones SQL ──────────────────────────────────────────────────

    def key_in(self, keys: Sequence[Key]):
        """Las filas cuya clave está entre `keys`."""
        model = self.model_class
        if len(self.key_columns) == 1:
            return getattr(model, self.key_columns[0]).in_([k[0] for k in keys])
        # `or_` de igualdades y no un `tuple_(...).in_(...)`: SQL Server no admite
        # comparar filas con IN.
        return or_(*(
            and_(*(getattr(model, c) == v for c, v in zip(self.key_columns, key)))
            for key in keys
        ))

    def is_child_of(self, cte):
        """Las filas del modelo que cuelgan de una fila del CTE."""
        model = self.model_class
        return and_(*(
            getattr(model, parent) == getattr(cte.c, key)
            for parent, key in zip(self.parent_columns, self.key_columns)
        ))

    def is_parent_of(self, cte):
        """Las filas del modelo de las que cuelga una fila del CTE."""
        model = self.model_class
        return and_(*(
            getattr(model, key) == getattr(cte.c, parent)
            for parent, key in zip(self.parent_columns, self.key_columns)
        ))

    def is_same_node(self, cte):
        """La fila del modelo que es la del CTE."""
        model = self.model_class
        return and_(*(getattr(model, c) == getattr(cte.c, c) for c in self.key_columns))


@dataclass
class TreeNode(Generic[D]):
    """
    Nodo del árbol con DTO y metadatos de profundidad.

    Attributes:
        dto: El DTO de lectura del registro.
        pk: Clave del nodo, como tupla.
        parent_ref: Clave del padre, o None si es raíz.
        level: Profundidad en el árbol (0 = nodo raíz de la consulta).
    """
    dto: D
    pk: Key
    parent_ref: Optional[Key]
    level: int = 0


# ─────────────────────────────────────────────────────────────────────────────
# HierarchyResolver
# ─────────────────────────────────────────────────────────────────────────────

class HierarchyResolver(Generic[T, D]):
    """
    Motor de consultas jerárquicas basado en CTEs recursivos.

    Uso desde el DAO generado:

        resolver = HierarchyResolver(
            config=HierarchyConfig(
                ToolCall,
                key_columns=('message_id', 'call_id'),
                parent_columns=('message_id', 'padre'),
            ),
            dto_factory=lambda instance, includes, max_depth: ToolCallRead.from_instance(instance, includes, max_depth),
            rls=rls,
        )

        results = resolver.resolve(
            session=session,
            root_ids=[(7, 'call_1')],
            mode=TreeMode.DESCENDANTS,
            max_depth=None,
            includes=None,
            dto_max_depth=5,
        )

    El resolver:
    1. Construye un CTE recursivo (descendants, ancestors, o ambos).
    2. Ejecuta la query y obtiene filas planas con _tree_level.
    3. Ensambla la estructura anidada (descendants/ancestors en cada DTO).
    """

    __slots__ = ('config', 'dto_factory', 'rls')

    def __init__(
        self,
        config: HierarchyConfig,
        dto_factory: Callable[..., D],
        rls: Any = None,
    ):
        self.config = config
        self.dto_factory = dto_factory
        # las reglas del find_many: acotan cada nodo, no solo las raíces
        self.rls = rls

    # ── Public API ───────────────────────────────────────────────────────

    def resolve(
        self,
        session: Session,
        root_ids: List[Key],
        mode: TreeMode,
        max_depth: Optional[int] = None,
        includes: Optional[List[str]] = None,
        dto_max_depth: int = 5,
    ) -> List[D]:
        """
        Ejecuta la consulta jerárquica y retorna DTOs con árbol anidado.

        Args:
            session: Sesión SQLAlchemy activa.
            root_ids: Claves de los nodos raíz, como tuplas.
            mode: Modo de consulta (descendants, ancestors, full_tree).
            max_depth: Profundidad máxima de recursión. None = hasta DEFAULT_TREE_DEPTH,
                con un aviso en el log si el árbol sigue más abajo.
            includes: Relaciones a incluir en from_instance.
            dto_max_depth: max_depth para from_instance.

        Returns:
            Lista de DTOs raíz con descendants/ancestors poblados.
        """
        if not root_ids:
            return []

        desc_rows: List[Tuple[Any, int]] = []
        anc_rows: List[Tuple[Any, int]] = []

        if mode in (TreeMode.DESCENDANTS, TreeMode.FULL_TREE):
            desc_rows = self._fetch_descendants(session, root_ids, max_depth, includes)

        if mode in (TreeMode.ANCESTORS, TreeMode.FULL_TREE):
            anc_rows = self._fetch_ancestors(session, root_ids, max_depth, includes)

        return self._assemble(mode, desc_rows, anc_rows, root_ids, includes, dto_max_depth)

    async def resolve_async(
        self,
        session: AsyncSession,
        root_ids: List[Key],
        mode: TreeMode,
        max_depth: Optional[int] = None,
        includes: Optional[List[str]] = None,
        dto_max_depth: int = 5,
    ) -> List[D]:
        """Versión async de resolve."""
        if not root_ids:
            return []

        desc_rows: List[Tuple[Any, int]] = []
        anc_rows: List[Tuple[Any, int]] = []

        if mode in (TreeMode.DESCENDANTS, TreeMode.FULL_TREE):
            desc_rows = await self._fetch_descendants_async(session, root_ids, max_depth, includes)

        if mode in (TreeMode.ANCESTORS, TreeMode.FULL_TREE):
            anc_rows = await self._fetch_ancestors_async(session, root_ids, max_depth, includes)

        return self._assemble(mode, desc_rows, anc_rows, root_ids, includes, dto_max_depth)

    def _assemble(
        self,
        mode: TreeMode,
        desc_rows: List[Tuple[Any, int]],
        anc_rows: List[Tuple[Any, int]],
        root_ids: List[Key],
        includes: Optional[List[str]],
        dto_max_depth: int,
    ) -> List[D]:
        """Las filas planas de los dos sentidos, montadas en DTOs anidados."""
        root_id_set = set(root_ids)

        if mode == TreeMode.DESCENDANTS:
            return self._build_descendant_tree(desc_rows, root_id_set, includes, dto_max_depth)
        if mode == TreeMode.ANCESTORS:
            return self._build_ancestor_chain(anc_rows, root_id_set, includes, dto_max_depth)

        # full_tree: merge both directions
        desc_dtos = self._build_descendant_tree(desc_rows, root_id_set, includes, dto_max_depth)
        anc_dtos = self._build_ancestor_chain(anc_rows, root_id_set, includes, dto_max_depth)

        # Attach ancestors to each root
        anc_by_key = {self.config.key(dto): dto for dto in anc_dtos}
        for dto in desc_dtos:
            root_key = self.config.key(dto)
            if root_key in anc_by_key:
                dto.ancestors = anc_by_key[root_key].ancestors

        return desc_dtos

    # ── CTE Construction ─────────────────────────────────────────────────

    def _build_descendants_cte(
        self,
        root_ids: List[Key],
        max_depth: int,
        includes: Optional[List[str]] = None,
    ):
        """
        Construye el CTE recursivo para descendientes.

        SQL equivalente, con la clave (message_id, call_id) y el padre (message_id, padre):
            WITH RECURSIVE _descendants AS (
                SELECT *, 0 AS _tree_level FROM tool_call
                 WHERE (message_id = :m AND call_id = :c) AND <rls>
                UNION ALL
                SELECT h.*, d._tree_level + 1
                FROM tool_call h JOIN _descendants d
                  ON h.message_id = d.message_id AND h.padre = d.call_id
                WHERE d._tree_level < :max_depth AND <rls>
            )
            SELECT * FROM _descendants
        """
        cfg = self.config
        Model = cfg.model_class

        base = RLSQueryApplicator.apply_rls(
            select(Model, literal(0).label("_tree_level")).where(cfg.key_in(root_ids)),
            Model, self.rls,
        )

        cte = base.cte(name="_descendants", recursive=True)

        recursive = RLSQueryApplicator.apply_rls(
            select(Model, (cte.c._tree_level + 1).label("_tree_level"))
            .where(cfg.is_child_of(cte))
            .where(cte.c._tree_level < max_depth),
            Model, self.rls,
        )

        cte = cte.union_all(recursive)

        query = (
            select(Model, cte.c._tree_level)
            .join(cte, cfg.is_same_node(cte))
        )

        if includes:
            loading_options = get_loading_options(Model, includes)
            if loading_options:
                query = query.options(*loading_options)

        return query

    def _build_ancestors_cte(
        self,
        root_ids: List[Key],
        max_depth: int,
        includes: Optional[List[str]] = None,
    ):
        """
        Construye el CTE recursivo para ancestros.

        SQL equivalente, con la clave (message_id, call_id) y el padre (message_id, padre):
            WITH RECURSIVE _ancestors AS (
                SELECT *, 0 AS _tree_level FROM tool_call
                 WHERE (message_id = :m AND call_id = :c) AND <rls>
                UNION ALL
                SELECT p.*, a._tree_level + 1
                FROM tool_call p JOIN _ancestors a
                  ON p.message_id = a.message_id AND p.call_id = a.padre
                WHERE a._tree_level < :max_depth AND <rls>
            )
            SELECT * FROM _ancestors
        """
        cfg = self.config
        Model = cfg.model_class

        base = RLSQueryApplicator.apply_rls(
            select(Model, literal(0).label("_tree_level")).where(cfg.key_in(root_ids)),
            Model, self.rls,
        )

        cte = base.cte(name="_ancestors", recursive=True)

        recursive = RLSQueryApplicator.apply_rls(
            select(Model, (cte.c._tree_level + 1).label("_tree_level"))
            .where(cfg.is_parent_of(cte))
            .where(cte.c._tree_level < max_depth),
            Model, self.rls,
        )

        cte = cte.union_all(recursive)

        query = (
            select(Model, cte.c._tree_level)
            .join(cte, cfg.is_same_node(cte))
        )

        if includes:
            loading_options = get_loading_options(Model, includes)
            if loading_options:
                query = query.options(*loading_options)

        return query

    # ── Query Execution ──────────────────────────────────────────────────

    @staticmethod
    def _depth(max_depth: Optional[int]) -> Tuple[int, bool]:
        """
        Hasta qué nivel baja el CTE, y si hay que mirar uno más para saber si se cortó.

        Con `tree_depth` se baja hasta donde se pidió, sin más. Sin él, hasta
        DEFAULT_TREE_DEPTH, y un nivel más: si ese nivel trae filas, el árbol seguía, y
        cortarlo sin decirlo devolvería un árbol incompleto como si fuera el entero.
        """
        if max_depth is not None:
            return max_depth, False
        return DEFAULT_TREE_DEPTH + 1, True

    def _trim(
        self,
        rows: List[Tuple[Any, int]],
        probed: bool,
        direction: str,
        root_ids: List[Key],
    ) -> List[Tuple[Any, int]]:
        """Quita el nivel de más que se pidió para saber si el árbol seguía, y avisa."""
        if not probed or not any(level > DEFAULT_TREE_DEPTH for _, level in rows):
            return rows

        roots = ', '.join(repr(k if len(k) > 1 else k[0]) for k in root_ids[:3])
        if len(root_ids) > 3:
            roots += f' y {len(root_ids) - 3} más'
        logger.warning(
            f"[{self.config.model_class.__tablename__}] La consulta de {direction} desde "
            f"{roots} pasa de {DEFAULT_TREE_DEPTH} niveles y se ha cortado ahí. Si el árbol "
            f"es así de hondo, pide más con tree_depth=; si no, hay un ciclo: una fila que "
            f"acaba colgando de sí misma"
        )
        return [(instance, level) for instance, level in rows if level <= DEFAULT_TREE_DEPTH]

    def _fetch_descendants(
        self,
        session: Session,
        root_ids: List[Key],
        max_depth: Optional[int],
        includes: Optional[List[str]] = None,
    ) -> List[Tuple[Any, int]]:
        depth, probed = self._depth(max_depth)
        query = self._build_descendants_cte(root_ids, depth, includes)
        result = session.execute(query)
        return self._trim(result.all(), probed, 'descendientes', root_ids)

    def _fetch_ancestors(
        self,
        session: Session,
        root_ids: List[Key],
        max_depth: Optional[int],
        includes: Optional[List[str]] = None,
    ) -> List[Tuple[Any, int]]:
        depth, probed = self._depth(max_depth)
        query = self._build_ancestors_cte(root_ids, depth, includes)
        result = session.execute(query)
        return self._trim(result.all(), probed, 'ancestros', root_ids)

    async def _fetch_descendants_async(
        self,
        session: AsyncSession,
        root_ids: List[Key],
        max_depth: Optional[int],
        includes: Optional[List[str]] = None,
    ) -> List[Tuple[Any, int]]:
        depth, probed = self._depth(max_depth)
        query = self._build_descendants_cte(root_ids, depth, includes)
        result = await session.execute(query)
        return self._trim(result.all(), probed, 'descendientes', root_ids)

    async def _fetch_ancestors_async(
        self,
        session: AsyncSession,
        root_ids: List[Key],
        max_depth: Optional[int],
        includes: Optional[List[str]] = None,
    ) -> List[Tuple[Any, int]]:
        depth, probed = self._depth(max_depth)
        query = self._build_ancestors_cte(root_ids, depth, includes)
        result = await session.execute(query)
        return self._trim(result.all(), probed, 'ancestros', root_ids)

    # ── Tree Assembly ────────────────────────────────────────────────────

    def _build_descendant_tree(
        self,
        rows: List[Tuple[Any, int]],
        root_ids: Set[Key],
        includes: Optional[List[str]],
        dto_max_depth: int,
    ) -> List[D]:
        """
        Ensambla árbol de descendientes desde filas planas del CTE.

        Cada fila es (instance, _tree_level). Los nodos se indexan por su clave
        y se enlazan hijos→padre usando las columnas del padre.
        """
        if not rows:
            return []

        cfg = self.config
        nodes: Dict[Key, TreeNode[D]] = {}

        for row in rows:
            instance, level = row[0], row[1]
            pk = cfg.key(instance)

            # When all keys are passed as root_ids the CTE produces duplicate rows
            # (once from the base case at level 0, once as a descendant at level N).
            # Keep only the deepest occurrence - it reflects the node's actual
            # position in the tree.
            if pk in nodes and level <= nodes[pk].level:
                continue

            dto = self.dto_factory(instance, includes, dto_max_depth)
            dto.tree_level = level
            dto.descendants = []

            nodes[pk] = TreeNode(dto=dto, pk=pk, parent_ref=cfg.parent_key(instance), level=level)

        # Link children to parents.
        # A node is a root only when its parent is absent from the result set -
        # do NOT use root_ids here, because every fetched key is in root_ids when
        # find_many passes all records (which would incorrectly promote every
        # node to a top-level root).
        # A child hangs from a parent one level above it. In a cycle the parent comes
        # back below its child, and linking it would make the DTOs reference each
        # other: serializing them would never end.
        roots: List[D] = []
        for node in nodes.values():
            parent_node = nodes.get(node.parent_ref) if node.parent_ref is not None else None
            if parent_node is None or parent_node.level >= node.level:
                roots.append(node.dto)
            else:
                if parent_node.dto.descendants is None:
                    parent_node.dto.descendants = []
                parent_node.dto.descendants.append(node.dto)

        return roots

    def _build_ancestor_chain(
        self,
        rows: List[Tuple[Any, int]],
        root_ids: Set[Key],
        includes: Optional[List[str]],
        dto_max_depth: int,
    ) -> List[D]:
        """
        Ensambla cadena de ancestros desde filas planas del CTE.

        Cada nodo apunta a su padre a través de ancestors=[parent_dto].
        La cadena es recursiva: nodo.ancestors[0].ancestors[0]... hasta la raíz.
        """
        if not rows:
            return []

        cfg = self.config
        nodes: Dict[Key, TreeNode[D]] = {}

        for row in rows:
            instance, level = row[0], row[1]
            pk = cfg.key(instance)

            # In a cycle a node comes back further up the chain: keep where it first
            # appeared, which is its place in the chain.
            if pk in nodes and level >= nodes[pk].level:
                continue

            dto = self.dto_factory(instance, includes, dto_max_depth)
            dto.tree_level = level
            dto.ancestors = []

            nodes[pk] = TreeNode(dto=dto, pk=pk, parent_ref=cfg.parent_key(instance), level=level)

        # Link each node to its parent as ancestor. The parent is one level above
        # the node; one at or below it is the cycle coming back, and is not linked.
        roots: List[D] = []
        for node in nodes.values():
            if node.pk in root_ids:
                roots.append(node.dto)
            parent_node = nodes.get(node.parent_ref) if node.parent_ref is not None else None
            if parent_node is not None and parent_node.level > node.level:
                node.dto.ancestors = [parent_node.dto]

        return roots
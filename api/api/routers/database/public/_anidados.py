# Generado por tai-api: este fichero lo reescribe `tai-api generate`.
"""
Las escrituras anidadas de `public`: lo que el cuerpo de una petición escribe **en otras
tablas**.

El `<Tabla>Create` lleva las filas relacionadas que se crean con ella (`{"etiquetas": [{…}]}`, o
`{"autor": {…}}` en una many-to-one), y el `<Tabla>UpdateValues`, `create`/`update`/`delete` sobre
las hijas (`{"etiquetas": {"create": […], "update": […], "delete": […]}}`), a cualquier
profundidad. Las aplica el DAO de tai-sql dentro de la escritura del padre, con su misma sesión.

Hasta ahora se escribían **con el permiso del padre**: con `receta-update` se creaban, cambiaban y
borraban `paso_receta` sin ningún permiso sobre esa tabla, y un `update`/`delete` anidado alcanzaba
filas fuera del RLS del usuario. Ahora cada una pide lo que pediría su propio endpoint:

El proyecto no tiene autenticación, así que no hay permisos ni filtrado por fila que exigir:
queda el recorrido del cuerpo.

**Lo que rechaza el DAO** (tai-sql 0.8.0): un `update`/`delete` anidado de una fila que no está bajo
el registro o que el `rls=` no alcanza (`NestedRowNotFound`) es un 404, y un `update` anidado que cambia la unión
del hijo con su padre (`NestedParentMismatch`), un 422, con el `field` del anidado
(`traducir_anidada`, que los endpoints de escritura llaman en los dos modos). Sin traducirlas
serían un 500.

`PATCH /<tabla>` (`update_many`) no las admite: su cuerpo (`_masivos.py`) no lleva relaciones.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, FrozenSet, Iterator, List, Optional, Tuple

from pydantic import BaseModel

from api.resources import APIException, RecordNotFoundException, ValidationException

#: Las relaciones por las que se escribe, por tabla: {relación: (tabla destino, si es una lista,
#: ((columna del destino, columna de la tabla), …), relación inversa)}. Las columnas son las de la
#: unión: una fila del destino está relacionada si `destino.<columna del destino> ==
#: tabla.<columna de la tabla>`. La inversa, cuando es el destino quien lleva la clave foránea (la
#: one-to-many y la one-to-one implícita): la relación del hijo que apunta a esta fila.
RELACIONES: Dict[str, Dict[str, Tuple[str, bool, Tuple[Tuple[str, str], ...], Optional[str]]]] = {
    "usuario": {
        "eventos": ("evento", True, (("usuario_id", "id"), ), "usuario"),
        "proyectos": ("proyecto", True, (("id_usuario", "id"), ), "usuario"),
        "repertorios": ("repertorio", True, (("usuario_id", "id"), ), "usuario"),
    },
    "proyecto": {
        "eventos": ("evento", True, (("id_proyecto", "id"), ), "proyecto"),
        "repertorios": ("repertorio", True, (("id_proyecto", "id"), ), "proyecto"),
        "usuario": ("usuario", False, (("id", "id_usuario"), ), None),
    },
    "evento": {
        "gastos": ("gasto", True, (("id_evento", "id"), ), "evento"),
        "ingresos": ("ingreso", True, (("id_evento", "id"), ), "evento"),
        "proyecto": ("proyecto", False, (("id", "id_proyecto"), ), None),
        "usuario": ("usuario", False, (("id", "usuario_id"), ), None),
    },
    "repertorio": {
        "canciones": ("cancion", True, (("id_repertorio", "id"), ), "repertorio"),
        "proyecto": ("proyecto", False, (("id", "id_proyecto"), ), None),
        "usuario": ("usuario", False, (("id", "usuario_id"), ), None),
    },
    "cancion": {
        "repertorio": ("repertorio", False, (("id", "id_repertorio"), ), None),
    },
    "gasto": {
        "evento": ("evento", False, (("id", "id_evento"), ), None),
    },
    "ingreso": {
        "evento": ("evento", False, (("id", "id_evento"), ), None),
    },
}

#: Las relaciones de `<Tabla>Create`: se crean con la fila.
CREA: Dict[str, FrozenSet[str]] = {
    "usuario": frozenset(["eventos", "proyectos", "repertorios"]),
    "proyecto": frozenset(["eventos", "repertorios", "usuario"]),
    "evento": frozenset(["gastos", "ingresos", "proyecto", "usuario"]),
    "repertorio": frozenset(["canciones", "proyecto", "usuario"]),
    "cancion": frozenset(["repertorio"]),
    "gasto": frozenset(["evento"]),
    "ingreso": frozenset(["evento"]),
}

#: Las relaciones de `<Tabla>UpdateValues`: admiten `create`, `update` y `delete` anidados.
MODIFICA: Dict[str, FrozenSet[str]] = {
    "usuario": frozenset(["eventos", "proyectos", "repertorios"]),
    "proyecto": frozenset(["eventos", "repertorios"]),
    "evento": frozenset(["gastos", "ingresos"]),
    "repertorio": frozenset(["canciones"]),
    "cancion": frozenset([]),
    "gasto": frozenset([]),
    "ingreso": frozenset([]),
}

#: La clave primaria de cada tabla, en el orden del schema.
CLAVES: Dict[str, Tuple[str, ...]] = {
    "usuario": tuple(["id"]),
    "proyecto": tuple(["id"]),
    "evento": tuple(["id"]),
    "repertorio": tuple(["id"]),
    "cancion": tuple(["id"]),
    "gasto": tuple(["id"]),
    "ingreso": tuple(["id"]),
}

#: Cómo se pide un lote de filas por cada columna: `in` (`in_<columna>`), `range`
#: (`min_<columna>`/`max_<columna>`); la que no está no se puede pedir por lote. Es el
#: `filter_fields` del DAO.
FILTROS: Dict[str, Dict[str, str]] = {
    "usuario": {"apellido": "in", "created_at": "range", "created_by": "in", "email": "in", "id": "in", "nombre": "in", "updated_at": "range", "updated_by": "in"},
    "proyecto": {"created_at": "range", "created_by": "in", "descripcion": "in", "id": "in", "id_usuario": "in", "nombre": "in", "tipo": "in", "updated_at": "range", "updated_by": "in"},
    "evento": {"created_at": "range", "created_by": "in", "estado": "in", "fecha": "range", "hora": "range", "id": "in", "id_proyecto": "in", "nombre": "in", "notas": "in", "tipo": "in", "ubicacion": "in", "updated_at": "range", "updated_by": "in", "usuario_id": "in"},
    "repertorio": {"created_at": "range", "created_by": "in", "descripcion": "in", "id": "in", "id_proyecto": "in", "nombre": "in", "updated_at": "range", "updated_by": "in", "usuario_id": "in"},
    "cancion": {"created_at": "range", "created_by": "in", "id": "in", "id_repertorio": "in", "nombre": "in", "updated_at": "range", "updated_by": "in"},
    "gasto": {"concepto": "in", "created_at": "range", "created_by": "in", "id": "in", "id_evento": "in", "importe": "range", "nombre": "in", "updated_at": "range", "updated_by": "in"},
    "ingreso": {"concepto": "in", "created_at": "range", "created_by": "in", "id": "in", "id_evento": "in", "importe": "range", "nombre": "in", "updated_at": "range", "updated_by": "in"},
}

#: El nombre de cada tabla en los mensajes: el de su clase.
NOMBRES: Dict[str, str] = {
    "usuario": "Usuario",
    "proyecto": "Proyecto",
    "evento": "Evento",
    "repertorio": "Repertorio",
    "cancion": "Cancion",
    "gasto": "Gasto",
    "ingreso": "Ingreso",
}


# ── El recorrido del cuerpo ────────────────────────────────────────────────────
#
# Vale para los DTOs ya validados y para el JSON crudo de `_tx`, que se recorre antes de resolver
# los `$ref` (los permisos se comprueban antes de abrir la transacción). Lo que no tiene la forma
# esperada se salta: la validación del DTO lo rechazará después.

def _valor(objeto: Any, nombre: str) -> Any:
    if isinstance(objeto, dict):
        return objeto.get(nombre)
    if isinstance(objeto, BaseModel):
        return getattr(objeto, nombre, None)
    return None


def _es_objeto(valor: Any) -> bool:
    return isinstance(valor, (dict, BaseModel))


def _elementos(valor: Any, lista: bool) -> Iterator[Tuple[str, Any]]:
    """(sufijo de su `field`, elemento): `.0`, `.1`… en una lista; nada en una relación suelta."""
    if lista:
        if isinstance(valor, list):
            for posición, elemento in enumerate(valor):
                yield f".{posición}", elemento
    elif valor is not None:
        yield "", valor


def _cambios(valores: Any, tabla: str) -> Dict[str, Any]:
    """Las columnas que cambia un `<Tabla>UpdateValues`: lo que puede mover su clave primaria."""
    if isinstance(valores, BaseModel) and hasattr(valores, "to_dict"):
        return valores.to_dict()
    if isinstance(valores, dict):
        return {k: v for k, v in valores.items() if k not in MODIFICA.get(tabla, ())}
    return {}


def _clave_de(tabla: str, objeto: Any) -> Dict[str, Any]:
    """La clave de la fila de un `update` anidado: sus columnas, junto a `values`."""
    return {columna: _valor(objeto, columna) for columna in CLAVES[tabla]}


def _clave_borrada(tabla: str, borrada: Any) -> Dict[str, Any]:
    """La clave de un `delete` anidado: el valor, o un objeto con sus columnas si es compuesta."""
    if isinstance(borrada, dict):
        return {columna: borrada.get(columna) for columna in CLAVES[tabla]}
    return {CLAVES[tabla][0]: borrada}


def _fusionar(destino: Dict[str, dict], origen: Dict[str, dict]) -> None:
    for relación, sub in origen.items():
        _fusionar(destino.setdefault(relación, {}), sub)


def _forma(tabla: str, cuerpo: Any) -> Dict[str, dict]:
    """Qué relaciones crea un `<Tabla>Create`, a todos los niveles: {relación: {relación: …}}."""
    forma: Dict[str, dict] = {}
    for relación in sorted(CREA.get(tabla, ())):
        destino, lista = RELACIONES[tabla][relación][:2]
        for _, hijo in _elementos(_valor(cuerpo, relación), lista):
            if _es_objeto(hijo):
                _fusionar(forma.setdefault(relación, {}), _forma(destino, hijo))
    return forma


@dataclass
class Anidada:
    """Una escritura anidada: qué hace, en qué tabla y dónde está en el cuerpo (`field`)."""
    accion: str
    tabla: str
    campo: str
    #: `update` y `delete`: la clave de la fila.
    clave: Optional[Dict[str, Any]] = None
    #: `update`: las columnas que cambia.
    cambios: Dict[str, Any] = field(default_factory=dict)
    #: `create` dentro de un `update`: la fila de la que cuelga (tabla, clave, cambios, relación) y
    #: el `field` de sus `create` (`etiquetas.create`).
    padre: Optional[Tuple[str, Dict[str, Any], Dict[str, Any], str, str]] = None
    #: `create`: las relaciones que crea a su vez, para comprobar después las filas que deja.
    forma: Dict[str, dict] = field(default_factory=dict)


def _sin_inversa(tabla: str, relación: str, hijo: Any, donde: str) -> None:
    """
    Una fila que se crea colgando de otra no crea a su vez la fila de la que cuelga
    (`{"etiquetas": {"create": [{"publicacion": {…}}]}}`): la clave foránea quedaría apuntando a la
    nueva, fuera de la fila bajo la que se pidió, y lo que se comprueba de ella —su propietario— se
    comprobaría sobre la fila equivocada. Es un 422.
    """
    inversa = RELACIONES[tabla][relación][3]
    if inversa is not None and _valor(hijo, inversa) is not None:
        raise ValidationException(
            f"Una fila de {relación} cuelga de esta: no puede crear también la suya ({inversa})",
            f"{donde}.{inversa}",
        )


def en_create(tabla: str, cuerpo: Any, campo: str = "") -> List[Anidada]:
    """Las escrituras anidadas de un `<Tabla>Create` (`POST`, `/bulk`, el `create` de `_tx`)."""
    anidadas: List[Anidada] = []
    for relación in sorted(CREA.get(tabla, ())):
        destino, lista = RELACIONES[tabla][relación][:2]
        for sufijo, hijo in _elementos(_valor(cuerpo, relación), lista):
            if not _es_objeto(hijo):
                continue
            donde = f"{campo}{relación}{sufijo}"
            _sin_inversa(tabla, relación, hijo, donde)
            anidadas.append(Anidada("create", destino, donde, forma=_forma(destino, hijo)))
            anidadas += en_create(destino, hijo, f"{donde}.")
    return anidadas


def en_update(tabla: str, valores: Any, campo: str = "", clave: Optional[Dict[str, Any]] = None) -> List[Anidada]:
    """
    Las escrituras anidadas de un `<Tabla>UpdateValues` (`PATCH /<tabla>/<clave>`, el `update` de
    `_tx`). `clave` es la de la fila que se actualiza: sin ella solo sirven para los permisos.
    """
    anidadas: List[Anidada] = []
    cambios = _cambios(valores, tabla)
    for relación in sorted(MODIFICA.get(tabla, ())):
        destino, lista = RELACIONES[tabla][relación][:2]
        anidado = _valor(valores, relación)
        if not _es_objeto(anidado):
            continue
        base = f"{campo}{relación}."
        padre = (tabla, clave, cambios, relación, f"{base}create") if clave is not None else None
        for sufijo, hijo in _elementos(_valor(anidado, "create"), lista):
            if not _es_objeto(hijo):
                continue
            donde = f"{base}create{sufijo}"
            _sin_inversa(tabla, relación, hijo, donde)
            anidadas.append(Anidada("create", destino, donde, padre=padre, forma=_forma(destino, hijo)))
            anidadas += en_create(destino, hijo, f"{donde}.")
        for sufijo, hijo in _elementos(_valor(anidado, "update"), lista):
            if not _es_objeto(hijo):
                continue
            donde = f"{base}update{sufijo}"
            clave_hija = _clave_de(destino, hijo)
            valores_hijo = _valor(hijo, "values")
            anidadas.append(Anidada(
                "update", destino, donde, clave=clave_hija, cambios=_cambios(valores_hijo, destino),
            ))
            anidadas += en_update(destino, valores_hijo, f"{donde}.values.", clave_hija)
        for sufijo, borrada in _elementos(_valor(anidado, "delete"), lista):
            anidadas.append(Anidada(
                "delete", destino, f"{base}delete{sufijo}", clave=_clave_borrada(destino, borrada),
            ))
    return anidadas


# ── Lo que rechaza el DAO ──────────────────────────────────────────────────────

def traducir_anidada(error: BaseException, prefijo: str = "") -> None:
    """
    Si `error` es el rechazo de una escritura anidada por el DAO, lanza su respuesta; si no, no
    hace nada y quien llama lo relanza (`except Exception as e: traducir_anidada(e); raise`).

    tai-sql #218 (S6) acota las escrituras anidadas al registro que se actualiza y lanza, en vez de
    ignorar lo que no casa, una subclase de `NestedWriteError` con `reason`, `field` (la ruta en el
    cuerpo: `libros.update.0.values.resenas.delete.0`), `table`, `key` y `message`:

    - `reason == "not_found"` (`NestedRowNotFound`): la fila no existe, cuelga de otro registro o el
      RLS no la alcanza. **404 `RECORD_NOT_FOUND`**, el mismo que el endpoint de su tabla y sin
      distinguir los tres casos: distinguirlos delataría lo que la regla oculta.
    - `reason == "parent_mismatch"` (`NestedParentMismatch`): un `update` anidado cambia las
      columnas que unen al hijo con su padre. **422 `VALIDATION_ERROR`** con el mensaje del DAO.

    Se reconocen **por la marca** (`tai_nested_write`), como `resources/` reconoce `t.abort()` por
    `tai_trigger_abort`: cada schema tiene su clase, y con tai-sql 0.7.21 no existe ninguna que
    importar. Sin esto llegaban a `resources/` como una excepción desconocida —un `LookupError` y un
    `ValueError` sin marca—: un 500. `prefijo` es lo que va delante del `field` del DAO, que es
    relativo al cuerpo que recibió: `values.` en `_tx` (el endpoint antepone `operations.<i>`).

    Una `reason` que no se conoce no se traduce: sale como el 500 que es.
    """
    if not getattr(error, "tai_nested_write", False):
        return
    razón = getattr(error, "reason", "")
    campo = getattr(error, "field", None)
    campo = f"{prefijo}{campo}" if campo else (prefijo.rstrip(".") or None)
    if razón == "not_found":
        tabla = getattr(error, "table", "") or ""
        excepcion: APIException = RecordNotFoundException(NOMBRES.get(tabla, tabla or "Registro"))
        excepcion.field = campo
        raise excepcion from None
    if razón == "parent_mismatch":
        raise ValidationException(getattr(error, "message", None) or str(error), campo) from None

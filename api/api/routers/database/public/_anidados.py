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

- **El permiso de su tabla** (`<tabla>-<acción>`, con `sudo`, `<tabla>-admin` y
  `allresources-<acción>`), el de todas **antes de abrir la transacción**: un 403
  `INSUFFICIENT_PERMISSIONS` cuyo `field` dice cuál (`etiquetas.create.0`).
- **Su `owner()`**: un `update` que la saca de lo suyo y un `create` con dueño ajeno son un 403
  `reason: OWNER`, comprobados después de escribir, en la misma transacción. Si algo falla no queda
  nada, el padre incluido.

**Su RLS y que cuelgue de la fila que se actualiza** no se comprueban aquí: los aplica el DAO de
tai-sql (0.8.0), que recibe el `rls=` del endpoint y lo baja a cada `update`/`delete` anidado
acotado al padre. Un hijo que el usuario no alcanza, que no existe o que es de otra fila
(`PATCH /publicacion/1` con `{"etiquetas": {"delete": [{"publicacion_id": 2, …}]}}`) es el mismo
404, a cualquier profundidad y con claves compuestas (abajo, «Lo que rechaza el DAO»).

Con la autorización apagada (`tai-api dev`) no se exige ningún permiso ni regla de propietario,
como en el resto de la API; la fila anidada que no existe sigue siendo un 404.

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

from api.routers.auth import build_owner_rules, owner_violation, require_permission
from api.database.public import public_async_api, RLS
from api.database.public._shared import get_model_by_name
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


# ── La autorización de cada una ────────────────────────────────────────────────

#: El DAO de cada tabla: el mismo que llama su endpoint.
DAOS: Dict[str, Any] = {
    "usuario": public_async_api.usuario,
    "proyecto": public_async_api.proyecto,
    "evento": public_async_api.evento,
    "repertorio": public_async_api.repertorio,
    "cancion": public_async_api.cancion,
    "gasto": public_async_api.gasto,
    "ingreso": public_async_api.ingreso,
}


def _en(excepcion: APIException, campo: str) -> APIException:
    """La excepción con el `field` de la escritura anidada que la causa."""
    excepcion.field = campo
    return excepcion


def exigir_permisos(token: Any, anidadas: List[Anidada], prefijo: str = "") -> None:
    """
    El permiso de la tabla de cada escritura anidada (`<tabla>-<acción>`), con la misma regla que
    `requires_permissions`. Se llama **antes de abrir la transacción**: sin permiso es un 403 sin
    haber tocado la base de datos, y su `field` dice qué escritura lo pidió.
    """
    for anidada in anidadas:
        try:
            require_permission(token, anidada.accion, anidada.tabla)
        except APIException as e:
            raise _en(e, f"{prefijo}{anidada.campo}")


def _propias(token: Any, tabla: str, cache: Dict[str, list]) -> list:
    """Las reglas de propietario que alcanzan a la tabla, como en su endpoint."""
    if tabla not in cache:
        cache[tabla] = build_owner_rules(
            token, "public", get_model_by_name, RLS,
            model=get_model_by_name(f"public.{tabla}"),
        )
    return cache[tabla]


def _alcanza(token: Any, tabla: str, forma: Dict[str, dict], cache: Dict[str, list]) -> bool:
    """Si alguna tabla de lo que crea `forma` desde `tabla` tiene reglas de propietario."""
    for relación, sub in forma.items():
        destino = RELACIONES[tabla][relación][0]
        if _propias(token, destino, cache) or _alcanza(token, destino, sub, cache):
            return True
    return False


def _clave_fila(tabla: str, fila: Any) -> Dict[str, Any]:
    return {columna: getattr(fila, columna) for columna in CLAVES[tabla]}


async def _relacionadas(tabla: str, fila: Any, relación: str, session) -> list:
    """
    Las filas de `relación` de `fila`, leídas de la base de datos en la sesión de la escritura.

    Con una consulta, no con `includes`: una colección que la sesión ya tiene cargada no se vuelve
    a leer, y no vería lo que el DAO acaba de crear.
    """
    destino, _, columnas, _ = RELACIONES[tabla][relación]
    filtro = {columna_destino: getattr(fila, columna_origen) for columna_destino, columna_origen in columnas}
    if any(valor is None for valor in filtro.values()):
        return []
    if set(filtro) == set(CLAVES[destino]):
        encontrada = await DAOS[destino].find(**filtro, session=session)
        return [] if encontrada is None else [encontrada]
    return await DAOS[destino].find_many(**filtro, session=session)


async def _relacionadas_de(tabla: str, filas: List[Any], relación: str, session) -> List[list]:
    """
    `_relacionadas` de varias filas a la vez, en su orden: una consulta con `in_` por cada columna de
    la unión, repartida después por fila. Si alguna columna no tiene `in_`, una consulta por fila.
    """
    destino, _, columnas, _ = RELACIONES[tabla][relación]
    if len(filas) == 1 or any(FILTROS[destino].get(columna_destino) != "in" for columna_destino, _ in columnas):
        return [await _relacionadas(tabla, fila, relación, session) for fila in filas]
    uniones = [tuple(getattr(fila, columna_origen) for _, columna_origen in columnas) for fila in filas]
    con_valor = [union for union in uniones if None not in union]
    if not con_valor:
        return [[] for _ in filas]
    filtro = {
        f"in_{columna_destino}": list({union[i] for union in con_valor})
        for i, (columna_destino, _) in enumerate(columnas)
    }
    por_union: Dict[tuple, list] = {}
    for hija in await DAOS[destino].find_many(**filtro, session=session):
        por_union.setdefault(tuple(getattr(hija, columna_destino) for columna_destino, _ in columnas), []).append(hija)
    return [por_union.get(union, []) for union in uniones]


def _tupla(tabla: str, fila: Any) -> tuple:
    return tuple(getattr(fila, columna) for columna in CLAVES[tabla])


async def _primera_ajena(tabla: str, filas: List[Any], propias: list, session) -> Optional[int]:
    """
    La posición de la primera de `filas` que la regla no alcanza, o `None` si las alcanza todas.

    Una consulta para todas, no una por fila: con una clave simple con `in_`, cuántas de esas claves
    alcanza la regla; si no, las filas que alcanza entre las que acotan la lista o el rango de cada
    columna de la clave (puede traer alguna más; lo que cuenta es que estén todas). La que no aparece
    —ajena, o con un valor que vuelve de la base de datos con otra forma, como una fecha con zona— se
    busca sola con la regla, que es la comprobación exacta: el lote solo ahorra las que confirma.
    """
    if not filas:
        return None
    dao, columnas = DAOS[tabla], CLAVES[tabla]
    if len(columnas) == 1 and FILTROS[tabla].get(columnas[0]) == "in":
        valores = list({getattr(fila, columnas[0]) for fila in filas})
        if await dao.count(**{f"in_{columnas[0]}": valores}, rls=propias, session=session) == len(valores):
            return None
    acotado: Dict[str, Any] = {}
    for columna in columnas:
        valores = [getattr(fila, columna) for fila in filas]
        if FILTROS[tabla].get(columna) == "in":
            acotado[f"in_{columna}"] = list(set(valores))
        elif FILTROS[tabla].get(columna) == "range":
            try:
                acotado[f"min_{columna}"], acotado[f"max_{columna}"] = min(valores), max(valores)
            except TypeError:  # valores que no se comparan entre sí (fechas con y sin zona)
                pass
    alcanzadas = set()
    if acotado:
        alcanzadas = {_tupla(tabla, fila) for fila in await dao.find_many(**acotado, rls=propias, session=session)}
    for posición, fila in enumerate(filas):
        if _tupla(tabla, fila) in alcanzadas:
            continue
        if await dao.find(**_clave_fila(tabla, fila), rls=propias, session=session) is None:
            return posición
    return None


async def _comprobar_filas(token: Any, tabla: str, filas: List[Tuple[Any, Dict[str, dict], str]], session, cache) -> None:
    """
    Filas de `tabla` recién creadas, cada una con lo que se creó con ella (`forma`) y su `field`: tienen
    que ser del usuario (403 `OWNER`), y lo de debajo también. Una consulta por tabla y nivel para
    todas, no una por fila.
    """
    propias = _propias(token, tabla, cache)
    if propias:
        ajena = await _primera_ajena(tabla, [fila for fila, _, _ in filas], propias, session)
        if ajena is not None:
            raise _en(owner_violation(), filas[ajena][2])
    await _bajar(token, tabla, [(fila, forma, f"{campo}.") for fila, forma, campo in filas], session, cache)


async def _bajar(token: Any, tabla: str, padres: List[Tuple[Any, Dict[str, dict], str]], session, cache) -> None:
    """
    Lo que se creó bajo `padres` —filas de `tabla`, con su `forma` y el prefijo del `field` de lo suyo—,
    relación a relación: las hijas de todos los padres en una consulta, y comprobadas todas juntas.
    """
    for relación in sorted({relación for _, forma, _ in padres for relación in forma}):
        destino = RELACIONES[tabla][relación][0]
        con_ella = [(fila, forma[relación], prefijo) for fila, forma, prefijo in padres if relación in forma]
        if not any(_propias(token, destino, cache) or _alcanza(token, destino, sub, cache) for _, sub, _ in con_ella):
            continue
        hijas = await _relacionadas_de(tabla, [fila for fila, _, _ in con_ella], relación, session)
        await _comprobar_filas(token, destino, [
            (hija, sub, f"{prefijo}{relación}")
            for (_, sub, prefijo), suyas in zip(con_ella, hijas)
            for hija in suyas
        ], session, cache)


async def despues_de_crear(token: Any, tabla: str, creada: Any, cuerpo: Any, session, prefijo: str = "") -> None:
    """
    Después de un `create` (`POST`, el `create` de `_tx`), en su transacción: lo que se creó anidado en
    `creada` tiene que ser del usuario. La fila de arriba la comprueba el endpoint.

    Solo cuesta consultas si alguna tabla de lo creado tiene reglas de propietario.
    """
    await _bajar(token, tabla, [(creada, _forma(tabla, cuerpo), prefijo)], session, {})


async def despues_de_crear_varias(token: Any, tabla: str, creadas: List[Any], cuerpos: List[Any], session) -> None:
    """
    Después de `create_many` (`/bulk`), en su transacción: cada fila creada y lo que se creó anidado
    con ella tiene que ser del usuario. El `field` de un 403 lleva la posición en la lista (`3`, o
    `3.etiquetas` si es lo anidado).

    Todo el lote a la vez: una consulta por tabla y nivel, no una por registro. Era un `find` por
    fila, y con mil registros por petición eran mil viajes a la base de datos. Solo cuesta consultas
    si alguna tabla de lo creado tiene reglas de propietario.
    """
    await _comprobar_filas(token, tabla, [
        (creada, _forma(tabla, cuerpo), str(posición))
        for posición, (creada, cuerpo) in enumerate(zip(creadas, cuerpos))
    ], session, {})


@dataclass
class _Grupo:
    """Los `create` anidados de un `update` bajo una misma fila y relación."""
    tabla: str
    clave: Dict[str, Any]
    cambios: Dict[str, Any]
    relacion: str
    campo: str
    forma: Dict[str, dict] = field(default_factory=dict)
    antes: set = field(default_factory=set)


@dataclass
class Plan:
    """Lo que `antes_de_escribir` deja para `despues_de_escribir`."""
    anidadas: List[Anidada]
    grupos: List[_Grupo]
    cache: Dict[str, list]


def _congelada(clave: Dict[str, Any]) -> tuple:
    return tuple(sorted(clave.items()))


async def antes_de_escribir(token: Any, anidadas: List[Anidada], session) -> Plan:
    """
    Antes del `update` del padre, en su transacción: los `create` anidados bajo una fila cuya tabla
    —o lo que se crea con ella— tiene reglas de propietario, y qué filas tiene ya esa relación, para
    saber después cuáles son las nuevas.

    Un `update`/`delete` anidado no se comprueba aquí: su RLS, y que cuelgue de la fila bajo la que
    se nombra, los aplica el DAO de tai-sql (0.8.0) al escribir, con el `rls=` del endpoint
    (`NestedRowNotFound`, un 404 por `traducir_anidada`). Antes de tai-sql 0.8.0 se buscaba aquí
    cada fila con la regla y se comparaban sus columnas de la unión con las del padre: la misma
    respuesta, con una consulta más por anidado y la regla de tai-sql copiada (SPEC-cliente-ts-2, P8).
    """
    cache: Dict[str, list] = {}
    grupos: Dict[tuple, _Grupo] = {}
    for anidada in anidadas:
        if anidada.accion == "create" and anidada.padre is not None:
            tabla, clave, cambios, relación, campo = anidada.padre
            grupo = grupos.setdefault((tabla, _congelada(clave), relación), _Grupo(
                tabla=tabla, clave=clave, cambios=cambios, relacion=relación, campo=campo,
            ))
            _fusionar(grupo.forma, anidada.forma)

    activos: List[_Grupo] = []
    for grupo in grupos.values():
        destino = RELACIONES[grupo.tabla][grupo.relacion][0]
        if not (_propias(token, destino, cache) or _alcanza(token, destino, grupo.forma, cache)):
            continue
        fila = await DAOS[grupo.tabla].find(**grupo.clave, session=session)
        if fila is not None:
            grupo.antes = {
                _congelada(_clave_fila(destino, hija))
                for hija in await _relacionadas(grupo.tabla, fila, grupo.relacion, session)
            }
        activos.append(grupo)
    return Plan(anidadas=anidadas, grupos=activos, cache=cache)


async def despues_de_escribir(token: Any, plan: Plan, session) -> None:
    """
    Después del `update` del padre, en su transacción: lo que dejan las escrituras anidadas tiene
    que seguir siendo del usuario (403 `OWNER`), y la excepción deshace todo.

    - Cada fila de un `update` anidado, con la clave que tiene ahora: no se le cambia el dueño ni se
      la mueve a un padre ajeno.
    - Cada fila que ha aparecido en una relación con `create` anidados, y lo que se creó con ella.
    """
    for anidada in plan.anidadas:
        if anidada.accion != "update":
            continue
        propias = _propias(token, anidada.tabla, plan.cache)
        if not propias:
            continue
        ahora = {columna: anidada.cambios.get(columna, valor) for columna, valor in anidada.clave.items()}
        if await DAOS[anidada.tabla].find(**ahora, rls=propias, session=session) is None:
            raise _en(owner_violation(), anidada.campo)

    for grupo in plan.grupos:
        destino = RELACIONES[grupo.tabla][grupo.relacion][0]
        ahora = {columna: grupo.cambios.get(columna, valor) for columna, valor in grupo.clave.items()}
        fila = await DAOS[grupo.tabla].find(**ahora, session=session)
        if fila is None:
            continue
        nuevas = [
            (hija, grupo.forma, grupo.campo)
            for hija in await _relacionadas(grupo.tabla, fila, grupo.relacion, session)
            if _congelada(_clave_fila(destino, hija)) not in grupo.antes
        ]
        await _comprobar_filas(token, destino, nuevas, session, plan.cache)

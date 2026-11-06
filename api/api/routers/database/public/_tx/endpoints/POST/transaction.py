import inspect
import json
import re
from dataclasses import dataclass
from datetime import date, datetime, time  # noqa: F401 — las claves primarias pueden ser de esos tipos
from uuid import UUID  # noqa: F401 — y de este
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Type

from fastapi import Depends, Request

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from api.routers.auth import (
    AccessToken,
    build_owner_rules,
    build_rls_rules,
    owner_locked_columns,
    owner_violation,
    require_permission,
    requires_authentication,
)
from api.database.public import username_context
from api.database.public._shared import get_model_by_name
from api.database.public import (
    public_async_api,
    RLS,
    UsuarioCreate,
    UsuarioFilter,
    UsuarioUpdateValues,
    ProyectoCreate,
    ProyectoFilter,
    ProyectoUpdateValues,
    EventoCreate,
    EventoFilter,
    EventoUpdateValues,
    RepertorioCreate,
    RepertorioFilter,
    RepertorioUpdateValues,
    CancionCreate,
    CancionFilter,
    CancionUpdateValues,
    GastoCreate,
    GastoFilter,
    GastoUpdateValues,
    IngresoCreate,
    IngresoFilter,
    IngresoUpdateValues,
)
from api.routers.database.public._masivos import (
    UsuarioUpdateMany,
    ProyectoUpdateMany,
    EventoUpdateMany,
    RepertorioUpdateMany,
    CancionUpdateMany,
    GastoUpdateMany,
    IngresoUpdateMany,
)
from api.resources import APIResponse, RecordNotFoundException, ValidationException
from api.routers.database.public._cabeceras import estricto
from api.routers.database.public._filtros import con_in_vacio
from api.routers.database.public._anidados import (
    antes_de_escribir,
    despues_de_crear,
    despues_de_escribir,
    en_create,
    en_update,
    exigir_permisos,
    traducir_anidada,
)
from .docs import TX_DESCRIPTION, TX_LIMIT, TX_RESPONSES, TX_SUMMARY
from ... import transaction_router


# ── Las tablas que se pueden escribir ──────────────────────────────────────────

class _ClaveUsuario(BaseModel):
    """La clave primaria de `usuario`."""
    model_config = ConfigDict(extra="forbid")
    id: int


class _ClaveProyecto(BaseModel):
    """La clave primaria de `proyecto`."""
    model_config = ConfigDict(extra="forbid")
    id: int


class _ClaveEvento(BaseModel):
    """La clave primaria de `evento`."""
    model_config = ConfigDict(extra="forbid")
    id: int


class _ClaveRepertorio(BaseModel):
    """La clave primaria de `repertorio`."""
    model_config = ConfigDict(extra="forbid")
    id: int


class _ClaveCancion(BaseModel):
    """La clave primaria de `cancion`."""
    model_config = ConfigDict(extra="forbid")
    id: int


class _ClaveGasto(BaseModel):
    """La clave primaria de `gasto`."""
    model_config = ConfigDict(extra="forbid")
    id: int


class _ClaveIngreso(BaseModel):
    """La clave primaria de `ingreso`."""
    model_config = ConfigDict(extra="forbid")
    id: int


@dataclass(frozen=True)
class _Tabla:
    """Lo que necesita una operación sobre una tabla: lo mismo que importa su endpoint."""
    nombre: str
    tablename: str
    dao: Any
    clave: Tuple[str, ...]
    Clave: Type[BaseModel]
    Create: Type[BaseModel]
    UpdateValues: Type[BaseModel]
    #: El cuerpo de `update_many`: `{filter, values}`, con `values` sin relaciones (`_masivos.py`).
    UpdateMany: Type[Any]
    Filter: Type[BaseModel]
    #: Los filtros de `DELETE /<tabla>`: los únicos que admite un `delete_many`.
    filtros: frozenset
    #: Las columnas del registro que devuelve `create`: lo que puede pedir un `$ref`.
    campos: frozenset


TABLAS: Dict[str, _Tabla] = {
    "usuario": _Tabla(
        nombre="Usuario",
        tablename="usuario",
        dao=public_async_api.usuario,
        clave=tuple(["id"]),
        Clave=_ClaveUsuario,
        Create=UsuarioCreate,
        UpdateValues=UsuarioUpdateValues,
        UpdateMany=UsuarioUpdateMany,
        Filter=UsuarioFilter,
        filtros=frozenset(["in_id", "nombre", "in_nombre", "apellido", "in_apellido", "email", "in_email", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"]),
        campos=frozenset(["id", "nombre", "apellido", "email", "created_at", "created_by", "updated_at", "updated_by"]),
    ),
    "proyecto": _Tabla(
        nombre="Proyecto",
        tablename="proyecto",
        dao=public_async_api.proyecto,
        clave=tuple(["id"]),
        Clave=_ClaveProyecto,
        Create=ProyectoCreate,
        UpdateValues=ProyectoUpdateValues,
        UpdateMany=ProyectoUpdateMany,
        Filter=ProyectoFilter,
        filtros=frozenset(["in_id", "id_usuario", "in_id_usuario", "nombre", "in_nombre", "tipo", "in_tipo", "descripcion", "in_descripcion", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"]),
        campos=frozenset(["id", "id_usuario", "nombre", "tipo", "descripcion", "created_at", "created_by", "updated_at", "updated_by"]),
    ),
    "evento": _Tabla(
        nombre="Evento",
        tablename="evento",
        dao=public_async_api.evento,
        clave=tuple(["id"]),
        Clave=_ClaveEvento,
        Create=EventoCreate,
        UpdateValues=EventoUpdateValues,
        UpdateMany=EventoUpdateMany,
        Filter=EventoFilter,
        filtros=frozenset(["in_id", "usuario_id", "in_usuario_id", "id_proyecto", "in_id_proyecto", "nombre", "in_nombre", "ubicacion", "in_ubicacion", "tipo", "in_tipo", "min_fecha", "max_fecha", "min_hora", "max_hora", "estado", "in_estado", "notas", "in_notas", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"]),
        campos=frozenset(["id", "usuario_id", "id_proyecto", "nombre", "ubicacion", "tipo", "fecha", "hora", "estado", "notas", "created_at", "created_by", "updated_at", "updated_by"]),
    ),
    "repertorio": _Tabla(
        nombre="Repertorio",
        tablename="repertorio",
        dao=public_async_api.repertorio,
        clave=tuple(["id"]),
        Clave=_ClaveRepertorio,
        Create=RepertorioCreate,
        UpdateValues=RepertorioUpdateValues,
        UpdateMany=RepertorioUpdateMany,
        Filter=RepertorioFilter,
        filtros=frozenset(["in_id", "usuario_id", "in_usuario_id", "id_proyecto", "in_id_proyecto", "nombre", "in_nombre", "descripcion", "in_descripcion", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"]),
        campos=frozenset(["id", "usuario_id", "id_proyecto", "nombre", "descripcion", "created_at", "created_by", "updated_at", "updated_by"]),
    ),
    "cancion": _Tabla(
        nombre="Cancion",
        tablename="cancion",
        dao=public_async_api.cancion,
        clave=tuple(["id"]),
        Clave=_ClaveCancion,
        Create=CancionCreate,
        UpdateValues=CancionUpdateValues,
        UpdateMany=CancionUpdateMany,
        Filter=CancionFilter,
        filtros=frozenset(["in_id", "id_repertorio", "in_id_repertorio", "nombre", "in_nombre", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"]),
        campos=frozenset(["id", "id_repertorio", "nombre", "created_at", "created_by", "updated_at", "updated_by"]),
    ),
    "gasto": _Tabla(
        nombre="Gasto",
        tablename="gasto",
        dao=public_async_api.gasto,
        clave=tuple(["id"]),
        Clave=_ClaveGasto,
        Create=GastoCreate,
        UpdateValues=GastoUpdateValues,
        UpdateMany=GastoUpdateMany,
        Filter=GastoFilter,
        filtros=frozenset(["in_id", "id_evento", "in_id_evento", "nombre", "in_nombre", "min_importe", "max_importe", "pagado", "concepto", "in_concepto", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"]),
        campos=frozenset(["id", "id_evento", "nombre", "importe", "pagado", "concepto", "created_at", "created_by", "updated_at", "updated_by"]),
    ),
    "ingreso": _Tabla(
        nombre="Ingreso",
        tablename="ingreso",
        dao=public_async_api.ingreso,
        clave=tuple(["id"]),
        Clave=_ClaveIngreso,
        Create=IngresoCreate,
        UpdateValues=IngresoUpdateValues,
        UpdateMany=IngresoUpdateMany,
        Filter=IngresoFilter,
        filtros=frozenset(["in_id", "id_evento", "in_id_evento", "nombre", "in_nombre", "min_importe", "max_importe", "recibido", "concepto", "in_concepto", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"]),
        campos=frozenset(["id", "id_evento", "nombre", "importe", "recibido", "concepto", "created_at", "created_by", "updated_at", "updated_by"]),
    ),
}

#: La acción de permiso de cada operación: la de su endpoint.
ACCION = {"create": "create", "update": "update", "delete": "delete", "update_many": "update", "delete_many": "delete"}


# ── El cuerpo ──────────────────────────────────────────────────────────────────

class PublicTransactionOperation(BaseModel):
    """Una escritura de la transacción: la operación del endpoint de su tabla."""
    model_config = ConfigDict(extra="forbid")

    op: Literal["create", "update", "delete", "update_many", "delete_many"] = Field(
        ..., description="La operación: la del endpoint del mismo nombre de la tabla")
    table: Literal["usuario", "proyecto", "evento", "repertorio", "cancion", "gasto", "ingreso"] = Field(
        ..., description="La tabla, por su nombre en la base de datos. Solo tablas: una vista no se escribe")
    key: Optional[Any] = Field(
        None, description="`update` y `delete`: la clave primaria, o un objeto con sus columnas si es compuesta")
    values: Optional[Dict[str, Any]] = Field(
        None, description="`create`, `update` y `update_many`: los valores, como en el cuerpo de su endpoint")
    filter: Optional[Dict[str, Any]] = Field(
        None, description="`update_many` y `delete_many`: los filtros, como en su endpoint")
    confirm_all: bool = Field(
        False, description="`update_many` y `delete_many`: necesario para operar sin ningún filtro")


class PublicTransaction(BaseModel):
    """Las operaciones de una transacción, en el orden en que se aplican."""
    model_config = ConfigDict(extra="forbid")

    operations: List[PublicTransactionOperation] = Field(..., min_length=1, max_length=TX_LIMIT)


# ── Lo que se comprueba antes de tocar la base de datos ─────────────────────────

#: Qué lleva cada operación: lo obligatorio y lo que no puede llevar.
_FORMA = {
    "create": ({"values"}, {"key", "filter", "confirm_all"}),
    "update": ({"key", "values"}, {"filter", "confirm_all"}),
    "delete": ({"key"}, {"values", "filter", "confirm_all"}),
    "update_many": ({"filter", "values"}, {"key"}),
    "delete_many": ({"filter"}, {"key", "values"}),
}

_REF = re.compile(r"^(\d+)\.([A-Za-z_][A-Za-z0-9_]*)$")


def _es_ref(valor: Any) -> bool:
    """Un objeto con una sola clave, `$ref`, es siempre una referencia."""
    return isinstance(valor, dict) and set(valor) == {"$ref"}


def _error(loc: tuple, mensaje: str, entrada: Any = None) -> dict:
    return {"type": "value_error", "loc": ("body",) + loc, "msg": mensaje, "input": entrada}


def _refs(valor: Any, ruta: tuple):
    """Cada `$ref` dentro de un valor, con su ruta."""
    if _es_ref(valor):
        yield ruta, valor["$ref"]
    elif isinstance(valor, dict):
        for clave, hijo in valor.items():
            yield from _refs(hijo, ruta + (clave,))
    elif isinstance(valor, list):
        for posición, hijo in enumerate(valor):
            yield from _refs(hijo, ruta + (posición,))


def _comprobar(operaciones: List[PublicTransactionOperation]) -> None:
    """
    La forma de cada operación y cada `$ref`, todas a la vez y sin tocar la base de datos: un 422
    con un error por cada cosa que no vale, cada uno con su `operations.<i>…`.

    El cuerpo de `_tx` es estricto **siempre**, con `X-Tai-Strict` o sin ella: una clave que una
    operación no tiene (`extra="forbid"`), un campo que su DTO no conoce y un filtro que su
    `delete_many` no admite son un 422. Es un endpoint nuevo, sin frontends a los que romper, y en
    una transacción explícita lo ignorado se escribe o se borra. La cabecera solo añade lo que mira
    en todos los endpoints: los parámetros de consulta, y `_tx` no declara ninguno.
    """
    errores: List[dict] = []
    for i, operación in enumerate(operaciones):
        tabla = TABLAS[operación.table]
        donde = ("operations", i)
        obligatorio, prohibido = _FORMA[operación.op]
        for parte in sorted(obligatorio):
            if getattr(operación, parte) is None:
                errores.append(_error(donde + (parte,), f"`{operación.op}` necesita `{parte}`"))
        for parte in sorted(prohibido):
            valor = getattr(operación, parte)
            if valor is not None and valor is not False:
                errores.append(_error(donde + (parte,), f"`{operación.op}` no lleva `{parte}`"))

        clave = operación.key
        if clave is not None and not _es_ref(clave):
            if isinstance(clave, list) or (not isinstance(clave, dict) and len(tabla.clave) > 1):
                errores.append(_error(
                    donde + ("key",),
                    f"La clave de {operación.table} es " + (
                        "compuesta: un objeto con " + ", ".join(tabla.clave)
                        if len(tabla.clave) > 1 else f"un valor ({tabla.clave[0]}) o un objeto con él"
                    ),
                ))

        for parte in ("key", "values", "filter"):
            for ruta, ref in _refs(getattr(operación, parte), donde + (parte,)):
                encontrada = _REF.match(ref) if isinstance(ref, str) else None
                if encontrada is None:
                    errores.append(_error(ruta, 'Un $ref es "<índice>.<campo>": "0.id"', ref))
                    continue
                índice, campo = int(encontrada.group(1)), encontrada.group(2)
                if índice >= i:
                    errores.append(_error(ruta, f"$ref {ref!r}: solo puede apuntar a una operación anterior", ref))
                elif operaciones[índice].op != "create":
                    errores.append(_error(ruta, f"$ref {ref!r}: la operación {índice} es `{operaciones[índice].op}` y devuelve un número; solo `create` devuelve un registro", ref))
                elif campo not in TABLAS[operaciones[índice].table].campos:
                    errores.append(_error(ruta, f"$ref {ref!r}: {operaciones[índice].table} no tiene la columna {campo!r}", ref))
    if errores:
        raise RequestValidationError(errores)


# ── Una operación ──────────────────────────────────────────────────────────────

class _FalloEnOperacion(Exception):
    """La excepción de la operación `indice`, que tiene que salir del `async with` para deshacerlo todo."""

    def __init__(self, indice: int, causa: Exception):
        super().__init__(f"operations.{indice}: {causa}")
        self.indice = indice
        self.causa = causa


def _resolver(valor: Any, resultados: List[Any]) -> Any:
    """Sustituye cada `$ref` por el campo del registro al que apunta. La forma ya se comprobó."""
    if _es_ref(valor):
        índice, campo = valor["$ref"].split(".", 1)
        return getattr(resultados[int(índice)], campo)
    if isinstance(valor, dict):
        return {clave: _resolver(hijo, resultados) for clave, hijo in valor.items()}
    if isinstance(valor, list):
        return [_resolver(hijo, resultados) for hijo in valor]
    return valor


def _validar(i: int, parte: Optional[str], Modelo: Type[BaseModel], datos: Any) -> Any:
    """El DTO de la operación, o un 422 cuyo `field` dice dónde: `operations.<i>.values.<campo>`."""
    try:
        return Modelo.model_validate(datos)
    except ValidationError as e:
        prefijo = ("body", "operations", i) + ((parte,) if parte else ())
        raise RequestValidationError([
            {"type": error["type"], "loc": prefijo + tuple(error["loc"]), "msg": error["msg"], "input": error.get("input")}
            for error in e.errors()
        ]) from None


def _clave(i: int, operación: PublicTransactionOperation, tabla: _Tabla, resultados: List[Any]) -> Dict[str, Any]:
    crudo = _resolver(operación.key, resultados)
    if not isinstance(crudo, dict):
        crudo = {tabla.clave[0]: crudo}
    return dict(_validar(i, "key", tabla.Clave, crudo))


def _sin_filtro() -> ValidationException:
    return ValidationException(
        "Sin filtros, esta operación alcanzaría todas las filas. "
        "Añade algún filtro, o confirm_all: true si es lo que quieres.",
        "confirm_all",
    )


def _reglas(token: AccessToken) -> list:
    """El RLS de las lecturas y escrituras sobre filas que existen, como en cada endpoint."""
    return build_rls_rules(token, "public", get_model_by_name, RLS)


def _propias(token: AccessToken, tabla: _Tabla) -> list:
    """Las reglas de propietario que alcanzan a la tabla, como en cada endpoint."""
    return build_owner_rules(
        token, "public", get_model_by_name, RLS,
        model=get_model_by_name(f"public.{tabla.tablename}"),
    )


async def _create(i, operación, tabla: _Tabla, resultados, token, session) -> Any:
    valores = _validar(i, "values", tabla.Create, _resolver(operación.values, resultados))
    try:
        creado = await tabla.dao.create(valores, session=session)
    except Exception as error:
        # Lo que el DAO rechaza de las anidadas (tai-sql #218): con el `field` bajo `values`, y
        # el endpoint antepone `operations.<i>`.
        traducir_anidada(error, "values.")
        raise
    # Como `POST /<tabla>`: la fila nueva tiene que ser del usuario.
    propias = _propias(token, tabla)
    if propias and await tabla.dao.find(
        **{columna: getattr(creado, columna) for columna in tabla.clave}, rls=propias, session=session,
    ) is None:
        raise owner_violation()
    # Y lo que creó anidado, como en el endpoint.
    await despues_de_crear(token, tabla.tablename, creado, valores, session, "values.")
    return creado


async def _update(i, operación, tabla: _Tabla, resultados, token, session) -> int:
    clave = _clave(i, operación, tabla, resultados)
    valores = _validar(i, "values", tabla.UpdateValues, _resolver(operación.values, resultados))
    rls = _reglas(token)
    # Como `PATCH /<tabla>/<clave>`: lo que la regla no alcanza no existe para el usuario (404).
    if await tabla.dao.find(**clave, rls=rls, session=session) is None:
        raise RecordNotFoundException(tabla.nombre)
    # Sus escrituras anidadas: el RLS y que cuelguen de esta fila los aplica el DAO con `rls=`;
    # aquí, lo que hace falta para el propietario de lo creado.
    plan = await antes_de_escribir(token, en_update(tabla.tablename, valores, "values.", clave), session)
    try:
        resultado = await tabla.dao.update(**clave, updated_values=valores, rls=rls, session=session)
    except Exception as error:
        traducir_anidada(error, "values.")
        raise
    if resultado == 0:
        raise RecordNotFoundException(tabla.nombre)
    propias = _propias(token, tabla)
    if propias:
        cambios = valores.to_dict()
        if await tabla.dao.find(
            **{columna: cambios.get(columna, valor) for columna, valor in clave.items()},
            rls=propias, session=session,
        ) is None:
            raise owner_violation()
    await despues_de_escribir(token, plan, session)
    return resultado


async def _delete(i, operación, tabla: _Tabla, resultados, token, session) -> int:
    clave = _clave(i, operación, tabla, resultados)
    rls = _reglas(token)
    if await tabla.dao.find(**clave, rls=rls, session=session) is None:
        raise RecordNotFoundException(tabla.nombre)
    resultado = await tabla.dao.delete(**clave, rls=rls, session=session)
    if resultado == 0:
        raise RecordNotFoundException(tabla.nombre)
    return resultado


async def _update_many(i, operación, tabla: _Tabla, resultados, token, session) -> int:
    carga = _validar(i, None, tabla.UpdateMany, {
        "filter": _resolver(operación.filter, resultados),
        "values": _resolver(operación.values, resultados),
    }).to_dao()
    if not carga.filter.to_dict() and not operación.confirm_all:
        raise _sin_filtro()
    # Un `in_` vacío no casa con ninguna fila: 0 sin llamar al DAO (`_filtros.py`).
    if con_in_vacio(carga.filter.to_dict()) is not None:
        return 0
    # Como `PATCH /<tabla>`: con una regla de propietario no se cambia de quién son las filas.
    modelo = get_model_by_name(f"public.{tabla.tablename}")
    if owner_locked_columns(_propias(token, tabla), modelo) & set(carga.values.to_dict()):
        raise owner_violation()
    return await tabla.dao.update_many(carga, rls=_reglas(token), session=session)


async def _delete_many(i, operación, tabla: _Tabla, resultados, token, session) -> int:
    crudo = _resolver(operación.filter, resultados)
    # Los filtros de `DELETE /<tabla>` y ninguno más. El endpoint ignora un parámetro que no
    # conoce; aquí un filtro mal escrito borraría más de lo pedido, así que es un 422.
    desconocidos = sorted(set(crudo) - tabla.filtros)
    if desconocidos:
        raise RequestValidationError([
            _error(("operations", i, "filter", nombre), f"{tabla.tablename} no tiene el filtro {nombre!r}")
            for nombre in desconocidos
        ])
    filtro = _validar(i, "filter", tabla.Filter, crudo).to_dict()
    if not filtro and not operación.confirm_all:
        raise _sin_filtro()
    if con_in_vacio(filtro) is not None:
        return 0
    return await tabla.dao.delete_many(**filtro, rls=_reglas(token), session=session)


_OPERACIONES: Dict[str, Callable] = {
    "create": _create,
    "update": _update,
    "delete": _delete,
    "update_many": _update_many,
    "delete_many": _delete_many,
}


async def _ejecutar(operaciones: List[PublicTransactionOperation], token, session) -> List[Any]:
    resultados: List[Any] = []
    for i, operación in enumerate(operaciones):
        try:
            resultados.append(
                await _OPERACIONES[operación.op](i, operación, TABLAS[operación.table], resultados, token, session)
            )
        except RequestValidationError:
            raise  # ya dice dónde: operations.<i>…
        except Exception as e:
            raise _FalloEnOperacion(i, e) from e
    return resultados


# ── El error de una operación ──────────────────────────────────────────────────

def _manejador(app, exc: Exception):
    """El manejador que la aplicación tiene para esta excepción, por su herencia, como Starlette."""
    for clase in type(exc).__mro__:
        manejador = app.exception_handlers.get(clase)
        if manejador is not None:
            return manejador
    return None


async def _responder_fallo(request: Request, indice: int, exc: Exception) -> JSONResponse:
    """
    La respuesta que daría el endpoint de la operación —la compone el manejador de la aplicación,
    de `resources/`— con `operations.<i>` delante del `field` de cada error. Así un 404, un 409 o
    el 422 de un trigger dicen qué operación fue, sin que `resources/` tenga que saber de `_tx`.
    Un 5xx sale tal cual: no dice nada del motivo, tampoco cuál.
    """
    manejador = _manejador(request.app, exc)
    if manejador is None:
        raise exc
    respuesta = manejador(request, exc)
    if inspect.isawaitable(respuesta):
        respuesta = await respuesta
    if respuesta.status_code >= 500:
        return respuesta
    cuerpo = json.loads(respuesta.body)
    for error in cuerpo.get("errors") or []:
        campo = error.get("field")
        error["field"] = f"operations.{indice}" + (f".{campo}" if campo else "")
    cabeceras = {
        nombre: valor for nombre, valor in respuesta.headers.items()
        if nombre.lower() not in ("content-length", "content-type")
    }
    return JSONResponse(status_code=respuesta.status_code, content=cuerpo, headers=cabeceras)


# ── El endpoint ────────────────────────────────────────────────────────────────

@transaction_router.post("/_tx",
    response_model=APIResponse[List[Any]],
    operation_id="public_transaction",
    summary=TX_SUMMARY,
    description=TX_DESCRIPTION,
    responses=TX_RESPONSES
)
async def public_transaction(
    request: Request,
    transaccion: PublicTransaction,
    # Solo identidad: el permiso es el de cada operación, y se comprueba abajo.
    token: AccessToken = Depends(requires_authentication()),
    # El modo estricto (`X-Tai-Strict: 1`) solo añade aquí que no hay parámetros de consulta: el
    # cuerpo ya es estricto siempre (ver `_comprobar`). Último, para que un 401/403 vaya antes.
    _estricto: None = Depends(estricto("_tx", "transaction")),
):
    """
    Aplica las operaciones en orden y en una sola transacción: o todas, o ninguna.
    """
    operaciones = transaccion.operations
    _comprobar(operaciones)

    # El permiso de cada operación, el de su endpoint, antes de escribir nada; y el de las tablas
    # en las que escriben sus `values` anidados.
    for i, operación in enumerate(operaciones):
        try:
            require_permission(token, ACCION[operación.op], operación.table)
            if operación.op == "create":
                exigir_permisos(token, en_create(operación.table, operación.values, "values."))
            elif operación.op == "update":
                exigir_permisos(token, en_update(operación.table, operación.values, "values."))
        except Exception as e:
            return await _responder_fallo(request, i, e)

    try:
        with username_context(token.preferred_username):
            async with public_async_api.session_manager.get_session() as session:
                resultados = await _ejecutar(operaciones, token, session)
    except _FalloEnOperacion as fallo:
        return await _responder_fallo(request, fallo.indice, fallo.causa)

    return APIResponse.success(
        data=resultados,
        message=f"{len(resultados)} operaciones aplicadas en una transacción",
    )
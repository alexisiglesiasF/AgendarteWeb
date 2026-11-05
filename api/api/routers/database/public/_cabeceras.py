# Generado por tai-api: este fichero lo reescribe `tai-api generate`.
"""
Lo que hacen los endpoints de `public` según las cabeceras de la petición.

**`X-Tai-Strict: 1`, el modo estricto.** Sin la cabecera, la API ignora en silencio lo que no
conoce —un parámetro de consulta que el endpoint no declara, un `order_by` sobre una columna que no
existe, un `includes` que no es una relación o que pasa de la profundidad máxima— y responde como
si no se hubiera pedido. Es lo de siempre, y sigue así: la forma de la API es contrato con
frontends que no mandan la cabecera. Con ella, cada una de esas cosas es un **422
`VALIDATION_ERROR`** con su `field`, el mismo que compone el handler de la validación de FastAPI.
Un filtro con una errata (`in_idd`) deja de devolver la tabla entera, y un sexto nivel de
`includes` deja de llegar vacío. El cliente TypeScript la manda siempre.

**`Prefer: return=representation`, en `PATCH /<tabla>/<clave>`.** Con ella, `data` es el registro
actualizado en vez de cuántas filas cambiaron (RFC 7240). Sin ella, el entero de siempre.
"""
from typing import Dict, FrozenSet, List, Optional, Tuple

from fastapi import Header, Request
from fastapi.exceptions import RequestValidationError

#: La profundidad máxima de `includes` (`client.max_depth`): un nivel más llegaría vacío.
MAX_DEPTH = 5

#: Las relaciones que se pueden pedir en `includes`, por tabla: {relación: tabla destino}.
RELACIONES: Dict[str, Dict[str, str]] = {
    "usuario": {"proyectos": "proyecto", "eventos": "evento", "repertorios": "repertorio"},
    "proyecto": {"usuario": "usuario", "eventos": "evento", "repertorios": "repertorio"},
    "evento": {"proyecto": "proyecto", "usuario": "usuario", "gastos": "gasto", "ingresos": "ingreso"},
    "repertorio": {"canciones": "cancion", "usuario": "usuario", "proyecto": "proyecto"},
    "cancion": {"repertorio": "repertorio"},
    "gasto": {"evento": "evento"},
    "ingreso": {"evento": "evento"},
}

#: Las columnas por las que se puede ordenar, por tabla.
COLUMNAS: Dict[str, FrozenSet[str]] = {
    "usuario": frozenset({"id", "nombre", "apellido", "email", "created_at", "created_by", "updated_at", "updated_by"}),
    "proyecto": frozenset({"id", "id_usuario", "nombre", "tipo", "descripcion", "created_at", "created_by", "updated_at", "updated_by"}),
    "evento": frozenset({"id", "usuario_id", "id_proyecto", "nombre", "ubicacion", "tipo", "fecha", "hora", "estado", "notas", "created_at", "created_by", "updated_at", "updated_by"}),
    "repertorio": frozenset({"id", "usuario_id", "id_proyecto", "nombre", "descripcion", "created_at", "created_by", "updated_at", "updated_by"}),
    "cancion": frozenset({"id", "id_repertorio", "nombre", "created_at", "created_by", "updated_at", "updated_by"}),
    "gasto": frozenset({"id", "id_evento", "nombre", "importe", "pagado", "concepto", "created_at", "created_by", "updated_at", "updated_by"}),
    "ingreso": frozenset({"id", "id_evento", "nombre", "importe", "recibido", "concepto", "created_at", "created_by", "updated_at", "updated_by"}),
}

#: Los parámetros de consulta que declara cada operación: cualquier otro es un 422.
CONSULTA: Dict[Tuple[str, str], FrozenSet[str]] = {
    ("usuario", "find_many"): frozenset({"limit", "order_by", "order", "offset", "in_id", "nombre", "in_nombre", "apellido", "in_apellido", "email", "in_email", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by", "includes"}),
    ("usuario", "count"): frozenset({"in_id", "nombre", "in_nombre", "apellido", "in_apellido", "email", "in_email", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("usuario", "exists"): frozenset({"in_id", "nombre", "in_nombre", "apellido", "in_apellido", "email", "in_email", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("usuario", "sum"): frozenset({"in_id", "nombre", "in_nombre", "apellido", "in_apellido", "email", "in_email", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("usuario", "mean"): frozenset({"in_id", "nombre", "in_nombre", "apellido", "in_apellido", "email", "in_email", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("usuario", "max"): frozenset({"in_id", "nombre", "in_nombre", "apellido", "in_apellido", "email", "in_email", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("usuario", "min"): frozenset({"in_id", "nombre", "in_nombre", "apellido", "in_apellido", "email", "in_email", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("usuario", "find_by"): frozenset({"email", "includes"}),
    ("usuario", "find"): frozenset({"includes"}),
    ("usuario", "agg"): frozenset(),
    ("usuario", "create"): frozenset(),
    ("usuario", "create_many"): frozenset(),
    ("usuario", "update"): frozenset({"includes"}),
    ("usuario", "update_many"): frozenset({"confirm_all"}),
    ("usuario", "delete"): frozenset(),
    ("usuario", "delete_many"): frozenset({"in_id", "nombre", "in_nombre", "apellido", "in_apellido", "email", "in_email", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by", "confirm_all"}),
    ("proyecto", "find_many"): frozenset({"limit", "order_by", "order", "offset", "in_id", "id_usuario", "in_id_usuario", "nombre", "in_nombre", "tipo", "in_tipo", "descripcion", "in_descripcion", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by", "includes"}),
    ("proyecto", "count"): frozenset({"in_id", "id_usuario", "in_id_usuario", "nombre", "in_nombre", "tipo", "in_tipo", "descripcion", "in_descripcion", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("proyecto", "exists"): frozenset({"in_id", "id_usuario", "in_id_usuario", "nombre", "in_nombre", "tipo", "in_tipo", "descripcion", "in_descripcion", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("proyecto", "sum"): frozenset({"in_id", "id_usuario", "in_id_usuario", "nombre", "in_nombre", "tipo", "in_tipo", "descripcion", "in_descripcion", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("proyecto", "mean"): frozenset({"in_id", "id_usuario", "in_id_usuario", "nombre", "in_nombre", "tipo", "in_tipo", "descripcion", "in_descripcion", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("proyecto", "max"): frozenset({"in_id", "id_usuario", "in_id_usuario", "nombre", "in_nombre", "tipo", "in_tipo", "descripcion", "in_descripcion", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("proyecto", "min"): frozenset({"in_id", "id_usuario", "in_id_usuario", "nombre", "in_nombre", "tipo", "in_tipo", "descripcion", "in_descripcion", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("proyecto", "find_by"): frozenset({"nombre", "includes"}),
    ("proyecto", "find"): frozenset({"includes"}),
    ("proyecto", "agg"): frozenset(),
    ("proyecto", "create"): frozenset(),
    ("proyecto", "create_many"): frozenset(),
    ("proyecto", "update"): frozenset({"includes"}),
    ("proyecto", "update_many"): frozenset({"confirm_all"}),
    ("proyecto", "delete"): frozenset(),
    ("proyecto", "delete_many"): frozenset({"in_id", "id_usuario", "in_id_usuario", "nombre", "in_nombre", "tipo", "in_tipo", "descripcion", "in_descripcion", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by", "confirm_all"}),
    ("evento", "find_many"): frozenset({"limit", "order_by", "order", "offset", "in_id", "usuario_id", "in_usuario_id", "id_proyecto", "in_id_proyecto", "nombre", "in_nombre", "ubicacion", "in_ubicacion", "tipo", "in_tipo", "min_fecha", "max_fecha", "min_hora", "max_hora", "estado", "in_estado", "notas", "in_notas", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by", "includes"}),
    ("evento", "count"): frozenset({"in_id", "usuario_id", "in_usuario_id", "id_proyecto", "in_id_proyecto", "nombre", "in_nombre", "ubicacion", "in_ubicacion", "tipo", "in_tipo", "min_fecha", "max_fecha", "min_hora", "max_hora", "estado", "in_estado", "notas", "in_notas", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("evento", "exists"): frozenset({"in_id", "usuario_id", "in_usuario_id", "id_proyecto", "in_id_proyecto", "nombre", "in_nombre", "ubicacion", "in_ubicacion", "tipo", "in_tipo", "min_fecha", "max_fecha", "min_hora", "max_hora", "estado", "in_estado", "notas", "in_notas", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("evento", "sum"): frozenset({"in_id", "usuario_id", "in_usuario_id", "id_proyecto", "in_id_proyecto", "nombre", "in_nombre", "ubicacion", "in_ubicacion", "tipo", "in_tipo", "min_fecha", "max_fecha", "min_hora", "max_hora", "estado", "in_estado", "notas", "in_notas", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("evento", "mean"): frozenset({"in_id", "usuario_id", "in_usuario_id", "id_proyecto", "in_id_proyecto", "nombre", "in_nombre", "ubicacion", "in_ubicacion", "tipo", "in_tipo", "min_fecha", "max_fecha", "min_hora", "max_hora", "estado", "in_estado", "notas", "in_notas", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("evento", "max"): frozenset({"in_id", "usuario_id", "in_usuario_id", "id_proyecto", "in_id_proyecto", "nombre", "in_nombre", "ubicacion", "in_ubicacion", "tipo", "in_tipo", "min_fecha", "max_fecha", "min_hora", "max_hora", "estado", "in_estado", "notas", "in_notas", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("evento", "min"): frozenset({"in_id", "usuario_id", "in_usuario_id", "id_proyecto", "in_id_proyecto", "nombre", "in_nombre", "ubicacion", "in_ubicacion", "tipo", "in_tipo", "min_fecha", "max_fecha", "min_hora", "max_hora", "estado", "in_estado", "notas", "in_notas", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("evento", "find_by"): frozenset({"nombre", "includes"}),
    ("evento", "find"): frozenset({"includes"}),
    ("evento", "agg"): frozenset(),
    ("evento", "create"): frozenset(),
    ("evento", "create_many"): frozenset(),
    ("evento", "update"): frozenset({"includes"}),
    ("evento", "update_many"): frozenset({"confirm_all"}),
    ("evento", "delete"): frozenset(),
    ("evento", "delete_many"): frozenset({"in_id", "usuario_id", "in_usuario_id", "id_proyecto", "in_id_proyecto", "nombre", "in_nombre", "ubicacion", "in_ubicacion", "tipo", "in_tipo", "min_fecha", "max_fecha", "min_hora", "max_hora", "estado", "in_estado", "notas", "in_notas", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by", "confirm_all"}),
    ("repertorio", "find_many"): frozenset({"limit", "order_by", "order", "offset", "in_id", "usuario_id", "in_usuario_id", "id_proyecto", "in_id_proyecto", "nombre", "in_nombre", "descripcion", "in_descripcion", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by", "includes"}),
    ("repertorio", "count"): frozenset({"in_id", "usuario_id", "in_usuario_id", "id_proyecto", "in_id_proyecto", "nombre", "in_nombre", "descripcion", "in_descripcion", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("repertorio", "exists"): frozenset({"in_id", "usuario_id", "in_usuario_id", "id_proyecto", "in_id_proyecto", "nombre", "in_nombre", "descripcion", "in_descripcion", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("repertorio", "sum"): frozenset({"in_id", "usuario_id", "in_usuario_id", "id_proyecto", "in_id_proyecto", "nombre", "in_nombre", "descripcion", "in_descripcion", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("repertorio", "mean"): frozenset({"in_id", "usuario_id", "in_usuario_id", "id_proyecto", "in_id_proyecto", "nombre", "in_nombre", "descripcion", "in_descripcion", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("repertorio", "max"): frozenset({"in_id", "usuario_id", "in_usuario_id", "id_proyecto", "in_id_proyecto", "nombre", "in_nombre", "descripcion", "in_descripcion", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("repertorio", "min"): frozenset({"in_id", "usuario_id", "in_usuario_id", "id_proyecto", "in_id_proyecto", "nombre", "in_nombre", "descripcion", "in_descripcion", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("repertorio", "find_by"): frozenset({"nombre", "includes"}),
    ("repertorio", "find"): frozenset({"includes"}),
    ("repertorio", "agg"): frozenset(),
    ("repertorio", "create"): frozenset(),
    ("repertorio", "create_many"): frozenset(),
    ("repertorio", "update"): frozenset({"includes"}),
    ("repertorio", "update_many"): frozenset({"confirm_all"}),
    ("repertorio", "delete"): frozenset(),
    ("repertorio", "delete_many"): frozenset({"in_id", "usuario_id", "in_usuario_id", "id_proyecto", "in_id_proyecto", "nombre", "in_nombre", "descripcion", "in_descripcion", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by", "confirm_all"}),
    ("cancion", "find_many"): frozenset({"limit", "order_by", "order", "offset", "in_id", "id_repertorio", "in_id_repertorio", "nombre", "in_nombre", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by", "includes"}),
    ("cancion", "count"): frozenset({"in_id", "id_repertorio", "in_id_repertorio", "nombre", "in_nombre", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("cancion", "exists"): frozenset({"in_id", "id_repertorio", "in_id_repertorio", "nombre", "in_nombre", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("cancion", "sum"): frozenset({"in_id", "id_repertorio", "in_id_repertorio", "nombre", "in_nombre", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("cancion", "mean"): frozenset({"in_id", "id_repertorio", "in_id_repertorio", "nombre", "in_nombre", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("cancion", "max"): frozenset({"in_id", "id_repertorio", "in_id_repertorio", "nombre", "in_nombre", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("cancion", "min"): frozenset({"in_id", "id_repertorio", "in_id_repertorio", "nombre", "in_nombre", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("cancion", "find_by"): frozenset({"nombre", "includes"}),
    ("cancion", "find"): frozenset({"includes"}),
    ("cancion", "agg"): frozenset(),
    ("cancion", "create"): frozenset(),
    ("cancion", "create_many"): frozenset(),
    ("cancion", "update"): frozenset({"includes"}),
    ("cancion", "update_many"): frozenset({"confirm_all"}),
    ("cancion", "delete"): frozenset(),
    ("cancion", "delete_many"): frozenset({"in_id", "id_repertorio", "in_id_repertorio", "nombre", "in_nombre", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by", "confirm_all"}),
    ("gasto", "find_many"): frozenset({"limit", "order_by", "order", "offset", "in_id", "id_evento", "in_id_evento", "nombre", "in_nombre", "min_importe", "max_importe", "pagado", "concepto", "in_concepto", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by", "includes"}),
    ("gasto", "count"): frozenset({"in_id", "id_evento", "in_id_evento", "nombre", "in_nombre", "min_importe", "max_importe", "pagado", "concepto", "in_concepto", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("gasto", "exists"): frozenset({"in_id", "id_evento", "in_id_evento", "nombre", "in_nombre", "min_importe", "max_importe", "pagado", "concepto", "in_concepto", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("gasto", "sum"): frozenset({"in_id", "id_evento", "in_id_evento", "nombre", "in_nombre", "min_importe", "max_importe", "pagado", "concepto", "in_concepto", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("gasto", "mean"): frozenset({"in_id", "id_evento", "in_id_evento", "nombre", "in_nombre", "min_importe", "max_importe", "pagado", "concepto", "in_concepto", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("gasto", "max"): frozenset({"in_id", "id_evento", "in_id_evento", "nombre", "in_nombre", "min_importe", "max_importe", "pagado", "concepto", "in_concepto", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("gasto", "min"): frozenset({"in_id", "id_evento", "in_id_evento", "nombre", "in_nombre", "min_importe", "max_importe", "pagado", "concepto", "in_concepto", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("gasto", "find_by"): frozenset({"nombre", "includes"}),
    ("gasto", "find"): frozenset({"includes"}),
    ("gasto", "agg"): frozenset(),
    ("gasto", "create"): frozenset(),
    ("gasto", "create_many"): frozenset(),
    ("gasto", "update"): frozenset({"includes"}),
    ("gasto", "update_many"): frozenset({"confirm_all"}),
    ("gasto", "delete"): frozenset(),
    ("gasto", "delete_many"): frozenset({"in_id", "id_evento", "in_id_evento", "nombre", "in_nombre", "min_importe", "max_importe", "pagado", "concepto", "in_concepto", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by", "confirm_all"}),
    ("ingreso", "find_many"): frozenset({"limit", "order_by", "order", "offset", "in_id", "id_evento", "in_id_evento", "nombre", "in_nombre", "min_importe", "max_importe", "recibido", "concepto", "in_concepto", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by", "includes"}),
    ("ingreso", "count"): frozenset({"in_id", "id_evento", "in_id_evento", "nombre", "in_nombre", "min_importe", "max_importe", "recibido", "concepto", "in_concepto", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("ingreso", "exists"): frozenset({"in_id", "id_evento", "in_id_evento", "nombre", "in_nombre", "min_importe", "max_importe", "recibido", "concepto", "in_concepto", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("ingreso", "sum"): frozenset({"in_id", "id_evento", "in_id_evento", "nombre", "in_nombre", "min_importe", "max_importe", "recibido", "concepto", "in_concepto", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("ingreso", "mean"): frozenset({"in_id", "id_evento", "in_id_evento", "nombre", "in_nombre", "min_importe", "max_importe", "recibido", "concepto", "in_concepto", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("ingreso", "max"): frozenset({"in_id", "id_evento", "in_id_evento", "nombre", "in_nombre", "min_importe", "max_importe", "recibido", "concepto", "in_concepto", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("ingreso", "min"): frozenset({"in_id", "id_evento", "in_id_evento", "nombre", "in_nombre", "min_importe", "max_importe", "recibido", "concepto", "in_concepto", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by"}),
    ("ingreso", "find_by"): frozenset({"nombre", "includes"}),
    ("ingreso", "find"): frozenset({"includes"}),
    ("ingreso", "agg"): frozenset(),
    ("ingreso", "create"): frozenset(),
    ("ingreso", "create_many"): frozenset(),
    ("ingreso", "update"): frozenset({"includes"}),
    ("ingreso", "update_many"): frozenset({"confirm_all"}),
    ("ingreso", "delete"): frozenset(),
    ("ingreso", "delete_many"): frozenset({"in_id", "id_evento", "in_id_evento", "nombre", "in_nombre", "min_importe", "max_importe", "recibido", "concepto", "in_concepto", "min_created_at", "max_created_at", "in_created_by", "min_updated_at", "max_updated_at", "in_updated_by", "confirm_all"}),
    # `POST /<schema>/_tx`, que es del schema y no de una tabla: no declara parámetros de consulta.
    ("_tx", "transaction"): frozenset(),
}


def quiere_representacion(prefer: Optional[str]) -> bool:
    """
    Si la cabecera `Prefer` pide `return=representation` (RFC 7240): entre varias preferencias
    separadas por comas, sin mirar sus parámetros (`; ...`), ni mayúsculas ni comillas.
    """
    for preferencia in (prefer or "").split(","):
        nombre, _, valor = preferencia.split(";")[0].partition("=")
        if nombre.strip().lower() == "return" and valor.strip().strip('"').lower() == "representation":
            return True
    return False


def include_no_valido(tabla: str, ruta: str) -> Optional[str]:
    """El motivo por el que `ruta` no es un `includes` de `tabla`, o `None` si lo es."""
    partes = ruta.split(".")
    if len(partes) > MAX_DEPTH:
        return (
            f"'{ruta}' tiene {len(partes)} niveles y el máximo es {MAX_DEPTH}: "
            "lo que pasa de ahí llegaría vacío"
        )
    actual = tabla
    for parte in partes:
        destino = RELACIONES.get(actual, {}).get(parte)
        if destino is None:
            return f"'{parte}' no es una relación de {actual}"
        actual = destino
    return None


def estricto(tabla: str, operacion: str):
    """
    La dependencia de una operación: comprueba la petición si lleva `X-Tai-Strict: 1`.

    El endpoint la declara como último parámetro, después del token: así una petición sin sesión
    o sin permiso sigue siendo un 401 o un 403 antes que un 422, como con cualquier otro parámetro
    que no vale.
    """
    declarados = CONSULTA[(tabla, operacion)]

    async def comprobar(
        request: Request,
        x_tai_strict: Optional[str] = Header(
            None,
            alias="X-Tai-Strict",
            description=(
                "Con 1, un parámetro de consulta que el endpoint no declara, un order_by sobre una "
                "columna que no existe o un include que no existe o pasa de la profundidad máxima "
                "son un 422 en vez de ignorarse."
            ),
        ),
    ) -> None:
        if (x_tai_strict or "").strip() != "1":
            return

        consulta = request.query_params
        errores: List[dict] = []
        for nombre in sorted(set(consulta.keys()) - declarados):
            errores.append({
                "type": "extra_forbidden",
                "loc": ("query", nombre),
                "msg": "este endpoint no tiene ese parámetro",
                "input": consulta.getlist(nombre),
            })
        if "order_by" in declarados:
            for columna in consulta.getlist("order_by"):
                if columna not in COLUMNAS[tabla]:
                    errores.append({
                        "type": "value_error",
                        "loc": ("query", "order_by"),
                        "msg": f"'{columna}' no es una columna de {tabla}",
                        "input": columna,
                    })
        if "includes" in declarados:
            for ruta in consulta.getlist("includes"):
                motivo = include_no_valido(tabla, ruta)
                if motivo is not None:
                    errores.append({"type": "value_error", "loc": ("query", "includes"), "msg": motivo, "input": ruta})
        if errores:
            raise RequestValidationError(errores)

    return comprobar
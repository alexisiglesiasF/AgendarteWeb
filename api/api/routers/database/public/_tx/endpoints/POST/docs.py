#: Cuántas operaciones admite una sola transacción (`TX_LIMIT` del contrato).
TX_LIMIT = 100

TX_SUMMARY = "Varias escrituras del schema public en una sola transacción"

TX_DESCRIPTION = """
Aplica las operaciones **en orden y en una sola transacción**: si una falla, no se aplica
ninguna, y el error dice cuál (`field`: `operations.<i>` o `operations.<i>.values.<campo>`).

```json
{ "operations": [
  { "op": "create", "table": "<tabla>", "values": { … } },
  { "op": "create", "table": "<otra>", "values": { "<fk>": { "$ref": "0.id" } } },
  { "op": "update", "table": "<tabla>", "key": 3, "values": { … } },
  { "op": "delete", "table": "<tabla>", "key": { "<pk1>": 1, "<pk2>": "x" } },
  { "op": "update_many", "table": "<tabla>", "filter": { … }, "values": { … } },
  { "op": "delete_many", "table": "<tabla>", "filter": { … }, "confirm_all": false }
] }
```

- **Cada operación es la de su endpoint**: el mismo cuerpo (`values` de `create` es el
  `<Tabla>Create`; de `update`, el `<Tabla>UpdateValues`; de `update_many`, el `<Tabla>UpdateMany`,
  cuyos `values` no llevan relaciones; `filter` de `delete_many` admite los
  filtros de `DELETE /<tabla>`), el mismo permiso (`<tabla>-<acción>`), el mismo filtrado por fila
  y por propietario y los mismos triggers. Los masivos sin filtro exigen `confirm_all` en su
  operación.
- **El permiso de todas se comprueba antes de escribir nada**: la petición solo pide identidad,
  y una operación sin permiso es un 403 sin que se haya tocado la base de datos.
- `{ "$ref": "<i>.<campo>" }`, en cualquier punto de `values`, `key` o `filter`, toma el campo
  del registro que creó la operación `<i>`, que tiene que ser anterior y un `create`.
- `key` es el valor de la clave primaria o, si es compuesta, un objeto con sus columnas.
- `data` es la lista de resultados, en orden: el registro creado (`create`) o el número de filas
  afectadas (las demás), como responde cada endpoint.
- Solo tablas de este schema; una vista no se puede escribir. Hasta 100 operaciones.
"""

TX_RESPONSES = {
    403: {"description": "Una operación pide un permiso que el usuario no tiene, o escribiría una fila que no es suya"},
    404: {"description": "Una operación apunta a una fila que no existe o que el usuario no puede ver"},
    409: {"description": "Una operación choca con una restricción de unicidad o una clave foránea"},
    422: {"description": "Una operación no es válida, un `$ref` no apunta a nada, o un trigger detuvo la escritura"},
}
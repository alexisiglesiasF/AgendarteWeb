
UPDATE_RESPONSES = {
    200: {
        "description": "Repertorio actualizado exitosamente: cuántas filas cambiaron o, con `Prefer: return=representation`, el registro actualizado (y la cabecera `Preference-Applied`)",
        "headers": {
            "Preference-Applied": {
                "description": "`return=representation` cuando `data` es el registro actualizado. Sin ella, `data` es cuántas filas cambiaron",
                "schema": {"type": "string"},
            },
        },
        "content": {
            "application/json": {
                "example": {
                    "status": "success",
                    "data": 1,
                    "message": "Repertorio actualizado exitosamente",
                    "errors": None,
                    "meta": None
                }
            }
        }
    },
    422: {
        "description": "Error de validación en parámetros o datos",
        "content": {
            "application/json": {
                "example": {
                    "status": "error",
                    "data": None,
                    "message": "Error de validación",
                    "errors": [
                        {
                            "code": "VALIDATION_ERROR",
                            "message": "El valor no es del tipo esperado",
                            "field": "usuario_id",
                            "details": None
                        }
                    ],
                    "meta": None
                }
            }
        }
    },
    404: {
        "description": "Repertorio no encontrado",
        "content": {
            "application/json": {
                "example": {
                    "status": "error",
                    "data": None,
                    "message": "Repertorio no encontrado",
                    "errors": [
                        {
                            "code": "RECORD_NOT_FOUND",
                            "message": "Repertorio no encontrado",
                            "field": None,
                            "details": None
                        }
                    ],
                    "meta": None
                }
            }
        }
    },
    500: {
        "description": "Error interno del servidor",
        "content": {
            "application/json": {
                "example": {
                    "status": "error",
                    "data": None,
                    "message": "Error interno del servidor",
                    "errors": [
                        {
                            "code": "DATABASE_ERROR",
                            "message": "Error en la base de datos",
                            "field": None,
                            "details": None
                        }
                    ],
                    "meta": None
                }
            }
        }
    }
}

UPDATE_SUMMARY = "Actualiza un registro en la tabla repertorio"

UPDATE_DESCRIPTION = """
## Resumen
Actualiza un Repertorio existente identificado por su clave primaria.

Solo se actualizan los campos incluidos en el body. Los campos omitidos **no se modifican**.

## Qué devuelve
Por defecto, en `data`, cuántas filas cambiaron (`1`). Con la cabecera
`Prefer: return=representation`, el **registro actualizado** (`RepertorioRead`), leído en la
misma transacción con las relaciones de `includes` y con el mismo acceso que una lectura: es lo que
devolvería un `GET` después, sin hacerlo. La respuesta lleva entonces
`Preference-Applied: return=representation`.

Si el cambio deja el registro fuera de tu acceso (una regla de filtrado por fila que ya no lo
alcanza), no se puede devolver: `data` es el entero, sin `Preference-Applied`.

## Campos actualizables
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `usuario_id` | `int` | Usuario que crea el evento |
| `id_proyecto` | `int` | Proyecto al que pertenece el repertorio |
| `nombre` | `str` | Nombre del repertorio |
| `descripcion` | `str` | Descripción del repertorio |

## Escrituras anidadas (Nested Writes)
El cuerpo admite operaciones en cascada sobre las filas relacionadas: `create`, `update` y
`delete`, en la misma transacción que el registro.

**Cada escritura anidada pide el permiso de su tabla** (`<tabla>-create`, `-update` o `-delete`, a
cualquier profundidad), además de `repertorio-update`: sin él es un 403
`INSUFFICIENT_PERMISSIONS` con `details.required_permission` y un `field` que dice cuál
(`canciones.create.0`), sin haber escrito nada. Y se le aplica lo mismo que en su endpoint: un
`update` o `delete` de una fila que tu filtrado por fila (RLS o propietario) no alcanza —o que no
existe— es un **404**, y si la tabla tiene reglas de propietario, lo que se crea o se modifica tiene
que seguir siendo tuyo (403 `reason: OWNER`). Si algo falla, no se escribe nada.

### `canciones`
Relación hacia **cancion** (one-to-many): pide `cancion-create`, `-update` o `-delete` según la operación.

```json
{
"usuario_id": "nuevo_valor",
    "canciones": {
        "create": [
            { /* las columnas de cancion */ }
        ],
        "update": [
            {
                /* la clave primaria de cancion */
                "values": { /* las columnas que cambian */ }
            }
        ],
        "delete": [ /* claves primarias de cancion */ ]
    }
}
```

> **Nota:** Las tres operaciones son opcionales e independientes. Puedes enviar solo `create`, solo `delete`, o cualquier combinación.

## Ejemplo básico
```json
{
"usuario_id": 42,
"id_proyecto": 42,
"nombre": "valor_actualizado"
}
```
"""

UPDATE_MANY_RESPONSES = {
    200: {
        "description": "Repertorios actualizados exitosamente",
        "content": {
            "application/json": {
                "examples": {
                    "records_updated": {
                        "summary": "Registros actualizados",
                        "value": {
                            "status": "success",
                            "data": 5,
                            "message": "5 Repertorios actualizados exitosamente",
                            "errors": None,
                            "meta": None
                        }
                    },
                    "no_records_found": {
                        "summary": "No se encontraron registros",
                        "value": {
                            "status": "success",
                            "data": 0,
                            "message": "No se encontraron registros que coincidan con los criterios",
                            "errors": None,
                            "meta": None
                        }
                    }
                }
            }
        }
    },
    422: {
        "description": "Error de validación en los datos",
        "content": {
            "application/json": {
                "example": {
                    "status": "error",
                    "data": None,
                    "message": "Error de validación",
                    "errors": [
                        {
                            "code": "VALIDATION_ERROR",
                            "message": "Los criterios de búsqueda son requeridos",
                            "field": "filters",
                            "details": None
                        }
                    ],
                    "meta": None
                }
            }
        }
    },
    422: {
        "description": "Sin filtros y sin confirm_all=true: la operación alcanzaría todas las filas",
        "content": {
            "application/json": {
                "example": {
                    "status": "error",
                    "data": None,
                    "message": "Sin filtros, esta operación alcanzaría todas las filas. Añade algún filtro, o confirm_all=true si es lo que quieres.",
                    "errors": [
                        {
                            "code": "VALIDATION_ERROR",
                            "message": "Sin filtros, esta operación alcanzaría todas las filas. Añade algún filtro, o confirm_all=true si es lo que quieres.",
                            "field": "confirm_all",
                            "details": None
                        }
                    ],
                    "meta": None
                }
            }
        }
    },
    500: {
        "description": "Error interno del servidor",
        "content": {
            "application/json": {
                "example": {
                    "status": "error",
                    "data": None,
                    "message": "Error interno del servidor",
                    "errors": [
                        {
                            "code": "DATABASE_ERROR",
                            "message": "Error en la base de datos",
                            "field": None,
                            "details": None
                        }
                    ],
                    "meta": None
                }
            }
        }
    }
}

UPDATE_MANY_SUMMARY = "Actualiza múltiples registros en la tabla repertorio"

UPDATE_MANY_DESCRIPTION = """
Actualiza con los mismos `values` todas las filas que cumplen `filter`. Sin ningún filtro exige
`confirm_all=true`.

**No admite escrituras anidadas** (`canciones`): `values` solo lleva columnas, y
mandarlas es un 422 sobre `values`. Para escribir en las filas relacionadas, `PATCH /repertorio/<clave>`.
"""
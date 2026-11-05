
UPDATE_RESPONSES = {
    200: {
        "description": "Usuario actualizado exitosamente: cuántas filas cambiaron o, con `Prefer: return=representation`, el registro actualizado (y la cabecera `Preference-Applied`)",
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
                    "message": "Usuario actualizado exitosamente",
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
                            "field": "nombre",
                            "details": None
                        }
                    ],
                    "meta": None
                }
            }
        }
    },
    404: {
        "description": "Usuario no encontrado",
        "content": {
            "application/json": {
                "example": {
                    "status": "error",
                    "data": None,
                    "message": "Usuario no encontrado",
                    "errors": [
                        {
                            "code": "RECORD_NOT_FOUND",
                            "message": "Usuario no encontrado",
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

UPDATE_SUMMARY = "Actualiza un registro en la tabla usuario"

UPDATE_DESCRIPTION = """
## Resumen
Actualiza un Usuario existente identificado por su clave primaria.

Solo se actualizan los campos incluidos en el body. Los campos omitidos **no se modifican**.

## Qué devuelve
Por defecto, en `data`, cuántas filas cambiaron (`1`). Con la cabecera
`Prefer: return=representation`, el **registro actualizado** (`UsuarioRead`), leído en la
misma transacción con las relaciones de `includes` y con el mismo acceso que una lectura: es lo que
devolvería un `GET` después, sin hacerlo. La respuesta lleva entonces
`Preference-Applied: return=representation`.

Si el cambio deja el registro fuera de tu acceso (una regla de filtrado por fila que ya no lo
alcanza), no se puede devolver: `data` es el entero, sin `Preference-Applied`.

## Campos actualizables
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `nombre` | `str` | Nombre visible |
| `apellido` | `str` | Apellido visible |
| `email` | `str` | Campo email de la tabla usuario |

## Escrituras anidadas (Nested Writes)
El cuerpo admite operaciones en cascada sobre las filas relacionadas: `create`, `update` y
`delete`, en la misma transacción que el registro.

### `proyectos`
Relación hacia **proyecto** (one-to-many).

```json
{
"nombre": "nuevo_valor",
    "proyectos": {
        "create": [
            { /* las columnas de proyecto */ }
        ],
        "update": [
            {
                /* la clave primaria de proyecto */
                "values": { /* las columnas que cambian */ }
            }
        ],
        "delete": [ /* claves primarias de proyecto */ ]
    }
}
```
### `eventos`
Relación hacia **evento** (one-to-many).

```json
{
"nombre": "nuevo_valor",
    "eventos": {
        "create": [
            { /* las columnas de evento */ }
        ],
        "update": [
            {
                /* la clave primaria de evento */
                "values": { /* las columnas que cambian */ }
            }
        ],
        "delete": [ /* claves primarias de evento */ ]
    }
}
```
### `repertorios`
Relación hacia **repertorio** (one-to-many).

```json
{
"nombre": "nuevo_valor",
    "repertorios": {
        "create": [
            { /* las columnas de repertorio */ }
        ],
        "update": [
            {
                /* la clave primaria de repertorio */
                "values": { /* las columnas que cambian */ }
            }
        ],
        "delete": [ /* claves primarias de repertorio */ ]
    }
}
```

> **Nota:** Las tres operaciones son opcionales e independientes. Puedes enviar solo `create`, solo `delete`, o cualquier combinación.

## Ejemplo básico
```json
{
"nombre": "valor_actualizado",
"apellido": "valor_actualizado",
"email": "valor_actualizado"
}
```
"""

UPDATE_MANY_RESPONSES = {
    200: {
        "description": "Usuarios actualizados exitosamente",
        "content": {
            "application/json": {
                "examples": {
                    "records_updated": {
                        "summary": "Registros actualizados",
                        "value": {
                            "status": "success",
                            "data": 5,
                            "message": "5 Usuarios actualizados exitosamente",
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

UPDATE_MANY_SUMMARY = "Actualiza múltiples registros en la tabla usuario"

UPDATE_MANY_DESCRIPTION = """
Actualiza con los mismos `values` todas las filas que cumplen `filter`. Sin ningún filtro exige
`confirm_all=true`.

**No admite escrituras anidadas** (`proyectos`, `eventos`, `repertorios`): `values` solo lleva columnas, y
mandarlas es un 422 sobre `values`. Para escribir en las filas relacionadas, `PATCH /usuario/<clave>`.
"""
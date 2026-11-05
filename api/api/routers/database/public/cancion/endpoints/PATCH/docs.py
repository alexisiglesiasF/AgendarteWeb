
UPDATE_RESPONSES = {
    200: {
        "description": "Cancion actualizado exitosamente: cuántas filas cambiaron o, con `Prefer: return=representation`, el registro actualizado (y la cabecera `Preference-Applied`)",
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
                    "message": "Cancion actualizado exitosamente",
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
                            "field": "id_repertorio",
                            "details": None
                        }
                    ],
                    "meta": None
                }
            }
        }
    },
    404: {
        "description": "Cancion no encontrado",
        "content": {
            "application/json": {
                "example": {
                    "status": "error",
                    "data": None,
                    "message": "Cancion no encontrado",
                    "errors": [
                        {
                            "code": "RECORD_NOT_FOUND",
                            "message": "Cancion no encontrado",
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

UPDATE_SUMMARY = "Actualiza un registro en la tabla cancion"

UPDATE_DESCRIPTION = """
## Resumen
Actualiza un Cancion existente identificado por su clave primaria.

Solo se actualizan los campos incluidos en el body. Los campos omitidos **no se modifican**.

## Qué devuelve
Por defecto, en `data`, cuántas filas cambiaron (`1`). Con la cabecera
`Prefer: return=representation`, el **registro actualizado** (`CancionRead`), leído en la
misma transacción con las relaciones de `includes` y con el mismo acceso que una lectura: es lo que
devolvería un `GET` después, sin hacerlo. La respuesta lleva entonces
`Preference-Applied: return=representation`.

Si el cambio deja el registro fuera de tu acceso (una regla de filtrado por fila que ya no lo
alcanza), no se puede devolver: `data` es el entero, sin `Preference-Applied`.

## Campos actualizables
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id_repertorio` | `int` | Repertorio al que pertenece la canción |
| `nombre` | `str` | Nombre de la canción |


## Ejemplo básico
```json
{
"id_repertorio": 42,
"nombre": "valor_actualizado"
}
```
"""

UPDATE_MANY_RESPONSES = {
    200: {
        "description": "Cancions actualizados exitosamente",
        "content": {
            "application/json": {
                "examples": {
                    "records_updated": {
                        "summary": "Registros actualizados",
                        "value": {
                            "status": "success",
                            "data": 5,
                            "message": "5 Cancions actualizados exitosamente",
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

UPDATE_MANY_SUMMARY = "Actualiza múltiples registros en la tabla cancion"

UPDATE_MANY_DESCRIPTION = """
Actualiza con los mismos `values` todas las filas que cumplen `filter`. Sin ningún filtro exige
`confirm_all=true`.
"""
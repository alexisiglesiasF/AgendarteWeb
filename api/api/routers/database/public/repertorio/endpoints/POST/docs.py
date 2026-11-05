
CREATE_RESPONSES = {
    422: {
        "description": "Error de validación en los datos de entrada",
        "content": {
            "application/json": {
                "example": {
                    "status": "error",
                    "data": None,
                    "message": "Error de validación",
                    "errors": [
                        {
                            "code": "VALIDATION_ERROR",
                            "message": "El campo es requerido",
                            "field": "usuario_id",
                            "details": None
                        }
                    ],
                    "meta": None
                }
            }
        }
    },
    409: {
        "description": "Registro duplicado",
        "content": {
            "application/json": {
                "example": {
                    "status": "error",
                    "data": None,
                    "message": "El registro ya existe",
                    "errors": [
                        {
                            "code": "DUPLICATE_RECORD",
                            "message": "El registro ya existe",
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

CREATE_SUMMARY = "Crea un registro en la tabla repertorio"

CREATE_DESCRIPTION = """
Crea un Repertorio y devuelve el registro creado.

## Escrituras anidadas
Con el registro se pueden crear filas relacionadas, en el mismo cuerpo y en la misma transacción:

- `canciones`: una lista de filas de `cancion`.
- `usuario`: una fila de `usuario`.
- `proyecto`: una fila de `proyecto`.
"""

#: Cuántos registros admite una sola petición a `/bulk`: van todos en una transacción.
CREATE_MANY_LIMIT = 1000

CREATE_MANY_SUMMARY = "Crea varios registros en la tabla repertorio"

CREATE_MANY_DESCRIPTION = (
    "Crea los registros de la lista, en orden y en una sola transacción: si uno falla "
    "—un duplicado, una clave foránea, una regla de negocio—, no se crea ninguno. "
    "Devuelve los registros creados, en el mismo orden. "
    f"Admite hasta {CREATE_MANY_LIMIT} por petición; para más, se envían en varias."
)

#: Las de `create`; en un 422 de validación, `field` lleva la posición en la lista: `3.campo`.
CREATE_MANY_RESPONSES = CREATE_RESPONSES

AGG_RESPONSES = {
    200: {
        "description": "Agregaciones calculadas exitosamente",
        "content": {
            "application/json": {
                "example": {
                    "status": "success",
                    "data": {
                        "sum_edad": 450,
                        "sum_salario": 150000.50,
                        "mean_edad": 30.5,
                        "max_fecha_nacimiento": "2000-01-15T00:00:00",
                        "min_fecha_nacimiento": "1970-05-20T00:00:00"
                    },
                    "message": "Agregaciones calculadas exitosamente",
                    "meta": {
                        "total_operations": 4,
                        "valid_operations": 4,
                        "total_expressions": 5,
                        "warnings": []
                    }
                }
            }
        }
    },
    422: {
        "description": "Error de validación en operaciones o filtros",
        "content": {
            "application/json": {
                "example": {
                    "status": "error",
                    "data": None,
                    "message": "Error de validación",
                    "errors": [
                        {
                            "code": "VALIDATION_ERROR",
                            "message": "Operación 'median' no soportada. Operaciones válidas: ['sum', 'mean', 'max', 'min']",
                            "field": "operations",
                            "details": None
                        }
                    ]
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
                            "code": "INTERNAL_SERVER_ERROR",
                            "message": "Ha ocurrido un error inesperado",
                            "field": None,
                            "details": None
                        }
                    ]
                }
            }
        }
    }
}

AGG_SUMMARY = "Realiza múltiples agregaciones en la tabla repertorio"

AGG_DESCRIPTION = """
## Resumen
Realiza múltiples operaciones de agregación en una sola consulta sobre la tabla repertorio.

Este endpoint permite combinar diferentes operaciones de agregación (sum, mean, max, min, count) 
sobre múltiples campos en una única petición.

## Cuerpo de la Petición

### operations (requerido)
Diccionario donde cada clave es una operación y el valor es una lista de campos o expresiones.

#### Operaciones disponibles:
- **sum**: Suma de valores numéricos
- **mean**: Promedio de valores numéricos
- **max**: Valor máximo (numérico o fechas)
- **min**: Valor mínimo (numérico o fechas)
- **count**: Conteo de registros

### filters (opcional)
Diccionario con filtros a aplicar:
- **in_id**: Filtrar por múltiples valores de id (OR lógico)
    - **usuario_id**: Filtrar por usuario_id
    - **in_usuario_id**: Filtrar por múltiples valores de usuario_id (OR lógico)
    - **id_proyecto**: Filtrar por id_proyecto
    - **in_id_proyecto**: Filtrar por múltiples valores de id_proyecto (OR lógico)
    - **nombre**: Filtrar por nombre
    - **in_nombre**: Filtrar por múltiples valores de nombre (OR lógico)
    - **descripcion**: Filtrar por descripcion
    - **in_descripcion**: Filtrar por múltiples valores de descripcion (OR lógico)
    - **min_created_at**: Filtrar por valor mínimo de created_at (incluído)
    - **max_created_at**: Filtrar por valor máximo de created_at (incluído)
    - **in_created_by**: Filtrar por múltiples valores de created_by (OR lógico)
    - **min_updated_at**: Filtrar por valor mínimo de updated_at (incluído)
    - **max_updated_at**: Filtrar por valor máximo de updated_at (incluído)
    - **in_updated_by**: Filtrar por múltiples valores de updated_by (OR lógico)

"""
from typing import Optional, List, Union

FIND_MANY_RESPONSES = {
    200: {
        "description": "Lista de registros de repertorio obtenido exitosamente",
        "content": {
            "application/json": {
                "schema": {
                    "$ref": "#/components/schemas/APIResponse_List_RepertorioRead__"
                }
            }
        },
        "links": {
            "self": {
                "operationId": "public_repertorio_find_many",
                "description": "La misma consulta, con los mismos filtros",
                "parameters": {
                    "in_id": "$request.query.in_id",
                    "usuario_id": "$request.query.usuario_id",
                    "in_usuario_id": "$request.query.in_usuario_id",
                    "id_proyecto": "$request.query.id_proyecto",
                    "in_id_proyecto": "$request.query.in_id_proyecto",
                    "nombre": "$request.query.nombre",
                    "in_nombre": "$request.query.in_nombre",
                    "descripcion": "$request.query.descripcion",
                    "in_descripcion": "$request.query.in_descripcion",
                    "min_created_at": "$request.query.min_created_at",
                    "max_created_at": "$request.query.max_created_at",
                    "in_created_by": "$request.query.in_created_by",
                    "min_updated_at": "$request.query.min_updated_at",
                    "max_updated_at": "$request.query.max_updated_at",
                    "in_updated_by": "$request.query.in_updated_by",
                    "limit": "$request.query.limit",
                    "offset": "$request.query.offset",
                    "order_by": "$request.query.order_by",
                    "order": "$request.query.order",
                    "includes": "$request.query.includes"
                }
            },
            "count": {
                "operationId": "public_repertorio_count",
                "description": "Cuántos registros hay con los mismos filtros",
                "parameters": {
                    "in_id": "$request.query.in_id",
                    "usuario_id": "$request.query.usuario_id",
                    "in_usuario_id": "$request.query.in_usuario_id",
                    "id_proyecto": "$request.query.id_proyecto",
                    "in_id_proyecto": "$request.query.in_id_proyecto",
                    "nombre": "$request.query.nombre",
                    "in_nombre": "$request.query.in_nombre",
                    "descripcion": "$request.query.descripcion",
                    "in_descripcion": "$request.query.in_descripcion",
                    "min_created_at": "$request.query.min_created_at",
                    "max_created_at": "$request.query.max_created_at",
                    "in_created_by": "$request.query.in_created_by",
                    "min_updated_at": "$request.query.min_updated_at",
                    "max_updated_at": "$request.query.max_updated_at",
                    "in_updated_by": "$request.query.in_updated_by"
                }
            },
            "create": {
                "operationId": "public_repertorio_create",
                "description": "Crear un nuevo Repertorio"
            }
        }
    },
    422: {
        "description": "Error de validación en parámetros",
        "content": {
            "application/json": {
                "example": {
                    "status": "error",
                    "data": None,
                    "message": "Error de validación",
                    "errors": [
                        {
                            "code": "VALIDATION_ERROR",
                            "message": "El límite no puede ser negativo",
                            "field": "limit",
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

FIND_MANY_SUMMARY = "Busca varios registros en la tabla repertorio"
FIND_MANY_DESCRIPTION = """
## Resumen
Obtiene una lista de `repertorios` con filtros opcionales y soporte para paginación.

Este endpoint permite realizar búsquedas flexibles aplicando filtros opcionales
por cualquiera de los campos disponibles, con soporte completo para paginación
mediante los parámetros limit y offset.

## Resultado
En `APIResponse.data`, retorna un listado de objetos donde cada uno representa un registro de la tabla `repertorio` que incluye todos sus atributos

## Datos
Para cada registro en `data` se incluye:
- **id** (int): Campo id de la tabla repertorio
- **usuario_id** (int): Usuario que crea el evento
- **id_proyecto** (int, opcional): Proyecto al que pertenece el repertorio
- **nombre** (str): Nombre del repertorio
- **descripcion** (str, opcional): Descripción del repertorio
- **created_at** (datetime): Fecha y hora de creación del registro en Repertorio
- **created_by** (str): Usuario que creó el registro en Repertorio
- **updated_at** (datetime): Fecha y hora de la última actualización del registro en Repertorio
- **updated_by** (str): Usuario que realizó la última actualización del registro en Repertorio

## Parámetros de Filtrado

Todos los parámetros de filtrado son opcionales y se pueden combinar:
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


## Parámetros de Paginación

- **limit**: Número máximo de registros a retornar. Solo admite valores positivos. Si no se especifica, retorna todos los registros que coincidan con los filtros.
- **order_by**: Lista de nombres de columnas para ordenar los resultados.⚠️ **IMPORTANTE**: los nombres de columnas deben existir, si no serán omitidas.
- **order**: Dirección de ordenamiento: 'ASC' para ascendente (por defecto), 'DESC' para descendente. Solo aplica si order_by está definido.
- **offset**: Número de registros a omitir desde el inicio. Solo admite valores positivos. Si no se especifica, inicia desde el primer registro.

## Consulta combinada (recomendado para pocos registros)
⚠️ **IMPORTANTE**: Usa siempre el parámetro `includes` para cargar relaciones en una sola consulta y evitar múltiples llamadas al API.

⚠️ **WARNING**: Si la relación incluida tiene muchos registros relacionados, la respuesta puede ser muy grande y lenta. Mejor consultar su endpoint directamente con filtros.

El parametro `includes` permite cargar relaciones asociadas a los registros.

### Relaciones disponibles
- **canciones**: lista de Cancion relacionados (one-to-many)

    - **descripción**: Canciones del usuario
- **usuario**: Usuario relacionado (many-to-one)

    - **descripción**: Usuarios del sistema.
- **proyecto**: Proyecto relacionado (many-to-one)

    - **descripción**: Proyectos del usuario.

### Ejemplos básicos:
#### Solo datos básicos
`repertorio = GET /repertorio`

#### Incluir canciones
`repertorio = GET /repertorio?includes=canciones`

#### Incluir usuario
`repertorio = GET /repertorio?includes=usuario`

#### Incluir proyecto
`repertorio = GET /repertorio?includes=proyecto`

#### Múltiples relaciones en una sola consulta
`repertorio = GET /repertorio?includes=canciones&includes=usuario`

#### Relaciones anidadas
Puedes incluir los datos de canciones y además incluir sus propias relaciones  
`repertorio = GET /repertorio?includes=canciones.{nested_relation}`  
Puedes incluir los datos de usuario y además incluir sus propias relaciones  
`repertorio = GET /repertorio?includes=usuario.{nested_relation}`  
Puedes incluir los datos de proyecto y además incluir sus propias relaciones  
`repertorio = GET /repertorio?includes=proyecto.{nested_relation}`  
"""

COUNT_RESPONSES = {
    200: {
        "description": "Conteo realizado exitosamente",
        "content": {
            "application/json": {
                "example": {
                    "status": "success",
                    "data": 42,
                    "message": "Conteo realizado exitosamente",
                    "errors": None,
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

COUNT_SUMMARY = "Cuenta registros en la tabla repertorio"

EXISTS_RESPONSES = {
    200: {
        "description": "Verificación realizada exitosamente",
        "content": {
            "application/json": {
                "example": {
                    "status": "success",
                    "data": True,
                    "message": "Verificación realizada exitosamente",
                    "errors": None,
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

EXISTS_SUMMARY = "Verifica existencia en la tabla repertorio"

AGG_FIELD_422 = {
    "description": "Campo inválido o no válido para la operación",
    "content": {
        "application/json": {
            "example": {
                "status": "error",
                "data": None,
                "message": "Error de validación",
                "errors": [
                    {
                        "code": "VALIDATION_ERROR",
                        "message": "El campo especificado no es válido para la operación",
                        "field": "field",
                        "details": None
                    }
                ],
                "meta": None
            }
        }
    }
}

AGG_FIELD_500 = {
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

SUM_RESPONSES = {
    200: {
        "description": "Suma calculada exitosamente",
        "content": {
            "application/json": {
                "example": {
                    "status": "success",
                    "data": 12500.75,
                    "message": "Suma de 'campo' calculada exitosamente",
                    "errors": None,
                    "meta": None
                }
            }
        }
    },
    422: AGG_FIELD_422,
    500: AGG_FIELD_500
}

SUM_SUMMARY = "Suma un campo numérico específico en la tabla repertorio"

MEAN_RESPONSES = {
    200: {
        "description": "Media calculada exitosamente",
        "content": {
            "application/json": {
                "example": {
                    "status": "success",
                    "data": 32.45,
                    "message": "Media de 'campo' calculada exitosamente",
                    "errors": None,
                    "meta": None
                }
            }
        }
    },
    422: AGG_FIELD_422,
    500: AGG_FIELD_500
}

MEAN_SUMMARY = "Calcula la media de un campo numérico específico en la tabla repertorio"

MAX_RESPONSES = {
    200: {
        "description": "Valor máximo encontrado exitosamente",
        "content": {
            "application/json": {
                "example": {
                    "status": "success",
                    "data": 99999.99,
                    "message": "Máximo de 'campo' encontrado exitosamente",
                    "errors": None,
                    "meta": None
                }
            }
        }
    },
    422: AGG_FIELD_422,
    500: AGG_FIELD_500
}

MAX_SUMMARY = "Encuentra el valor máximo de un campo específico en la tabla repertorio"

MIN_RESPONSES = {
    200: {
        "description": "Valor mínimo encontrado exitosamente",
        "content": {
            "application/json": {
                "example": {
                    "status": "success",
                    "data": 100.00,
                    "message": "Mínimo de 'campo' encontrado exitosamente",
                    "errors": None,
                    "meta": None
                }
            }
        }
    },
    422: AGG_FIELD_422,
    500: AGG_FIELD_500
}

MIN_SUMMARY = "Encuentra el valor mínimo de un campo específico en la tabla repertorio"

FIND_RESPONSES = {
    200: {
        "description": "Registro único de repertorio obtenido exitosamente",
        "content": {
            "application/json": {
                "schema": {
                    "$ref": "#/components/schemas/APIResponse_RepertorioRead_"
                }
            }
        },
        "links": {
            "self": {
                "operationId": "public_repertorio_find",
                "description": "El recurso actual",
                "parameters": {
                    "id": "$response.body#/data/id",
                    "includes": "$request.query.includes"
                }
            },
            "collection": {
                "operationId": "public_repertorio_find_many",
                "description": "La colección de Repertorio"
            },
            "edit": {
                "operationId": "public_repertorio_update",
                "description": "Actualizar este Repertorio",
                "parameters": {
                    "id": "$response.body#/data/id"
                }
            },
            "delete": {
                "operationId": "public_repertorio_delete",
                "description": "Eliminar este Repertorio",
                "parameters": {
                    "id": "$response.body#/data/id"
                }
            },
            "canciones": {
                "operationId": "public_cancion_find_many",
                "description": "Los Cancion relacionados",
                "parameters": {
                    "id_repertorio": "$response.body#/data/id"
                }
            },
            "usuario": {
                "operationId": "public_usuario_find",
                "description": "El Usuario relacionado",
                "parameters": {
                    "id": "$response.body#/data/usuario_id"
                }
            },
            "proyecto": {
                "operationId": "public_proyecto_find",
                "description": "El Proyecto relacionado",
                "parameters": {
                    "id": "$response.body#/data/id_proyecto"
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

FIND_BY_RESPONSES = {
    200: {
        "description": "Registro único de repertorio obtenido exitosamente",
        "content": {
            "application/json": {
                "schema": {
                    "$ref": "#/components/schemas/APIResponse_RepertorioRead_"
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
    422: {
        "description": "Lo dado no es exactamente una de las claves únicas",
        "content": {
            "application/json": {
                "example": {
                    "status": "error",
                    "data": None,
                    "message": "Se busca por una sola clave única, entera: (nombre)",
                    "errors": [
                        {
                            "code": "VALIDATION_ERROR",
                            "message": "Se busca por una sola clave única, entera: (nombre)",
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

FIND_BY_SUMMARY = "Busca un registro en la tabla repertorio por una clave única"

FIND_BY_DESCRIPTION = """
## Resumen
Obtiene un Repertorio por una de sus claves únicas, como `GET /public/repertorio/{id:int}` por la
clave primaria.

## Claves
Cada petición busca por **una** clave, con todas sus columnas y solo ellas:
- `GET /public/repertorio/find-by?nombre=...`

Media clave no: no sería un solo registro.
Lo que no es exactamente una clave es un 422 `VALIDATION_ERROR` que dice cuáles valen.

## Resultado
En `APIResponse.data`, el registro de la tabla `repertorio` con todos sus atributos. Si no
hay ninguno con esa clave, o tu acceso no lo alcanza, un 404 `RECORD_NOT_FOUND`.

## Datos
Para cada registro en `data` se incluye:
- **id** (int): Campo id de la tabla repertorio
- **usuario_id** (int): Usuario que crea el evento
- **id_proyecto** (int, opcional): Proyecto al que pertenece el repertorio
- **nombre** (str): Nombre del repertorio
- **descripcion** (str, opcional): Descripción del repertorio
- **created_at** (datetime): Fecha y hora de creación del registro en Repertorio
- **created_by** (str): Usuario que creó el registro en Repertorio
- **updated_at** (datetime): Fecha y hora de la última actualización del registro en Repertorio
- **updated_by** (str): Usuario que realizó la última actualización del registro en Repertorio

## Relaciones (parámetro `includes`)
- canciones: Lista de Cancion relacionados (one-to-many)
- usuario: Usuario relacionado (many-to-one)
- proyecto: Proyecto relacionado (many-to-one)
"""

FIND_SUMMARY = "Busca un registro en la tabla repertorio"

FIND_DESCRIPTION = """
## Resumen
Obtiene un Repertorio específico por su clave primaria.

Este endpoint permite recuperar un registro individual de Repertorio
utilizando su identificador único (clave primaria). Opcionalmente puede
incluir datos de relaciones asociadas.

## Resultado
Si la consulta es exitosa, en `APIResponse.data`, retorna un objeto que representa un registro de la tabla `repertorio` que incluye todos sus atributos

Si no se encuentra el registro, devuelve un error 404 `RECORD_NOT_FOUND`.

## Datos
Para cada registro en `data` se incluye:
- **id** (int): Campo id de la tabla repertorio
- **usuario_id** (int): Usuario que crea el evento
- **id_proyecto** (int, opcional): Proyecto al que pertenece el repertorio
- **nombre** (str): Nombre del repertorio
- **descripcion** (str, opcional): Descripción del repertorio
- **created_at** (datetime): Fecha y hora de creación del registro en Repertorio
- **created_by** (str): Usuario que creó el registro en Repertorio
- **updated_at** (datetime): Fecha y hora de la última actualización del registro en Repertorio
- **updated_by** (str): Usuario que realizó la última actualización del registro en Repertorio

## Parámetros de Identificación

- **id**: id del Repertorio a buscar (tipo: int)

## Consulta combinada (RECOMENDADO)
⚠️ **IMPORTANTE**: Usa siempre el parámetro `includes` para cargar relaciones en una sola consulta y evitar múltiples llamadas al API.

El parametro `includes` permite cargar relaciones asociadas a los registros.

### Relaciones disponibles (usar con parámetro 'includes'):
- canciones: Lista de Cancion relacionados (one-to-many)
    Canciones del usuario
- usuario: Usuario relacionado (many-to-one)
    Usuarios del sistema.
- proyecto: Proyecto relacionado (many-to-one)
    Proyectos del usuario.

### Uso del parámetro 'includes':
Para cargar relaciones específicas, usa el parámetro 'includes' en la consulta:

### Ejemplos básicos:
#### Solo datos básicos
`repertorio = GET /repertorio/{id:int}`

#### Incluir canciones
`repertorio = GET /repertorio/{id:int}?includes=canciones`

#### Incluir usuario
`repertorio = GET /repertorio/{id:int}?includes=usuario`

#### Incluir proyecto
`repertorio = GET /repertorio/{id:int}?includes=proyecto`

#### Múltiples relaciones en una sola consulta
`repertorio = GET /repertorio/{id:int}?includes=canciones&includes=usuario`

#### Relaciones anidadas
Puedes incluir los datos de canciones y además incluir sus propias relaciones  
`repertorio = GET /repertorio/{id:int}?includes=canciones.{nested_relation}`
Puedes incluir los datos de usuario y además incluir sus propias relaciones  
`repertorio = GET /repertorio/{id:int}?includes=usuario.{nested_relation}`
Puedes incluir los datos de proyecto y además incluir sus propias relaciones  
`repertorio = GET /repertorio/{id:int}?includes=proyecto.{nested_relation}`
"""

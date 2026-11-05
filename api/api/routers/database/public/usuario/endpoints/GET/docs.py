from typing import Optional, List, Union

FIND_MANY_RESPONSES = {
    200: {
        "description": "Lista de registros de usuario obtenido exitosamente",
        "content": {
            "application/json": {
                "schema": {
                    "$ref": "#/components/schemas/APIResponse_List_UsuarioRead__"
                }
            }
        },
        "links": {
            "self": {
                "operationId": "public_usuario_find_many",
                "description": "La misma consulta, con los mismos filtros",
                "parameters": {
                    "in_id": "$request.query.in_id",
                    "nombre": "$request.query.nombre",
                    "in_nombre": "$request.query.in_nombre",
                    "apellido": "$request.query.apellido",
                    "in_apellido": "$request.query.in_apellido",
                    "email": "$request.query.email",
                    "in_email": "$request.query.in_email",
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
                "operationId": "public_usuario_count",
                "description": "Cuántos registros hay con los mismos filtros",
                "parameters": {
                    "in_id": "$request.query.in_id",
                    "nombre": "$request.query.nombre",
                    "in_nombre": "$request.query.in_nombre",
                    "apellido": "$request.query.apellido",
                    "in_apellido": "$request.query.in_apellido",
                    "email": "$request.query.email",
                    "in_email": "$request.query.in_email",
                    "min_created_at": "$request.query.min_created_at",
                    "max_created_at": "$request.query.max_created_at",
                    "in_created_by": "$request.query.in_created_by",
                    "min_updated_at": "$request.query.min_updated_at",
                    "max_updated_at": "$request.query.max_updated_at",
                    "in_updated_by": "$request.query.in_updated_by"
                }
            },
            "create": {
                "operationId": "public_usuario_create",
                "description": "Crear un nuevo Usuario"
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

FIND_MANY_SUMMARY = "Busca varios registros en la tabla usuario"
FIND_MANY_DESCRIPTION = """
## Resumen
Obtiene una lista de `usuarios` con filtros opcionales y soporte para paginación.

Este endpoint permite realizar búsquedas flexibles aplicando filtros opcionales
por cualquiera de los campos disponibles, con soporte completo para paginación
mediante los parámetros limit y offset.

## Resultado
En `APIResponse.data`, retorna un listado de objetos donde cada uno representa un registro de la tabla `usuario` que incluye todos sus atributos

## Datos
Para cada registro en `data` se incluye:
- **id** (int): Campo id de la tabla usuario
- **nombre** (str): Nombre visible
- **apellido** (str): Apellido visible
- **email** (str): Campo email de la tabla usuario
- **created_at** (datetime): Fecha y hora de creación del registro en Usuario
- **created_by** (str): Usuario que creó el registro en Usuario
- **updated_at** (datetime): Fecha y hora de la última actualización del registro en Usuario
- **updated_by** (str): Usuario que realizó la última actualización del registro en Usuario

## Parámetros de Filtrado

Todos los parámetros de filtrado son opcionales y se pueden combinar:
- **in_id**: Filtrar por múltiples valores de id (OR lógico)
    - **nombre**: Filtrar por nombre
    - **in_nombre**: Filtrar por múltiples valores de nombre (OR lógico)
    - **apellido**: Filtrar por apellido
    - **in_apellido**: Filtrar por múltiples valores de apellido (OR lógico)
    - **email**: Filtrar por email
    - **in_email**: Filtrar por múltiples valores de email (OR lógico)
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
- **proyectos**: lista de Proyecto relacionados (one-to-many)

    - **descripción**: Proyectos del usuario.
- **eventos**: lista de Evento relacionados (one-to-many)

    - **descripción**: Eventos del musico
- **repertorios**: lista de Repertorio relacionados (one-to-many)

    - **descripción**: Repertorios del usuario

### Ejemplos básicos:
#### Solo datos básicos
`usuario = GET /usuario`

#### Incluir proyectos
`usuario = GET /usuario?includes=proyectos`

#### Incluir eventos
`usuario = GET /usuario?includes=eventos`

#### Incluir repertorios
`usuario = GET /usuario?includes=repertorios`

#### Múltiples relaciones en una sola consulta
`usuario = GET /usuario?includes=proyectos&includes=eventos`

#### Relaciones anidadas
Puedes incluir los datos de proyectos y además incluir sus propias relaciones  
`usuario = GET /usuario?includes=proyectos.{nested_relation}`  
Puedes incluir los datos de eventos y además incluir sus propias relaciones  
`usuario = GET /usuario?includes=eventos.{nested_relation}`  
Puedes incluir los datos de repertorios y además incluir sus propias relaciones  
`usuario = GET /usuario?includes=repertorios.{nested_relation}`  
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

COUNT_SUMMARY = "Cuenta registros en la tabla usuario"

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

EXISTS_SUMMARY = "Verifica existencia en la tabla usuario"

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

SUM_SUMMARY = "Suma un campo numérico específico en la tabla usuario"

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

MEAN_SUMMARY = "Calcula la media de un campo numérico específico en la tabla usuario"

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

MAX_SUMMARY = "Encuentra el valor máximo de un campo específico en la tabla usuario"

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

MIN_SUMMARY = "Encuentra el valor mínimo de un campo específico en la tabla usuario"

FIND_RESPONSES = {
    200: {
        "description": "Registro único de usuario obtenido exitosamente",
        "content": {
            "application/json": {
                "schema": {
                    "$ref": "#/components/schemas/APIResponse_UsuarioRead_"
                }
            }
        },
        "links": {
            "self": {
                "operationId": "public_usuario_find",
                "description": "El recurso actual",
                "parameters": {
                    "id": "$response.body#/data/id",
                    "includes": "$request.query.includes"
                }
            },
            "collection": {
                "operationId": "public_usuario_find_many",
                "description": "La colección de Usuario"
            },
            "edit": {
                "operationId": "public_usuario_update",
                "description": "Actualizar este Usuario",
                "parameters": {
                    "id": "$response.body#/data/id"
                }
            },
            "delete": {
                "operationId": "public_usuario_delete",
                "description": "Eliminar este Usuario",
                "parameters": {
                    "id": "$response.body#/data/id"
                }
            },
            "proyectos": {
                "operationId": "public_proyecto_find_many",
                "description": "Los Proyecto relacionados",
                "parameters": {
                    "id_usuario": "$response.body#/data/id"
                }
            },
            "eventos": {
                "operationId": "public_evento_find_many",
                "description": "Los Evento relacionados",
                "parameters": {
                    "usuario_id": "$response.body#/data/id"
                }
            },
            "repertorios": {
                "operationId": "public_repertorio_find_many",
                "description": "Los Repertorio relacionados",
                "parameters": {
                    "usuario_id": "$response.body#/data/id"
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

FIND_BY_RESPONSES = {
    200: {
        "description": "Registro único de usuario obtenido exitosamente",
        "content": {
            "application/json": {
                "schema": {
                    "$ref": "#/components/schemas/APIResponse_UsuarioRead_"
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
    422: {
        "description": "Lo dado no es exactamente una de las claves únicas",
        "content": {
            "application/json": {
                "example": {
                    "status": "error",
                    "data": None,
                    "message": "Se busca por una sola clave única, entera: (email)",
                    "errors": [
                        {
                            "code": "VALIDATION_ERROR",
                            "message": "Se busca por una sola clave única, entera: (email)",
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

FIND_BY_SUMMARY = "Busca un registro en la tabla usuario por una clave única"

FIND_BY_DESCRIPTION = """
## Resumen
Obtiene un Usuario por una de sus claves únicas, como `GET /public/usuario/{id:int}` por la
clave primaria.

## Claves
Cada petición busca por **una** clave, con todas sus columnas y solo ellas:
- `GET /public/usuario/find-by?email=...`

Media clave no: no sería un solo registro.
Lo que no es exactamente una clave es un 422 `VALIDATION_ERROR` que dice cuáles valen.

## Resultado
En `APIResponse.data`, el registro de la tabla `usuario` con todos sus atributos. Si no
hay ninguno con esa clave, o tu acceso no lo alcanza, un 404 `RECORD_NOT_FOUND`.

## Datos
Para cada registro en `data` se incluye:
- **id** (int): Campo id de la tabla usuario
- **nombre** (str): Nombre visible
- **apellido** (str): Apellido visible
- **email** (str): Campo email de la tabla usuario
- **created_at** (datetime): Fecha y hora de creación del registro en Usuario
- **created_by** (str): Usuario que creó el registro en Usuario
- **updated_at** (datetime): Fecha y hora de la última actualización del registro en Usuario
- **updated_by** (str): Usuario que realizó la última actualización del registro en Usuario

## Relaciones (parámetro `includes`)
- proyectos: Lista de Proyecto relacionados (one-to-many)
- eventos: Lista de Evento relacionados (one-to-many)
- repertorios: Lista de Repertorio relacionados (one-to-many)
"""

FIND_SUMMARY = "Busca un registro en la tabla usuario"

FIND_DESCRIPTION = """
## Resumen
Obtiene un Usuario específico por su clave primaria.

Este endpoint permite recuperar un registro individual de Usuario
utilizando su identificador único (clave primaria). Opcionalmente puede
incluir datos de relaciones asociadas.

## Resultado
Si la consulta es exitosa, en `APIResponse.data`, retorna un objeto que representa un registro de la tabla `usuario` que incluye todos sus atributos

Si no se encuentra el registro, devuelve un error 404 `RECORD_NOT_FOUND`.

## Datos
Para cada registro en `data` se incluye:
- **id** (int): Campo id de la tabla usuario
- **nombre** (str): Nombre visible
- **apellido** (str): Apellido visible
- **email** (str): Campo email de la tabla usuario
- **created_at** (datetime): Fecha y hora de creación del registro en Usuario
- **created_by** (str): Usuario que creó el registro en Usuario
- **updated_at** (datetime): Fecha y hora de la última actualización del registro en Usuario
- **updated_by** (str): Usuario que realizó la última actualización del registro en Usuario

## Parámetros de Identificación

- **id**: id del Usuario a buscar (tipo: int)

## Consulta combinada (RECOMENDADO)
⚠️ **IMPORTANTE**: Usa siempre el parámetro `includes` para cargar relaciones en una sola consulta y evitar múltiples llamadas al API.

El parametro `includes` permite cargar relaciones asociadas a los registros.

### Relaciones disponibles (usar con parámetro 'includes'):
- proyectos: Lista de Proyecto relacionados (one-to-many)
    Proyectos del usuario.
- eventos: Lista de Evento relacionados (one-to-many)
    Eventos del musico
- repertorios: Lista de Repertorio relacionados (one-to-many)
    Repertorios del usuario

### Uso del parámetro 'includes':
Para cargar relaciones específicas, usa el parámetro 'includes' en la consulta:

### Ejemplos básicos:
#### Solo datos básicos
`usuario = GET /usuario/{id:int}`

#### Incluir proyectos
`usuario = GET /usuario/{id:int}?includes=proyectos`

#### Incluir eventos
`usuario = GET /usuario/{id:int}?includes=eventos`

#### Incluir repertorios
`usuario = GET /usuario/{id:int}?includes=repertorios`

#### Múltiples relaciones en una sola consulta
`usuario = GET /usuario/{id:int}?includes=proyectos&includes=eventos`

#### Relaciones anidadas
Puedes incluir los datos de proyectos y además incluir sus propias relaciones  
`usuario = GET /usuario/{id:int}?includes=proyectos.{nested_relation}`
Puedes incluir los datos de eventos y además incluir sus propias relaciones  
`usuario = GET /usuario/{id:int}?includes=eventos.{nested_relation}`
Puedes incluir los datos de repertorios y además incluir sus propias relaciones  
`usuario = GET /usuario/{id:int}?includes=repertorios.{nested_relation}`
"""

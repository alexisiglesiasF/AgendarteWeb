DELETE_RESPONSES = {
    200: {
        "description": "Gasto eliminado exitosamente",
        "content": {
            "application/json": {
                "example": {
                    "status": "success",
                    "data": 1,
                    "message": "Gasto eliminado exitosamente",
                    "errors": None,
                    "meta": None
                }
            }
        }
    },
    404: {
        "description": "Gasto no encontrado",
        "content": {
            "application/json": {
                "example": {
                    "status": "error",
                    "data": None,
                    "message": "Gasto no encontrado",
                    "errors": [
                        {
                            "code": "RECORD_NOT_FOUND",
                            "message": "Gasto no encontrado",
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

DELETE_SUMMARY = "Elimina un registro en la tabla gasto"

DELETE_MANY_RESPONSES = {
    200: {
        "description": "Gastos eliminados exitosamente",
        "content": {
            "application/json": {
                "example": {
                    "status": "success",
                    "data": 5,
                    "message": "5 Gastos eliminados exitosamente",
                    "errors": None,
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

DELETE_MANY_SUMMARY = "Elimina múltiples registros en la tabla gasto según filtros"
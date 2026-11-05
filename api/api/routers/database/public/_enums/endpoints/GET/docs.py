ESTADO_RESPONSES = {
    200: {
        "description": "Valores de la enumeración estado obtenidos exitosamente",
        "content": {
            "application/json": {
                "example": {
                    "status": "success",
                    "data": ["realizado", "pendiente"],
                    "message": "Enumeración estado obtenida exitosamente",
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
TIPO_EVENTO_RESPONSES = {
    200: {
        "description": "Valores de la enumeración tipo_evento obtenidos exitosamente",
        "content": {
            "application/json": {
                "example": {
                    "status": "success",
                    "data": ["show", "ensayo", "grabacion", "otros"],
                    "message": "Enumeración tipo_evento obtenida exitosamente",
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

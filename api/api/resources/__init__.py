"""
Sistema de respuestas estandarizadas para tai-api.

Este módulo proporciona clases para manejar respuestas exitosas y de error
de manera consistente en toda la API.

`tai-api init` lo copia al proyecto una vez y a partir de ahí es del proyecto: ninguna versión
nueva lo reescribe. `RESOURCES_REVISION` dice de qué revisión es la copia, y `tai-api generate`
avisa cuando la del paquete es más nueva, con lo que ha cambiado.
"""

#: La revisión de estos ficheros. Súbela al cambiarlos, y añade qué cambió en
#: `tai_api/resources_revision.py`.
RESOURCES_REVISION = 2

# Importar excepciones y manejadores
from .exceptions import (
    ErrorCode,
    APIException,
    ValidationException,
    RecordNotFoundException,
    DatabaseException,
    DuplicateRecordException,
    ForeignKeyViolationException,
    BusinessRuleViolationException,
    InvalidCredentialsException,
    InvalidTokenException,
    TokenExpiredException,
    SessionInvalidatedException,
    SessionExpiredException,
    ConcurrentSessionDetectedException,
    UnAuthorizedException
)
from .responses import (
    APIResponse,
    APIError,
    PaginationMeta,
    ResponseStatus,
    PaginatedResponse
)

from .handlers import setup_exception_handlers

from .mcp import set_mcp

__all__ = [
    "RESOURCES_REVISION",

    # Clases de respuesta
    "ResponseStatus",
    "APIError",
    "PaginationMeta",
    "APIResponse",
    "PaginatedResponse",

    # Excepciones
    "APIException",
    "ErrorCode", 
    "ValidationException", 
    "RecordNotFoundException",
    "DatabaseException",
    "DuplicateRecordException",
    "ForeignKeyViolationException",
    "BusinessRuleViolationException",
    "InvalidCredentialsException",
    "InvalidTokenException",
    "TokenExpiredException", 
    "SessionInvalidatedException",
    "SessionExpiredException",
    "ConcurrentSessionDetectedException",
    "UnAuthorizedException",

    # Manejadores
    "setup_exception_handlers",
    
    # MCP
    "set_mcp"
]

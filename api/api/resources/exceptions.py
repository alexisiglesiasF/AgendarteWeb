"""
Excepciones personalizadas para tai-api.

Este módulo define excepciones específicas que se pueden lanzar en los endpoints
y que serán manejadas por el sistema de respuestas.
"""

from typing import Any, Optional, Dict
from enum import Enum

class ErrorCode(str, Enum):
    """Códigos de error estandardizados."""
    # Errores de validación
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    
    # Errores de base de datos
    DATABASE_ERROR = "DATABASE_ERROR"
    RECORD_NOT_FOUND = "RECORD_NOT_FOUND"
    DUPLICATE_RECORD = "DUPLICATE_RECORD"
    FOREIGN_KEY_VIOLATION = "FOREIGN_KEY_VIOLATION"
    
    # Errores de autenticación y autorización
    UNAUTHORIZED_ACCESS = "UNAUTHORIZED_ACCESS"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    INVALID_TOKEN = "INVALID_TOKEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    
    # Errores específicos de sesiones
    SESSION_INVALIDATED = "SESSION_INVALIDATED"
    SESSION_EXPIRED = "SESSION_EXPIRED"
    CONCURRENT_SESSION_DETECTED = "CONCURRENT_SESSION_DETECTED"
    
    # Errores de negocio
    BUSINESS_RULE_VIOLATION = "BUSINESS_RULE_VIOLATION"
    
    # Errores del sistema
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"

    @classmethod
    def from_http_code(cls, http_code: int) -> 'ErrorCode':
        """Mapeo de códigos HTTP a códigos de error."""
        mapping = {
            400: cls.INVALID_INPUT,
            401: cls.UNAUTHORIZED_ACCESS,
            403: cls.INSUFFICIENT_PERMISSIONS,
            404: cls.RECORD_NOT_FOUND,
            409: cls.DUPLICATE_RECORD,
            422: cls.VALIDATION_ERROR,
            500: cls.INTERNAL_SERVER_ERROR,
            503: cls.SERVICE_UNAVAILABLE,
            504: cls.TIMEOUT_ERROR,
        }
        return mapping.get(http_code, cls.INTERNAL_SERVER_ERROR)


class APIException(Exception):
    """Excepción base para API"""
    
    def __init__(
        self, 
        message: str, 
        error_code: ErrorCode = ErrorCode.INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
        field: Optional[str] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details
        self.field = field
        super().__init__(message)

class ValidationException(APIException):
    """Excepción para errores de validación."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            field=field
        )

class UnAuthorizedException(APIException):
    """
    Con un token válido, sin el permiso que pide el endpoint: un 403 `INSUFFICIENT_PERMISSIONS`.

    El nombre es histórico —un 401 es no estar autenticado, y eso es `UNAUTHORIZED_ACCESS`— y se
    conserva porque lo importan los endpoints generados.
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.INSUFFICIENT_PERMISSIONS,
            details=details
        )

class RecordNotFoundException(APIException):
    """Excepción para cuando no se encuentra un registro."""
    
    def __init__(self, resource: str = "Registro"):
        super().__init__(
            message=f"{resource} no encontrado",
            error_code=ErrorCode.RECORD_NOT_FOUND
        )

class DatabaseException(APIException):
    """Excepción para errores de base de datos."""
    
    def __init__(self, message: str = "Error en la base de datos"):
        super().__init__(
            message=message,
            error_code=ErrorCode.DATABASE_ERROR
        )

class DuplicateRecordException(APIException):
    """Excepción para registros duplicados."""
    
    def __init__(self, message: str = "El registro ya existe"):
        super().__init__(
            message=message,
            error_code=ErrorCode.DUPLICATE_RECORD
        )

class ForeignKeyViolationException(APIException):
    """Excepción para violaciones de clave foránea."""
    
    def __init__(self, message: str = "Violación de clave foránea"):
        super().__init__(
            message=message,
            error_code=ErrorCode.FOREIGN_KEY_VIOLATION
        )

class BusinessRuleViolationException(APIException):
    """Excepción para violaciones de reglas de negocio."""
    
    def __init__(self, message: str):
        super().__init__(
            message=message,
            error_code=ErrorCode.BUSINESS_RULE_VIOLATION
        )

class InvalidCredentialsException(APIException):
    """Excepción para credenciales inválidas durante el login."""
    
    def __init__(self, message: str = "Credenciales inválidas"):
        super().__init__(
            message=message,
            error_code=ErrorCode.INVALID_CREDENTIALS,
            details={
                "field": "credentials",
                "user_friendly_message": "El usuario o contraseña son incorrectos. Por favor, verifica tus datos e intenta nuevamente."
            }
        )

class InvalidTokenException(APIException):
    """Excepción para tokens inválidos."""
    
    def __init__(self, message: str = "Token inválido"):
        super().__init__(
            message=message,
            error_code=ErrorCode.INVALID_TOKEN
        )

class TokenExpiredException(APIException):
    """Excepción para tokens expirados."""
    
    def __init__(self, message: str = "Token expirado"):
        super().__init__(
            message=message,
            error_code=ErrorCode.TOKEN_EXPIRED
        )

class SessionInvalidatedException(APIException):
    """
    La sesión se cerró antes de tiempo, y `details.reason` dice por qué:

    - `concurrent_login`: otro inicio de sesión con la misma cuenta la reemplazó (una sesión por
      usuario).
    - `refresh_reused`: se presentó un refresh token que ya se había usado, y se revocó la sesión
      por seguridad.

    El cliente TypeScript lee `reason` para decirle al usuario qué ha pasado.
    """

    _USER_MESSAGES = {
        "concurrent_login": "Alguien más se ha conectado con tus credenciales, por lo que tu sesión ha sido cerrada por seguridad.",
        "refresh_reused": "Tu sesión se ha cerrado por seguridad. Vuelve a iniciar sesión.",
    }

    def __init__(
        self,
        message: str = "Tu sesión ha sido invalidada por un nuevo inicio de sesión",
        reason: str = "concurrent_login",
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.SESSION_INVALIDATED,
            details={
                "reason": reason,
                "action_required": "login_again",
                "user_friendly_message": self._USER_MESSAGES.get(reason, "Tu sesión se ha cerrado. Vuelve a iniciar sesión."),
            }
        )

class SessionExpiredException(APIException):
    """Excepción para sesiones expiradas."""
    
    def __init__(self, message: str = "Tu sesión ha expirado"):
        super().__init__(
            message=message,
            error_code=ErrorCode.SESSION_EXPIRED,
            details={
                "reason": "session_timeout",
                "action_required": "login_again",
                "user_friendly_message": "Tu sesión ha expirado por inactividad. Por favor, inicia sesión nuevamente."
            }
        )

class ConcurrentSessionDetectedException(APIException):
    """
    Reservada: tai-api no la lanza. Con una sesión por usuario, un login nuevo reemplaza al
    anterior (`SessionInvalidatedException` con `reason: "concurrent_login"`) en vez de
    preguntar. Queda para un endpoint propio que quiera confirmar antes de reemplazar.
    """
    
    def __init__(self, message: str = "Ya tienes una sesión activa"):
        super().__init__(
            message=message,
            error_code=ErrorCode.CONCURRENT_SESSION_DETECTED,
            details={
                "reason": "active_session_exists",
                "action_required": "confirm_new_login",
                "user_friendly_message": "Ya tienes una sesión activa. ¿Deseas cerrarla e iniciar una nueva?"
            }
        )
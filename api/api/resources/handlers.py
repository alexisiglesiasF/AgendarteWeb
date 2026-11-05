"""
Manejadores de excepciones para tai-api.

Convierten cualquier excepción en una respuesta con la forma de siempre (`APIResponse` con
`status: "error"`) y el código HTTP que corresponde. Es lo que permite que un cliente —el
TypeScript que genera tai-api, o cualquier otro— trate todos los errores igual: mira
`errors[].code`, nunca el texto.

Tres reglas que se cumplen en todos:

- **Nada de lo que envió el usuario se repite en la respuesta ni en el log** cuando va en el
  cuerpo: una contraseña con un formato inválido acababa en el log de la aplicación y de vuelta
  en el JSON. De los parámetros de consulta y de ruta sí, que es lo que ayuda a depurar un filtro.
- **El detalle de un fallo del servidor va al log, no a la respuesta.** Un 500 dice que falló;
  por qué, lo ve quien opera la API.
- **Un 4xx no es un fallo del servidor**: se registra sin traza, para que el log no se llene de
  pilas de peticiones que solo estaban mal hechas.
"""
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, NoResultFound, SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException
from tai_alphi import Alphi

from .exceptions import APIException, ErrorCode
from .responses import APIError, APIResponse

bot = Alphi()

logger = bot.get_logger(__name__)

#: El código HTTP de cada `ErrorCode`.
STATUS_BY_CODE: Dict[ErrorCode, int] = {
    ErrorCode.VALIDATION_ERROR: status.HTTP_422_UNPROCESSABLE_CONTENT,
    ErrorCode.INVALID_INPUT: status.HTTP_400_BAD_REQUEST,
    ErrorCode.MISSING_REQUIRED_FIELD: status.HTTP_400_BAD_REQUEST,
    ErrorCode.RECORD_NOT_FOUND: status.HTTP_404_NOT_FOUND,
    ErrorCode.DUPLICATE_RECORD: status.HTTP_409_CONFLICT,
    ErrorCode.FOREIGN_KEY_VIOLATION: status.HTTP_409_CONFLICT,
    ErrorCode.BUSINESS_RULE_VIOLATION: status.HTTP_422_UNPROCESSABLE_CONTENT,
    ErrorCode.UNAUTHORIZED_ACCESS: status.HTTP_401_UNAUTHORIZED,
    ErrorCode.INSUFFICIENT_PERMISSIONS: status.HTTP_403_FORBIDDEN,
    ErrorCode.INVALID_CREDENTIALS: status.HTTP_401_UNAUTHORIZED,
    ErrorCode.INVALID_TOKEN: status.HTTP_401_UNAUTHORIZED,
    ErrorCode.TOKEN_EXPIRED: status.HTTP_401_UNAUTHORIZED,
    ErrorCode.SESSION_INVALIDATED: status.HTTP_401_UNAUTHORIZED,
    ErrorCode.SESSION_EXPIRED: status.HTTP_401_UNAUTHORIZED,
    ErrorCode.CONCURRENT_SESSION_DETECTED: status.HTTP_409_CONFLICT,
    ErrorCode.DATABASE_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
    ErrorCode.INTERNAL_SERVER_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
    ErrorCode.SERVICE_UNAVAILABLE: status.HTTP_503_SERVICE_UNAVAILABLE,
    ErrorCode.TIMEOUT_ERROR: status.HTTP_504_GATEWAY_TIMEOUT,
}


def _response(status_code: int, errors, message: Optional[str] = None, headers=None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=APIResponse.error(errors, message=message).model_dump(),
        headers=headers,
    )


# ─────────────────────────────────────────────────────────────────────────────
#  Las excepciones de la API
# ─────────────────────────────────────────────────────────────────────────────

async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """
    Las excepciones de tai-api (`APIException` y sus subclases), con su código y sus detalles.

    Antes había además un manejador para `UnAuthorizedException` y otro para
    `InvalidTokenException` que perdían por el camino `field` y `details`: este ya sabe el código
    HTTP de cada una.
    """
    status_code = STATUS_BY_CODE.get(exc.error_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    if status_code >= 500:
        logger.error(f"{exc.error_code.value}: {exc.message}", exc_info=exc)
    else:
        logger.info(f"{exc.error_code.value} ({status_code}) en {request.method} {request.url.path}: {exc.message}")

    return _response(
        status_code,
        APIError(code=exc.error_code, message=exc.message, details=exc.details, field=exc.field),
    )


async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """
    Un trigger del schema que detuvo la operación con `t.abort(mensaje)`: una regla de negocio.

    tai-sql (0.7.12 en adelante) lanza `TriggerAborted`, un `ValueError` con la marca
    `tai_trigger_abort` y el mensaje del trigger en `message`. Se reconoce por la marca y no por la
    clase porque cada schema tiene la suya. Cualquier otro `ValueError` es un fallo del servidor.
    """
    if getattr(exc, "tai_trigger_abort", False):
        mensaje = getattr(exc, "message", None) or str(exc)
        logger.info(f"Regla de negocio en {request.method} {request.url.path}: {mensaje}")
        return _response(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            APIError(
                code=ErrorCode.BUSINESS_RULE_VIOLATION,
                message=mensaje,
                details={"user_friendly_message": mensaje},
            ),
            message=mensaje,
        )
    return await general_exception_handler(request, exc)


# ─────────────────────────────────────────────────────────────────────────────
#  La base de datos
# ─────────────────────────────────────────────────────────────────────────────

#: SQLSTATE → cómo se cuenta. Son los estándar, y los usan PostgreSQL y SQL Server; MySQL los
#: traduce desde su número de error (`_MYSQL_ERRNO`).
_SQLSTATE = {
    "23505": (ErrorCode.DUPLICATE_RECORD, status.HTTP_409_CONFLICT, "El registro ya existe"),
    "23503": (ErrorCode.FOREIGN_KEY_VIOLATION, status.HTTP_409_CONFLICT,
              "El registro apunta a otro que no existe, o hay otros que dependen de él"),
    "23502": (ErrorCode.VALIDATION_ERROR, status.HTTP_422_UNPROCESSABLE_CONTENT, "Falta un campo obligatorio"),
    "23514": (ErrorCode.VALIDATION_ERROR, status.HTTP_422_UNPROCESSABLE_CONTENT,
              "El valor no cumple una restricción de la tabla"),
}
_MYSQL_ERRNO = {1062: "23505", 1451: "23503", 1452: "23503", 1048: "23502", 1364: "23502", 3819: "23514"}


def _origins(exc: IntegrityError):
    """La excepción del driver, y la que envuelve (asyncpg llega envuelta en el adaptador de SQLAlchemy)."""
    orig = getattr(exc, "orig", None)
    return [o for o in (orig, getattr(orig, "__cause__", None)) if o is not None]


def _sqlstate(exc: IntegrityError) -> Optional[str]:
    for origen in _origins(exc):
        codigo = getattr(origen, "sqlstate", None) or getattr(origen, "pgcode", None)
        if codigo:
            return str(codigo)
        args = getattr(origen, "args", ())
        if args and isinstance(args[0], int) and args[0] in _MYSQL_ERRNO:
            return _MYSQL_ERRNO[args[0]]
    return None


def _diagnostic(exc: IntegrityError, attribute: str) -> Optional[str]:
    """Un dato del diagnóstico del motor —la constraint, la columna—, venga del driver que venga."""
    for origen in _origins(exc):
        valor = getattr(origen, attribute, None) or getattr(getattr(origen, "diag", None), attribute, None)
        if valor:
            return str(valor)
    return None


def _sqlstate_from_text(exc: IntegrityError) -> Optional[str]:
    """Para el driver que no da SQLSTATE: por el texto del mensaje, como último recurso."""
    texto = str(getattr(exc, "orig", exc)).lower()
    if "unique" in texto or "duplicate" in texto:
        return "23505"
    if "foreign key" in texto:
        return "23503"
    if "not null" in texto or "cannot be null" in texto:
        return "23502"
    return None


async def sqlalchemy_integrity_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """
    Una restricción de la base de datos: unicidad, clave foránea, obligatoriedad o `CHECK`.

    Se clasifica por el SQLSTATE y no por el texto, que cambia con el motor y el idioma del
    servidor: un duplicado de MySQL («Duplicate entry») salía como un 500. Y un `NOT NULL` es un
    campo que falta —un 422 con `field`, que un formulario sabe dónde poner—, no un fallo del
    servidor. `details.constraint` dice qué restricción fue, cuando el motor lo sabe.
    """
    logger.info(f"Integrity error en {request.method} {request.url.path}: {getattr(exc, 'orig', exc)}")

    estado = _sqlstate(exc) or _sqlstate_from_text(exc)
    if estado not in _SQLSTATE:
        logger.error("Integrity error sin clasificar", exc_info=exc)
        return _response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            APIError(code=ErrorCode.DATABASE_ERROR, message="Error de integridad en la base de datos"),
        )

    codigo, status_code, mensaje = _SQLSTATE[estado]
    detalles: Dict[str, Any] = {}
    restriccion = _diagnostic(exc, "constraint_name")
    if restriccion:
        detalles["constraint"] = restriccion
    columna = _diagnostic(exc, "column_name") if estado == "23502" else None
    return _response(
        status_code,
        APIError(code=codigo, message=mensaje, field=columna, details=detalles or None),
    )


async def sqlalchemy_notfound_handler(request: Request, exc: NoResultFound) -> JSONResponse:
    logger.info(f"Sin resultado en {request.method} {request.url.path}")
    return _response(
        status.HTTP_404_NOT_FOUND,
        APIError(code=ErrorCode.RECORD_NOT_FOUND, message="Registro no encontrado"),
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    logger.error(f"SQLAlchemy error: {exc}", exc_info=exc)
    return _response(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        APIError(code=ErrorCode.DATABASE_ERROR, message="Error en la base de datos"),
    )


# ─────────────────────────────────────────────────────────────────────────────
#  La validación
# ─────────────────────────────────────────────────────────────────────────────

_LOCATION = {
    "body": "Cuerpo de la petición",
    "query": "Parámetro de consulta",
    "path": "Parámetro de ruta",
    "header": "Cabecera",
}


def _loggable(errors) -> list:
    """Los errores sin el valor recibido, que en el cuerpo puede ser una contraseña."""
    return [{"loc": e.get("loc"), "type": e.get("type"), "msg": e.get("msg")} for e in errors]


async def request_validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Un parámetro, un campo del cuerpo o una cabecera que no vale: un error por cada uno, con
    `field`, que es lo que un formulario necesita para ponerlo en su sitio.
    """
    errores = exc.errors()
    logger.info(f"Validación en {request.method} {request.url.path}: {_loggable(errores)}")

    salida = []
    for error in errores:
        location = error.get("loc") or ()
        origen = location[0] if location else "unknown"
        campo = ".".join(str(parte) for parte in location[1:]) if len(location) > 1 else str(origen)
        donde = _LOCATION.get(origen, "Campo")

        tipo = error.get("type", "")
        texto = error.get("msg", "Error de validación")
        if tipo == "missing":
            mensaje = f"{donde} requerido: '{campo}'"
        elif tipo == "type_error":
            mensaje = f"Tipo incorrecto en {donde.lower()}: '{campo}' - {texto}"
        elif tipo == "value_error":
            mensaje = f"Valor inválido en {donde.lower()}: '{campo}' - {texto}"
        else:
            mensaje = f"Error en {donde.lower()}: '{campo}' - {texto}"

        detalles: Dict[str, Any] = {"error_type": tipo, "location_type": origen}
        if origen in ("query", "path"):
            detalles["input"] = error.get("input")
        salida.append(APIError(code=ErrorCode.VALIDATION_ERROR, message=mensaje, field=campo, details=detalles))

    return _response(
        status.HTTP_422_UNPROCESSABLE_CONTENT,
        salida,
        message=f"Se encontraron {len(salida)} error(es) de validación",
    )


async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """
    Un modelo de Pydantic que no valida fuera de la entrada de FastAPI: al construir un DTO en un
    endpoint propio, por ejemplo.
    """
    errores = exc.errors()
    logger.info(f"Validación de Pydantic en {request.method} {request.url.path}: {_loggable(errores)}")
    salida = [
        APIError(
            code=ErrorCode.VALIDATION_ERROR,
            message=error.get("msg", "Error de validación"),
            field=".".join(str(parte) for parte in error.get("loc", ())),
            details={"error_type": error.get("type")},
        )
        for error in errores
    ]
    return _response(status.HTTP_422_UNPROCESSABLE_CONTENT, salida, message="Errores de validación")


# ─────────────────────────────────────────────────────────────────────────────
#  HTTP y lo que no se esperaba
# ─────────────────────────────────────────────────────────────────────────────

_CODE_BY_STATUS = {
    400: ErrorCode.INVALID_INPUT,
    401: ErrorCode.UNAUTHORIZED_ACCESS,
    403: ErrorCode.INSUFFICIENT_PERMISSIONS,
    404: ErrorCode.RECORD_NOT_FOUND,
    405: ErrorCode.INVALID_INPUT,
    409: ErrorCode.DUPLICATE_RECORD,
    422: ErrorCode.VALIDATION_ERROR,
    500: ErrorCode.INTERNAL_SERVER_ERROR,
    503: ErrorCode.SERVICE_UNAVAILABLE,
    504: ErrorCode.TIMEOUT_ERROR,
}


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Un `HTTPException`, de FastAPI o de Starlette.

    Se registra sobre el de **Starlette**, del que hereda el de FastAPI: una ruta que no existe
    (404) o un método que no admite (405) los lanza Starlette, y con el manejador sobre el de
    FastAPI salían como `{"detail": "Not Found"}`, fuera del formato que espera cualquier cliente.
    Las cabeceras se conservan: `WWW-Authenticate` es lo que hace que el navegador pida la
    contraseña de la documentación.
    """
    codigo = _CODE_BY_STATUS.get(exc.status_code) or (
        ErrorCode.INVALID_INPUT if exc.status_code < 500 else ErrorCode.INTERNAL_SERVER_ERROR
    )
    mensaje = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    logger.info(f"HTTP {exc.status_code} en {request.method} {request.url.path}: {mensaje}")
    return _response(
        exc.status_code,
        APIError(code=codigo, message=mensaje),
        headers=getattr(exc, "headers", None),
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Lo que no se esperaba: un 500 sin detalles, y la traza en el log."""
    logger.error(f"Unhandled exception en {request.method} {request.url.path}: {exc}", exc_info=exc)
    return _response(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        APIError(code=ErrorCode.INTERNAL_SERVER_ERROR, message="Error interno del servidor"),
        message="Ha ocurrido un error inesperado",
    )


def setup_exception_handlers(app: FastAPI):
    """
    Configura los manejadores de excepciones en la aplicación.

    El orden de registro no importa: Starlette elige, para cada excepción, el manejador de la
    clase más cercana en su herencia. Por eso `ValidationError` de Pydantic —que es un
    `ValueError`— va a su manejador y no al de las reglas de negocio.
    """
    app.add_exception_handler(APIException, api_exception_handler)
    app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(IntegrityError, sqlalchemy_integrity_handler)
    app.add_exception_handler(NoResultFound, sqlalchemy_notfound_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(ValueError, value_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

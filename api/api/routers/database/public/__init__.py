# Generado por tai-api: este directorio lo reescribe `tai-api generate`.

from fastapi import APIRouter

from .usuario import usuario_router
from .proyecto import proyecto_router
from .evento import evento_router
from .repertorio import repertorio_router
from .cancion import cancion_router
from .gasto import gasto_router
from .ingreso import ingreso_router
from ._enums import enumerations_router
from ._tx import transaction_router

#: La marca del contrato HTTP de este schema (`tai_api/contract/`): la lleva cada respuesta en
#: `X-Tai-Contract`, y el cliente TypeScript avisa si la suya es otra.
CONTRACT_HASH = "af233699f378"

public_router = APIRouter(prefix="/public")

public_router.include_router(usuario_router)
public_router.include_router(proyecto_router)
public_router.include_router(evento_router)
public_router.include_router(repertorio_router)
public_router.include_router(cancion_router)
public_router.include_router(gasto_router)
public_router.include_router(ingreso_router)
public_router.include_router(enumerations_router)
public_router.include_router(transaction_router)

# Generado por tai-api: este fichero lo reescribe `tai-api generate`.

from fastapi import APIRouter

from .public import public_router, CONTRACT_HASH as _contrato_public

#: `X-Tai-Contract`: la marca del contrato de cada schema, `public=<hash>,ventas=<hash>`.
CONTRATO = ",".join([f"public={_contrato_public}"])

database_router = APIRouter()

database_router.include_router(public_router)

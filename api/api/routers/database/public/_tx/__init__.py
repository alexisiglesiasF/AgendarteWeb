# Generado por tai-api: este directorio lo reescribe `tai-api generate`.

from fastapi import APIRouter

# `POST /public/_tx`: varias escrituras de varias tablas del schema en una sola
# transacción. El tag lleva el schema, como los de los dominios.
transaction_router = APIRouter(tags=["public.Transacciones"])

# El módulo registra su endpoint en el router al importarse, por eso va después.
from .endpoints.POST import transaction  # noqa: E402,F401
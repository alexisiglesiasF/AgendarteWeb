# Generado por tai-api: este directorio lo reescribe `tai-api generate`.

from fastapi import APIRouter

# El tag lleva el schema, como los de los dominios: con dos schemas, dos grupos
# «Enumeraciones» sin más se fundían en uno en Swagger.
enumerations_router = APIRouter(
    prefix="/enums",
    tags=["public.Enumeraciones"]
)

# Cada módulo registra su endpoint en el router al importarse, por eso van después.
from .endpoints.GET import estado  # noqa: E402,F401
from .endpoints.GET import tipo_evento  # noqa: E402,F401

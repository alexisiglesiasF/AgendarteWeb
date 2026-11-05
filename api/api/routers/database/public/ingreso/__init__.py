# Generado por tai-api: este directorio lo reescribe `tai-api generate`.

from fastapi import APIRouter

# El tag lleva el schema: Swagger agrupa por tag, y dos tablas homónimas de schemas
# distintos se mezclaban en un solo grupo. El `operation_id` ya lo llevaba.
ingreso_router = APIRouter(
    prefix="/ingreso",
    tags=["public.Ingreso"]
)

# Cada módulo registra su endpoint en el router al importarse, por eso van después.
from .endpoints.GET import find_many  # noqa: E402,F401
from .endpoints.GET import count  # noqa: E402,F401
from .endpoints.GET import exists  # noqa: E402,F401
from .endpoints.GET import sum  # noqa: E402,F401
from .endpoints.GET import mean  # noqa: E402,F401
from .endpoints.GET import max  # noqa: E402,F401
from .endpoints.GET import min  # noqa: E402,F401
from .endpoints.GET import find_by  # noqa: E402,F401
from .endpoints.GET import find  # noqa: E402,F401
from .endpoints.POST import agg  # noqa: E402,F401
from .endpoints.POST import create  # noqa: E402,F401
from .endpoints.POST import create_many  # noqa: E402,F401
from .endpoints.PATCH import update  # noqa: E402,F401
from .endpoints.PATCH import update_many  # noqa: E402,F401
from .endpoints.DELETE import delete  # noqa: E402,F401
from .endpoints.DELETE import delete_many  # noqa: E402,F401

# Generado por tai-api: este directorio lo reescribe `tai-api generate`.
"""
agendarte-api — cómo se monta la aplicación.

`create_app()` es lo único que hacen `__main__.py` y `__dev__.py`: construir la app con lo que
el proyecto tiene generado. Cada pieza vive en su módulo y aquí solo se compone:

| Pieza | Módulo | Rutas |
|---|---|---|
| Salud | `health.py` | `/health`, `/health/ready` |
| Documentación | `docs.py` | `/docs`, `/docs/diagrams/<schema>`, `/docs/swagger`, `/redoc` |
| Datos | `routers/` | `/<schema>/...`, y `routers/custom/` si existe |

Lo propio del proyecto (middlewares, eventos) va en `extensions/` —ver `extensions/README.md`—:
si existe y define `setup(app)`, se llama al final. Este paquete lo reescribe `tai-api generate`.
"""
from __future__ import annotations

import importlib

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from starlette.middleware.cors import CORSMiddleware

from api.resources import setup_exception_handlers
from ..config import ALLOWED_ORIGINS, ROOT_PATH, VERSION, lifespan
from . import docs, health

#: El nombre con el que se presenta la API en la documentación.
TITLE = "agendarte-api"


class RootPath:
    """
    El prefijo bajo el que se sirve la API (`ROOT_PATH` de `config.py`), en cada petición.

    Es lo que hacía `FastAPI(root_path=...)`, que FastAPI desaprueba desde la 0.146 para que lo ponga
    el servidor (`--root-path`). Aquí no depende de cómo se arranque —`tai-api dev`, `uvicorn` en el
    contenedor, `__main__.py`—, y `ROOT_PATH` sigue en un solo sitio. De él cuelgan la ruta de la
    cookie de sesión (`/api/auth`) y los enlaces de la documentación.
    """

    def __init__(self, app, root_path: str):
        self.app = app
        self.root_path = root_path

    async def __call__(self, scope, receive, send):
        if self.root_path and scope["type"] in ("http", "websocket"):
            scope["root_path"] = self.root_path
        await self.app(scope, receive, send)


def create_app() -> FastAPI:
    app = FastAPI(
        title=TITLE,
        version=VERSION,
        lifespan=lifespan,
        # La documentación la sirve `docs.py`, con su propia página y su protección.
        docs_url=None,
        redoc_url=None,
    )

    app.include_router(health.router)
    app.include_router(docs.router)
    from api.routers import main_router
    from api.routers.database import CONTRATO

    app.include_router(main_router)

    # `X-Tai-Contract`: la marca de cada schema de datos y, con autenticación, la de `/auth` y
    # `/rbac` (`auth=<hash>`).
    contrato = ",".join(m for m in (CONTRATO, ) if m)

    @app.middleware("http")
    async def cabeceras_de_tai(request, call_next):
        # El cliente TypeScript compara esta marca con la suya y avisa si difieren: se generó
        # contra otra versión de la API. Antes un cliente desfasado se descubría cuando algo fallaba.
        respuesta = await call_next(request)
        respuesta.headers["X-Tai-Contract"] = contrato
        return respuesta

    setup_exception_handlers(app)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        # Sin esto, un frontend en otro origen no puede leer la marca del contrato, ni saber si un `PATCH` con `Prefer: return=representation`
        # devolvió el registro.
        expose_headers=["X-Tai-Contract", "Preference-Applied"],
    )

    _openapi_with_groups(app)
    _extensions(app)
    # El último, para que quede por fuera de todo, también de lo que añada `extensions`: el resto
    # ya ve el `root_path` de la petición
    app.add_middleware(RootPath, root_path=ROOT_PATH)
    return app


def read_operations(app: FastAPI) -> list[str]:
    """
    Los `operation_id` de lectura (`find`, `find_many`) de los endpoints de datos.

    Se leen del OpenAPI y no de `app.routes`: desde FastAPI 0.137 un router incluido aparece
    ahí como un único nodo que se aplana al usarlo, y buscar `APIRoute` dejaba el MCP sin
    ninguna operación. `get_openapi` es la vía pública para recorrerlas en cualquier versión.
    """
    paths = get_openapi(title=app.title, version=app.version, routes=app.routes)["paths"]
    return sorted(
        operation["operationId"]
        for methods in paths.values()
        for operation in methods.values()
        if operation.get("operationId", "").endswith(("_find", "_find_many"))
    )


def _openapi_with_groups(app: FastAPI) -> None:
    """
    El OpenAPI de FastAPI, con los tags agrupados (`x-tagGroups`) para que el índice de `/docs`
    se lea por bloques —sistema, autenticación, un bloque por schema— en vez de una lista plana,
    y cada router de datos con el nombre de su tabla (`x-displayName`).

    Depende de si la autorización está activa: sin ella (`tai-api dev`) no lleva candados, ni
    las rutas de autenticación, ni explica cómo conseguir un token. Se guarda uno por estado, porque el interruptor se consulta
    en cada petición y no al construir la app.
    """
    built: dict = {}

    def openapi() -> dict:
        secured = docs.secured()
        if secured not in built:
            schema = get_openapi(
                title=app.title,
                version=app.version,
                description=docs.description(docs.SCHEMAS, secured),
                routes=app.routes,
            )
            if not secured:
                docs.without_auth(schema)
            docs.absolute_token_urls(schema, ROOT_PATH)
            schema["x-tagGroups"] = docs.tag_groups(schema, docs.SCHEMAS)
            schema["tags"] = docs.tag_names(schema, docs.SCHEMAS)
            built[secured] = schema
        app.openapi_schema = built[secured]
        return app.openapi_schema

    app.openapi = openapi


def _extensions(app: FastAPI) -> None:
    """Lo que el proyecto añade por su cuenta: `extensions.setup(app)`, si existe."""
    package = __name__.rsplit(".", 1)[0]
    try:
        module = importlib.import_module(f"{package}.extensions")
    except ModuleNotFoundError as error:
        if error.name != f"{package}.extensions":
            raise  # el módulo existe y falla al importar algo suyo: que se vea
        return
    setup = getattr(module, "setup", None)
    if callable(setup):
        setup(app)

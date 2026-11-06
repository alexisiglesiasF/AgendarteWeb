# Generado por tai-api: este fichero lo reescribe `tai-api generate`.
"""
La documentación de la API, para quien la consume: una web navegable construida sobre el
`openapi.json` que FastAPI ya genera.

| Ruta | Qué es |
|---|---|
| `/docs` | La referencia: cada endpoint con sus parámetros, cuerpos, respuestas y ejemplos de código, y un cliente para probarlo ([Scalar](https://scalar.com)) |
| `/docs/diagrams/<schema>` | El modelo de datos de cada schema: el diagrama ER interactivo de tai-sql, en el cuerpo de la página |
| `/docs/swagger` | El Swagger UI clásico, con el diagrama SVG de cada schema en su cabecera: se amplía al pulsarlo |
| `/redoc` | ReDoc, como antes |

Todas comparten la barra de navegación —con el logo de Triple Alpha—, la misma protección y la
misma paleta (`docs_assets/docs.css`), en claro y en oscuro. El modo se elige en Scalar, que lo
guarda en `localStorage.colorMode`, y las demás páginas lo siguen; el Swagger va siempre en claro.
Los tags del índice se agrupan por bloques (`tag_groups`): sistema, autenticación y un bloque
por schema, donde cada router se ve solo por su tabla (`tag_names`).

**Protección.** Con la autorización activa (`RBAC_ENABLED`, que `__main__.py` enciende) las
páginas piden usuario y contraseña (HTTP Basic: `admin` y `API_DOCS_PWD`). En `__dev__.py`
están abiertas. El `openapi.json` sigue público: es lo que leen los clientes generados.

**Sin autorización** (`tai-api dev`) los endpoints responden sin token, y la documentación lo
refleja (`without_auth`): el OpenAPI sale sin esquemas de seguridad ni candados, sin las rutas de
autenticación —siguen montadas, pero documentar un login que no hace falta confunde— ni los
modelos que solo usaban ellas, y la portada dice que la autorización está apagada. Los candados
los ponen las dependencias de seguridad de cada endpoint, que FastAPI publica siempre.

Las páginas cargan su JavaScript de jsdelivr, como el Swagger que trae FastAPI: el navegador de
quien consulta necesita internet. Los diagramas no: van con todo incrustado.
"""
from __future__ import annotations

import html
import json
import re
import os
import secrets
from pathlib import Path
from string import Template
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.openapi.docs import get_redoc_html
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from tai_alphi import Alphi

from api.routers.auth.utils import rbac_activo

#: Los schemas de datos generados; cada uno tiene su diagrama en `diagrams/`.
SCHEMAS: List[str] = ["public"]
#: La versión de Scalar, fija: una página que cambia sola con cada publicación no es reproducible.
SCALAR_VERSION = "1.73.0"
SWAGGER_VERSION = "5.33.0"
#: Los tags de los routers de autenticación (`routers/auth/`): su bloque del índice, y lo que no se
#: documenta con la autorización apagada.
AUTH_TAGS = ["Autenticación", "RBAC"]
DIAGRAMS = Path(__file__).resolve().parent.parent / "diagrams"
ASSETS = Path(__file__).resolve().parent / "docs_assets"
_ASSETS = {"docs.css": "text/css", "zoom.js": "text/javascript", "triplealpha.svg": "image/svg+xml"}
_ACTIVE = ' class="active"'

logger = Alphi.get_logger_by_name("tai-api")

DOCS_USERNAME = "admin"
DOCS_PASSWORD = os.getenv("API_DOCS_PWD", "admin")
_basic = HTTPBasic(auto_error=False)
_warned = False


def _guard(credentials: HTTPBasicCredentials = Depends(_basic)) -> None:
    """Con la autorización activa, las páginas piden las credenciales de la documentación."""
    global _warned
    if not rbac_activo():
        return
    if "API_DOCS_PWD" not in os.environ and not _warned:
        logger.warning("[docs] API_DOCS_PWD no está definida: la documentación se protege con admin/admin")
        _warned = True
    valid = credentials is not None and (
        secrets.compare_digest(credentials.username, DOCS_USERNAME)
        & secrets.compare_digest(credentials.password, DOCS_PASSWORD)
    )
    if not valid:
        raise HTTPException(status_code=401, detail="Credenciales requeridas", headers={"WWW-Authenticate": "Basic"})


router = APIRouter(include_in_schema=False, dependencies=[Depends(_guard)])


# ─────────────────────────────────────────────────────────────────────────────
# El OpenAPI: descripción e índice
# ─────────────────────────────────────────────────────────────────────────────

def secured() -> bool:
    """Si la API pide token ahora mismo: la autorización está activa (`RBAC_ENABLED`)."""
    return rbac_activo()


def description(schemas: List[str], secured: bool) -> str:
    """La portada de la referencia: qué es la API, cómo se entra y dónde está su modelo de datos."""
    lines = [
        "API generada con tai-api sobre los schemas de tai-sql del proyecto.",
        "",
    ]
    if secured:
        lines += [
            "**Autenticación.** Cada endpoint de datos exige un token *Bearer*: se obtiene en "
            "`POST /auth/{realm}/login` y se renueva en `POST /auth/refresh`. Lo que devuelve cada "
            "consulta depende de los permisos y las reglas de acceso a filas (RLS) del usuario.",
            "",
        ]
    else:
        lines += [
            "**Autorización desactivada** (`tai-api dev`): los endpoints responden sin token y con "
            "permisos de superusuario, y cada respuesta lo dice con la cabecera `X-Tai-Auth: off`. "
            "Para probar la API con autorización: `tai-api dev --auth`.",
            "",
        ]
    lines += [
        "**Salud.** `GET /health` responde mientras el proceso atiende; `GET /health/ready`, "
        "cuando además responden sus dependencias.",
    ]
    if schemas:
        # Sin enlaces: el modelo de datos tiene su pestaña, y el Swagger lo enseña con su imagen.
        # Una lista aquí salía repetida en el Swagger y viajaba en el openapi.json de los clientes.
        lines += ["", f"**Modelo de datos.** Schemas: {', '.join(f'`{s}`' for s in schemas)}. "
                      "Sus diagramas entidad-relación están en la pestaña «Modelo de datos»."]
    return "\n".join(lines)


def absolute_token_urls(openapi: dict, root_path: str) -> dict:
    """
    Los `tokenUrl` de los flujos OAuth2, como ruta absoluta con el `ROOT_PATH` delante.

    Las dependencias de autenticación los declaran relativos a la API (`auth/docslogin`), y así
    no los resuelve nadie bien: Swagger los combina con `servers` (`/api`), que también es
    relativo, y el navegador acaba resolviéndolos contra la página. Desde `/docs/swagger` el login
    iba a `/docs/auth/docslogin`, o a `/api/docs/auth/docslogin` detrás del proxy: un 404 en los
    dos casos. Se completan aquí y no en `dependencies.py` porque es aquí donde se conoce el
    `ROOT_PATH` de `config.py`, que no se puede importar desde las dependencias.
    """
    raíz = root_path.rstrip("/")
    for esquema in openapi.get("components", {}).get("securitySchemes", {}).values():
        for flujo in (esquema.get("flows") or {}).values():
            url = flujo.get("tokenUrl")
            if url and "://" not in url and not url.startswith("/"):
                flujo["tokenUrl"] = f"{raíz}/{url}"
    return openapi


def without_auth(openapi: dict) -> dict:
    """
    El OpenAPI para cuando la autorización está apagada: sin esquemas de seguridad ni candados
    —si no, Scalar y el Swagger piden un token que la API no pide—, sin las rutas de
    autenticación y sin los modelos que solo usaban ellas, que se quedarían sueltos en «Models».
    """
    paths = openapi.get("paths", {})
    for route in list(paths):
        operations = paths[route]
        for method in list(operations):
            operation = operations[method]
            if not isinstance(operation, dict):
                continue
            if set(operation.get("tags", [])) & set(AUTH_TAGS):
                del operations[method]
            else:
                operation.pop("security", None)
        if not any(isinstance(o, dict) for o in operations.values()):
            del paths[route]
    openapi.pop("security", None)

    components = openapi.get("components", {})
    components.pop("securitySchemes", None)
    schemas = components.get("schemas", {})
    reachable = _referenced(paths, schemas)
    for name in [n for n in schemas if n not in reachable]:
        del schemas[name]
    if "schemas" in components and not schemas:
        del components["schemas"]
    if "components" in openapi and not components:
        del openapi["components"]
    return openapi


def _referenced(paths: dict, schemas: dict) -> set:
    """Los modelos a los que se llega desde las rutas, siguiendo sus referencias."""
    pattern = re.compile(r"#/components/schemas/([^\"]+)")
    pending = set(pattern.findall(json.dumps(paths)))
    seen: set = set()
    while pending:
        name = pending.pop()
        if name in seen or name not in schemas:
            continue
        seen.add(name)
        pending |= set(pattern.findall(json.dumps(schemas[name])))
    return seen


def tag_groups(openapi: dict, schemas: List[str]) -> List[Dict[str, object]]:
    """
    Los tags del OpenAPI en bloques, para el índice de la referencia (`x-tagGroups`). Un tag
    que no encaja en ninguno —el de un router propio— va a «Otros», nunca se pierde.
    """
    tags: List[str] = []
    for operations in openapi.get("paths", {}).values():
        for operation in operations.values():
            for tag in operation.get("tags", []) if isinstance(operation, dict) else []:
                if tag not in tags:
                    tags.append(tag)

    groups: List[Dict[str, object]] = []
    taken: set = set()

    def group(name: str, members: List[str]) -> None:
        members = [t for t in members if t in tags and t not in taken]
        if members:
            groups.append({"name": name, "tags": members})
            taken.update(members)

    group("Sistema", ["Salud"])
    group("Autenticación", AUTH_TAGS)
    for schema in schemas:
        group(f"Schema · {schema}", [t for t in tags if t.startswith(f"{schema}.")])
    group("Otros", [t for t in tags if t not in taken])
    return groups


def tag_names(openapi: dict, schemas: List[str]) -> List[Dict[str, str]]:
    """
    Cómo se ve cada router de datos en el índice: por su tabla, en mayúsculas y con las
    palabras separadas (`public.ResumenAutor` → `RESUMEN AUTOR`), porque el schema ya encabeza su
    bloque. Va en `x-displayName`: el nombre del tag sigue siendo `<schema>.<Tabla>`, que es su
    identidad —dos schemas pueden tener una tabla con el mismo nombre—.
    """
    declared = {t["name"]: t for t in openapi.get("tags", [])}
    for operations in openapi.get("paths", {}).values():
        for operation in operations.values():
            for tag in operation.get("tags", []) if isinstance(operation, dict) else []:
                schema, _, table = tag.partition(".")
                if schema in schemas and table and tag not in declared:
                    words = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", table)
                    declared[tag] = {"name": tag, "x-displayName": words.upper()}
    return list(declared.values())


# ─────────────────────────────────────────────────────────────────────────────
# Las páginas
# ─────────────────────────────────────────────────────────────────────────────

#: El modo elegido en Scalar (lo guarda en `localStorage.colorMode`: `light`, `dark` o `system`),
#: para las páginas que no son Scalar. Sin elección, claro. Va al principio del <body> para que
#: no se vea un destello del otro modo.
_MODE_SCRIPT = (
    "<script>(function(){var m=null;try{m=localStorage.getItem('colorMode')}catch(e){}"
    "var dark=m==='dark'||(m==='system'&&matchMedia('(prefers-color-scheme: dark)').matches);"
    "document.body.className=dark?'dark-mode':'light-mode'})()</script>"
)

_SHELL = Template("""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>$title · $section</title>
  <link rel="stylesheet" href="$root/docs/assets/docs.css">
  $head
</head>
<body class="light-mode">
  $mode_script
  <header class="tai-bar">
    <div class="tai-brand">$title <span class="tai-version">v$version</span></div>
    <nav class="tai-nav">$nav</nav>
    <div class="tai-spacer"></div>
    <div class="tai-logo"><img src="$root/docs/assets/triplealpha.svg" alt="Triple Alpha" width="29" height="28"></div>
  </header>
  $subbar
  <div class="$main_class">$content</div>
  $scripts
</body>
</html>
""")


def _nav(root: str, active: str) -> str:
    """Pestañas, sin desplegables: un menú colgado de la barra quedaba recortado y no se veía."""
    def link(href: str, label: str, key: str) -> str:
        css = ' class="active"' if key == active else ""
        return f'<a href="{root}{href}"{css}>{html.escape(label)}</a>'

    parts = [link("/docs", "Referencia", "reference")]
    if SCHEMAS:
        parts.append(link("/docs/diagrams", "Modelo de datos", "diagrams"))
    parts.append(link("/docs/swagger", "Swagger", "swagger"))
    return "".join(parts)


def _page(
    request: Request, *, section: str, active: str, content: str,
    head: str = "", scripts: str = "", subbar: str = "", follow_mode: bool = True,
) -> HTMLResponse:
    root = request.scope.get("root_path", "")
    app = request.app
    return HTMLResponse(_SHELL.substitute(
        title=html.escape(app.title),
        version=html.escape(app.version),
        section=html.escape(section),
        nav=_nav(root, active),
        root=root,
        mode_script=_MODE_SCRIPT if follow_mode else "",
        head=head,
        subbar=subbar,
        main_class="tai-main tai-with-subbar" if subbar else "tai-main",
        content=content,
        scripts=scripts,
    ))


@router.get("/docs")
async def reference(request: Request) -> HTMLResponse:
    root = request.scope.get("root_path", "")
    config = {
        "url": f"{root}{request.app.openapi_url}",
        "layout": "modern",
        # Los colores son los de `docs.css`, que comparte la barra; sin elección guardada, claro.
        "theme": "none",
        "darkMode": False,
        "defaultOpenAllTags": False,
        "hideDownloadButton": False,
        "metaData": {"title": request.app.title},
        # La barra de navegación de estas páginas va encima: Scalar le deja su sitio.
        "customCss": ":root { --scalar-custom-header-height: 56px; }",
        # Nada sale de aquí hacia Scalar: sin telemetría (viene activada), sin su asistente de
        # IA, que manda el documento a su servicio, y sin sus herramientas de desarrollo.
        "telemetry": False,
        "agent": {"disabled": True},
        "showDeveloperTools": "never",
        "mcp": {"disabled": True},
    }
    scripts = (
        f'<script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference@{SCALAR_VERSION}"></script>'
        f"<script>Scalar.createApiReference('#reference', {json.dumps(config)});</script>"
    )
    return _page(request, section="Referencia", active="reference", content='<div id="reference"></div>', scripts=scripts)


@router.get("/docs/diagrams")
async def diagrams(request: Request) -> RedirectResponse:
    """El modelo de datos: el primer schema, y los demás en la sub-barra."""
    if not SCHEMAS:
        raise HTTPException(status_code=404, detail="Esta API no tiene schemas de datos")
    return RedirectResponse(f"{request.scope.get('root_path', '')}/docs/diagrams/{SCHEMAS[0]}")


@router.get("/docs/diagrams/{schema}")
async def diagram(schema: str, request: Request) -> HTMLResponse:
    """El diagrama interactivo de un schema, en el cuerpo de la página."""
    _diagram_file(schema)
    root = request.scope.get("root_path", "")
    subbar = ""
    if len(SCHEMAS) > 1:
        tabs = "".join(
            f'<a href="{root}/docs/diagrams/{s}"{_ACTIVE if s == schema else ""}>{html.escape(s)}</a>'
            for s in SCHEMAS
        )
        subbar = f'<div class="tai-subbar"><span>Schema</span>{tabs}</div>'
    frame = (
        f'<iframe class="tai-frame" title="Diagrama ER de {html.escape(schema)}" '
        f'src="{root}/docs/diagrams/{schema}/file"></iframe>'
    )
    # El diagrama interactivo de tai-sql tiene su propio tema: se le da el de la documentación al
    # cargar, para que no quede en claro bajo una barra oscura. Con su `applyTheme()`, que además
    # repinta el grafo; solo el atributo `data-theme` dejaba las etiquetas con los colores de antes.
    scripts = (
        "<script>document.querySelector('.tai-frame').addEventListener('load',function(e){"
        "var t=document.body.classList.contains('dark-mode')?'dark':'light',w=e.target.contentWindow;"
        "try{if(typeof w.applyTheme==='function'){w.applyTheme(t)}"
        "else{w.document.documentElement.dataset.theme=t}}catch(_){}})</script>"
    )
    return _page(
        request, section=f"Modelo de datos · {schema}", active="diagrams", content=frame,
        subbar=subbar, scripts=scripts,
    )


@router.get("/docs/diagrams/{schema}/file")
async def diagram_file(schema: str) -> FileResponse:
    return FileResponse(_diagram_file(schema))


@router.get("/docs/diagrams/{schema}/svg")
async def diagram_svg(schema: str) -> FileResponse:
    """El diagrama como imagen: el que enseña el Swagger y se amplía en su visor."""
    path = _svg(schema)
    if path is None:
        raise HTTPException(status_code=404, detail=f"No hay diagrama SVG del schema '{schema}'")
    return FileResponse(path, media_type="image/svg+xml")


@router.get("/docs/assets/{name}")
async def asset(name: str) -> FileResponse:
    """El estilo de estas páginas y el visor de diagramas del Swagger."""
    if name not in _ASSETS:
        raise HTTPException(status_code=404, detail="No existe")
    return FileResponse(ASSETS / name, media_type=_ASSETS[name])


@router.get("/docs/swagger")
async def swagger(request: Request) -> HTMLResponse:
    """
    El Swagger UI, con el modelo de datos en su cabecera: el SVG de cada schema, que se amplía
    al pulsarlo. Se añade en la página y no en el `openapi.json`, que es de los clientes.
    """
    root = request.scope.get("root_path", "")
    config = {
        "url": f"{root}{request.app.openapi_url}",
        "dom_id": "#swagger-ui",
        "layout": "BaseLayout",
        "deepLinking": True,
        "persistAuthorization": True,
        "showExtensions": True,
        "showCommonExtensions": True,
    }
    diagrams = [
        {
            "schema": schema,
            "svg": f"{root}/docs/diagrams/{schema}/svg" if _svg(schema) else None,
            "page": f"{root}/docs/diagrams/{schema}",
        }
        for schema in SCHEMAS
    ]
    cdn = f"https://cdn.jsdelivr.net/npm/swagger-ui-dist@{SWAGGER_VERSION}"
    head = f'<link rel="stylesheet" href="{cdn}/swagger-ui.css">'
    scripts = (
        f'<script src="{cdn}/swagger-ui-bundle.js"></script>'
        f'<script src="{root}/docs/assets/zoom.js"></script>'
        "<script>"
        f"const config = {json.dumps(config)};"
        "config.presets = [SwaggerUIBundle.presets.apis];"
        f"config.onComplete = () => taiDocs.injectDiagrams({json.dumps(diagrams)});"
        "window.ui = SwaggerUIBundle(config);"
        "</script>"
    )
    # Siempre en claro: el Swagger UI no tiene modo oscuro propio, y el de la paleta lo dejaba
    # con el texto oscuro sobre el fondo oscuro.
    return _page(
        request, section="Swagger", active="swagger", content='<div id="swagger-ui"></div>',
        head=head, scripts=scripts, follow_mode=False,
    )


@router.get("/redoc")
async def redoc(request: Request) -> HTMLResponse:
    root = request.scope.get("root_path", "")
    return get_redoc_html(openapi_url=f"{root}{request.app.openapi_url}", title=f"{request.app.title} · ReDoc")


def _svg(schema: str) -> Optional[Path]:
    """El SVG de un schema generado, si se generó (hace falta Graphviz al generar)."""
    path = DIAGRAMS / f"{schema}.svg"
    return path if schema in SCHEMAS and path.is_file() else None


def _diagram_file(schema: str) -> Path:
    """El diagrama de un schema generado: el interactivo si lo hay, si no la imagen."""
    if schema in SCHEMAS:
        for suffix in (".html", ".svg"):
            path = DIAGRAMS / f"{schema}{suffix}"
            if path.is_file():
                return path
    raise HTTPException(status_code=404, detail=f"No hay diagrama del schema '{schema}'")

# Generado por tai-api: este fichero lo reescribe `tai-api generate`.
"""
La salud del servicio, en dos preguntas distintas:

- **`GET /health` — ¿el proceso responde?** (liveness). No mira nada más: si respondiera según
  la base de datos, un corte de la base de datos haría que el orquestador reiniciara un
  contenedor sano. Es el que usa el `HEALTHCHECK` del dockerfile. Siempre 200.
- **`GET /health/ready` — ¿puede atender peticiones?** (readiness). Comprueba cada dependencia
  —la base de datos de cada schema— con un
  tiempo máximo, y responde 503 si alguna falla. Es el que debe usar un balanceador.

Una comprobación que falla dice qué ha fallado y cuánto ha tardado, pero no por qué: el motivo
(una URL, un usuario) va al log, no a una respuesta que puede leer cualquiera.
"""
from __future__ import annotations

import asyncio
import importlib
import time
from datetime import datetime, timezone
from typing import Awaitable, Callable, Dict, Literal, Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from tai_alphi import Alphi

from ..config import VERSION

logger = Alphi.get_logger_by_name("tai-api")

router = APIRouter(prefix="/health", tags=["Salud"])

#: El nombre del servicio, como se presenta en la documentación.
SERVICE = "agendarte-api"
#: Lo que puede tardar cada comprobación antes de darse por fallida, en segundos.
TIMEOUT = 3.0
_STARTED = time.monotonic()


class Liveness(BaseModel):
    """El proceso responde."""

    status: Literal["ok"] = "ok"
    service: str = Field(description="Nombre del servicio")
    version: str = Field(description="Versión desplegada")
    uptime_seconds: float = Field(description="Segundos desde que arrancó el proceso")
    timestamp: datetime = Field(description="Hora del servidor, en UTC")


class Check(BaseModel):
    """El resultado de comprobar una dependencia."""

    status: Literal["ok", "error"]
    latency_ms: float = Field(description="Lo que ha tardado la comprobación")
    error: Optional[str] = Field(default=None, description="Qué ha fallado (el detalle, en el log)")


class Readiness(Liveness):
    """El servicio puede atender peticiones: todas sus dependencias responden."""

    status: Literal["ok", "error"] = "ok"
    checks: Dict[str, Check] = Field(description="Una entrada por dependencia")


def _liveness() -> dict:
    return {
        "service": SERVICE,
        "version": VERSION,
        "uptime_seconds": round(time.monotonic() - _STARTED, 3),
        "timestamp": datetime.now(timezone.utc),
    }


@router.get("", response_model=Liveness, summary="El proceso responde")
async def liveness() -> Liveness:
    """Siempre 200 mientras el proceso atienda. No comprueba dependencias: para eso, `/health/ready`."""
    return Liveness(**_liveness())


@router.get(
    "/ready",
    response_model=Readiness,
    summary="Las dependencias responden",
    responses={503: {"model": Readiness, "description": "Alguna dependencia no responde"}},
)
async def readiness():
    """Comprueba cada dependencia en paralelo. 200 si todas responden; 503 si alguna no."""
    names = list(CHECKS)
    results = await asyncio.gather(*(_run(name, CHECKS[name]) for name in names))
    checks = dict(zip(names, results))
    body = Readiness(
        **_liveness(),
        status="ok" if all(c.status == "ok" for c in checks.values()) else "error",
        checks=checks,
    )
    return JSONResponse(body.model_dump(mode="json"), status_code=200 if body.status == "ok" else 503)


async def _run(name: str, check: Callable[[], Awaitable[None]]) -> Check:
    start = time.perf_counter()
    try:
        await asyncio.wait_for(check(), timeout=TIMEOUT)
        return Check(status="ok", latency_ms=_since(start))
    except asyncio.TimeoutError:
        logger.warning(f"[health] {name}: sin respuesta en {TIMEOUT} s")
        return Check(status="error", latency_ms=_since(start), error=f"sin respuesta en {TIMEOUT} s")
    except Exception as exc:  # noqa: BLE001 - cualquier fallo de la dependencia es «no responde»
        logger.warning(f"[health] {name}: {type(exc).__name__}: {exc}")
        return Check(status="error", latency_ms=_since(start), error=type(exc).__name__)


def _since(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 2)


# ─────────────────────────────────────────────────────────────────────────────
# Las comprobaciones
# ─────────────────────────────────────────────────────────────────────────────

def _database(schema: str) -> Callable[[], Awaitable[None]]:
    """Un `SELECT 1` por el motor del cliente del schema: el mismo pool que usan los endpoints."""

    async def check() -> None:
        from sqlalchemy import text

        module = importlib.import_module(f"api.database.{schema}")
        async with module.async_session_manager.engine.connect() as connection:
            await connection.execute(text("SELECT 1"))

    return check


#: Las dependencias del servicio, por nombre. Un endpoint propio puede añadir la suya desde
#: `extensions.setup()`: `health.CHECKS["redis"] = mi_comprobacion`.
CHECKS: Dict[str, Callable[[], Awaitable[None]]] = {
    "database.public": _database("public"),
}

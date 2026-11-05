from contextlib import asynccontextmanager
from fastapi import FastAPI

VERSION = "0.1.0"
ROOT_PATH = ""
ALLOWED_ORIGINS = ["*"]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código de inicialización (si es necesario)
    yield
    # Código de limpieza (si es necesario)
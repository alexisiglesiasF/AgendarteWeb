# Generado por tai-api: este fichero lo reescribe `tai-api generate`.
"""
agendarte-api — punto de entrada de producción (`uvicorn <paquete>.__main__:app`).

Solo construye la app: cómo se monta está en `app/`, y lo propio del proyecto va en
`extensions/`, que `create_app()` carga si existe. Este fichero lo reescribe `tai-api generate`.
"""
import os

# Antes de construir la app. Las dependencias consultan el interruptor en cada petición, así que
# el orden ya no puede dejar la API abierta; se fija aquí para que este fichero sea correcto por
# sí solo y no dependa de que la variable venga del entorno del contenedor.
os.environ["RBAC_ENABLED"] = "true"

from .app import create_app

app = create_app()

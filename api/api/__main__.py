# Generado por tai-api: este fichero lo reescribe `tai-api generate`.
"""
agendarte-api — punto de entrada de producción (`uvicorn <paquete>.__main__:app`).

Solo construye la app: cómo se monta está en `app/`, y lo propio del proyecto va en
`extensions/`, que `create_app()` carga si existe. Este fichero lo reescribe `tai-api generate`.
"""
from .app import create_app

app = create_app()

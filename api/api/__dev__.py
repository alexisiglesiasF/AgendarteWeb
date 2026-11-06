# Generado por tai-api: este fichero lo reescribe `tai-api generate`.
"""
agendarte-api — punto de entrada de desarrollo (`tai-api dev`).

La misma app que `__main__.py`, con la autorización apagada. Este fichero lo reescribe
`tai-api generate`.
"""
import os
import sys

# Este entry point desactiva la autorización a propósito: es el de `tai-api dev`. Se avisa al
# arrancar porque un modo inseguro que no se nota es como se despliega por error. Para
# desarrollar CON autorización: `tai-api dev --auth`, que usa __main__.py.
os.environ["RBAC_ENABLED"] = "false"
print(
    "\n  AUTORIZACION DESACTIVADA - entry point de desarrollo.\n"
    "  Todos los endpoints responden con permisos de superusuario.\n"
    "  Para arrancar con autorizacion: tai-api dev --auth\n",
    file=sys.stderr,
)

from .app import create_app

app = create_app()

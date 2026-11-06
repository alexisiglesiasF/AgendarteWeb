
# rbac/main.py
from tai_api.rbac import source, role

source(realm_name="main", dbschemas=["public"])

role(name="main", api_permissions=["sudo", "main-admin"])
role(name="lector", api_permissions=["usuario-read", "post-read"])

"""
INSTRUCCIONES

# Definición de permisos de aplicación (custom, no vinculados a tablas)

all_permissions = app_permission(
    name="all_permissions",
    description="Permiso para realizar todas las acciones.",
)

view_data = app_permission(
    name="view_data",
    description="Permiso para visualizar los datos de las vistas.",
)

# Definición de roles (agrupan permisos de API y/o de aplicación)
# Los permisos de API se pueden referenciar:
#   1.  Usando las clases importadas de tables.
#           api_permissions=[Usuario.READ, Post.CREATE]
#   2.  Usando strings con el nombre del permiso.
#           api_permissions=['usuario-read', 'post-create']
# Los permisos de APP se pueden referenciar:
#   1.  Usando las variables definidas en este archivo:
#           app_permissions=[view_data]
#   2.  Usando strings con el nombre del permiso:
#           app_permissions=['view_data']
#
# `subroles` declara roles hijos, y un hijo HEREDA LOS PERMISOS DE SU PADRE (no al revés):
# con role("editor", subroles=["lector"]), quien tenga "lector" recibe también los de "editor".
# Pon los permisos comunes en el padre y lo específico en cada hijo.

viewer = role(
    name="viewer",
    description="Rol de lectura para vistas",
    app_permissions=[view_data],
)

reader = role(
    name="reader",
    description="Rol de lectura para vistas",
    app_permissions=['view_data'],
    subroles=[viewer],
)

# Filas de cada usuario: owner(schema, tabla, columna). Cada uno ve, cambia y borra solo las
# suyas, y no puede crear filas a nombre de otro ni cambiar de quién son. El valor es el usuario
# del token: no se asigna. Alcanza también a lo que cuelga de la tabla por relaciones
# many-to-one (con la de `chat`, sus mensajes); una vista necesita su propia regla.
# `exempt` lista los permisos que la saltan, en lectura y escritura (ninguno por defecto,
# tampoco sudo).
owner("public", "chat", "username")
owner("public", "tokens_mensaje", "username", exempt=["supervisor"])
"""
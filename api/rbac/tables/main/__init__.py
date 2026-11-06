"""
agendarte-api - RBAC Tables (main)
Generado automáticamente por tai-api

Clases de referencia para definir API permissions por tabla/vista. Las reescribe
`tai-api generate` a partir de las tablas de `source()` en rbac/main.py.
Uso en main.py:

    from rbac.tables.main import Usuario, Post

    admin = role(
        name="admin",
        api_permissions=[Usuario.READ, Usuario.UPDATE, Post.READ],
    )
"""
from tai_api.rbac import RBACPermission


class RealmResources:
    """Permisos API para todos los recursos del realm."""
    ADMIN = RBACPermission(
        name="main-admin",
        description="Administrador del realm main",
    )


class AllResources:
    """Permisos API para todos los recursos."""
    ADMIN = RBACPermission(
        name="sudo",
        description="Permiso total de superusuario",
    )
    CREATE = RBACPermission(
        name="allresources-create",
        description="Permiso total de create",
    )
    READ = RBACPermission(
        name="allresources-read",
        description="Permiso total de read",
    )
    UPDATE = RBACPermission(
        name="allresources-update",
        description="Permiso total de update",
    )
    DELETE = RBACPermission(
        name="allresources-delete",
        description="Permiso total de delete",
    )



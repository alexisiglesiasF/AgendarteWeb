"""
Schema de autenticación: realms, usuarios, roles y permisos.

Modela un control de acceso multi-realm — cada Realm agrupa sus propios
usuarios y roles, y las tablas puente UserRole/RolePermission resuelven las
relaciones muchos-a-muchos. Todas las tablas se relacionan por id, y su clave
natural (el nombre en su realm) es única. Los roles admiten anidamiento vía
`parent_id`.

Requisitos:
- Variable de entorno MAIN_DATABASE_URL con la conexión.

Uso:
tai-sql generate -s auth
"""
from __future__ import annotations
import os
from tai_sql import *
from tai_sql.generators import PythonClientGenerator, ERDiagramGenerator


# Configurar el datasource
datasource(
    provider=env('MAIN_DATABASE_URL'),
    schema='auth',
    syntax='v2',
    operative_fields=True, # Añade created_at, updated_at, created_by, updated_by a todas las tablas
)

# Configurar los generadores
generate(
    PythonClientGenerator(
        output_dir=[
            'database/database', # Directorio donde se generará el cliente python
            # Añade más directorios aquí
        ]
    ),
    ERDiagramGenerator(
        output_dir=[
            'database/diagrams', # Directorio donde se generará el diagrama
            # Añade más directorios aquí
        ],
        theme='classic',
        format='html'
    )
)

# ============================================================================
# ENUMS
# ============================================================================

class PermissionType(Enum):
    """Tipo de permiso: API (endpoints) o APP (funcionalidades de aplicación)"""
    API = 'api'
    APP = 'app'


# ============================================================================
# TABLAS
# ============================================================================
#
# Cada tabla tiene un `id` de clave primaria y un `unique` con su clave natural, y se
# relaciona con las demás por id. El de `user` es un UUID que pone la base de datos:
# viaja en el token y lo guardan otros schemas.
#
# El feed fija los ids (`id=1`) para que las filas que los referencian puedan
# escribirlos, y adelanta después las secuencias.

class Realm(Table):
    """Realm de autenticación — agrupa usuarios, roles y permisos"""
    __tablename__ = "realm"

    id: col[bigint] = column(primary_key=True, autoincrement=True)
    name: col[str] = column(unique=True, description="Nombre único del realm")
    description: col[str | None] = column(description="Descripción del realm")

    users: onetomany[User]
    roles: onetomany[Role]
    permissions: onetomany[Permission]
    rls_rules: onetomany[RowLevelSecurity]

    def feed(self) -> list:
        return [
            Realm(id=1, name="main", description="Main Realm")
        ]


class User(Table):
    """Usuario de autenticación"""
    __tablename__ = "user"
    # El nombre es único en su realm; la identidad es el `id`, que no se reutiliza.
    __constraints__ = unique_constraint("username", "realm_id")

    id: col[UUID] = column(primary_key=True, autoincrement=True, description="Identidad del usuario: la genera la base de datos y no se reutiliza")
    username: col[str] = column(description="Nombre de usuario, único en su realm")
    realm_id: col[bigint] = column(description="Realm al que pertenece el usuario")

    first_name: col[str | None] = column(description="Nombre del usuario")
    last_name: col[str | None] = column(description="Apellido del usuario")
    password: col[str] = column(hash=True, description="Contraseña hasheada: solo se puede verificar, no leer")
    email: col[str | None] = column(description="Correo electrónico")
    is_active: col[bool] = column(default=True, description="Usuario activo")
    session_id: col[str | None] = column(description="ID de sesión actual (para control de concurrencia)")
    # La rotación del refresh token (tai-api, sesión con cookie): cada refresco sube la
    # generación, y presentar uno de una generación anterior —fuera de una ventana de
    # gracia contada desde la última rotación— es que alguien tiene una copia, y cierra
    # la sesión. Opcionales y sin default, como `session_id`: un `push` las añade a una
    # base de datos existente sin tocar sus filas.
    refresh_generation: col[int | None] = column(description="Generación del refresh token vigente de la sesión")
    refresh_rotated_at: col[datetime | None] = column(description="Cuándo se rotó por última vez el refresh token")
    password_expiration: col[datetime | None] = column(description="Fecha de expiración de la contraseña")
    attributes: col[dict | None] = column(description="Atributos adicionales del usuario (JSON)")

    realm: manytoone[Realm] = relation(fields=["realm_id"], references=["id"], backref="users")

    user_roles: onetomany[UserRole]

    def feed(self) -> list:
        return [
            User(
                username="admin",
                password=os.getenv("ADMIN_PWD", "admin"),
                email="admin@localhost",
                first_name="Admin",
                last_name="User",
                is_active=True,
                realm_id=1,
                # Anidado: el `user_id` lo pone el feed con el id que genere la base
                user_roles=[UserRole(role_id=1)],
            )
        ]

    # Opcional: nombre y apellidos lo son, y sin ninguno de los dos no hay nombre
    # completo que calcular. Declarada `-> str`, la columna era NOT NULL y crear un
    # usuario sin nombre fallaba con una violación de integridad.
    @calculated_column
    def full_name(self) -> Optional[str]:
        return f"{self.first_name or ''} {self.last_name or ''}".strip() if self.first_name or self.last_name else None


class Role(Table):
    """Rol que agrupa permisos"""
    __tablename__ = "role"
    __constraints__ = unique_constraint("name", "realm_id")

    id: col[bigint] = column(primary_key=True, autoincrement=True)
    name: col[str] = column(description="Nombre del rol, único en su realm")
    realm_id: col[bigint] = column(description="Realm al que pertenece el rol")

    description: col[str | None] = column(description="Descripción del rol")
    attributes: col[dict | None] = column(description="Atributos adicionales del rol (JSON)")

    parent_id: col[bigint | None] = column(description="Rol padre, del mismo realm, para subroles (roles anidados)")

    realm: manytoone[Realm] = relation(fields=["realm_id"], references=["id"], backref="roles")
    # `restrict`: borrar un rol con subroles es un error, no una cascada que se los
    # lleve. Que el padre sea del mismo realm lo comprueba quien lo asigna (tai-api).
    # `tree=True`: la jerarquía de roles, con consultas en árbol (`find_many(tree_mode=...)`).
    parent: manytoone[Role] = relation(fields=["parent_id"], references=["id"], backref="subroles", onDelete="restrict", tree=True)

    subroles: onetomany[Role]

    role_permissions: onetomany[RolePermission]
    user_roles: onetomany[UserRole]

    def feed(self) -> list:
        return [
            Role(
                id=1,
                name="Administrador",
                description="Rol de administrador con todos los permisos",
                realm_id=1,
                attributes={ },
                # Anidado: el `role_id` lo pone el feed
                role_permissions=[
                    RolePermission(permission_id=1),  # admin-role → sudo
                    RolePermission(permission_id=2),  # admin-role → main-admin
                ],
            ),
        ]

class Permission(Table):
    """Permiso individual (API o APP)"""
    __tablename__ = "permission"
    __constraints__ = unique_constraint("name", "realm_id")

    id: col[bigint] = column(primary_key=True, autoincrement=True)
    name: col[str] = column(description="Nombre del permiso (ej: usuario-read), único en su realm")
    realm_id: col[bigint] = column(description="Realm al que pertenece el permiso")

    description: col[str | None] = column(description="Descripción del permiso")
    type: col[PermissionType] = column(description="Tipo: api o app")
    attributes: col[dict | None] = column(description="Atributos adicionales (JSON)")

    realm: manytoone[Realm] = relation(fields=["realm_id"], references=["id"], backref="permissions")

    role_permissions: onetomany[RolePermission]

    def feed(self) -> list:
        return [
            Permission(
                id=1,
                name="sudo",
                description="Permiso total de superusuario",
                type=PermissionType.API.value,
                realm_id=1,
            ),
            Permission(
                id=2,
                name="main-admin",
                description="Administrador del realm main",
                type=PermissionType.API.value,
                realm_id=1,
            ),
        ]


class UserRole(Table):
    """Relación M2M entre User y Role"""
    __tablename__ = "user_role"
    # Un usuario tiene un rol una vez. Es además la clave natural por la que
    # `tai-sql feed` reconoce la fila. Que el usuario y el rol sean del mismo realm
    # lo comprueba quien asigna (tai-api).
    __constraints__ = unique_constraint("user_id", "role_id")

    id: col[bigint] = column(primary_key=True, autoincrement=True)
    user_id: col[UUID] = column(description="Usuario")
    role_id: col[bigint] = column(description="Rol")

    user: manytoone[User] = relation(fields=["user_id"], references=["id"], backref="user_roles")
    role: manytoone[Role] = relation(fields=["role_id"], references=["id"], backref="user_roles")


class RolePermission(Table):
    """Relación M2M entre Role y Permission"""
    __tablename__ = "role_permission"
    # Un rol tiene un permiso una vez; y es la clave natural del feed, como en UserRole.
    __constraints__ = unique_constraint("role_id", "permission_id")

    id: col[bigint] = column(primary_key=True, autoincrement=True)
    role_id: col[bigint] = column(description="Rol")
    permission_id: col[bigint] = column(description="Permiso")

    role: manytoone[Role] = relation(fields=["role_id"], references=["id"], backref="role_permissions")
    permission: manytoone[Permission] = relation(fields=["permission_id"], references=["id"], backref="role_permissions")


class RowLevelSecurity(Table):
    """Definición de reglas de seguridad a nivel de fila (RLS)"""
    __tablename__ = "row_level_security"
    __constraints__ = unique_constraint("realm_id", "schema_name", "table_name", "column_name")

    id: col[bigint] = column(primary_key=True, autoincrement=True)
    realm_id: col[bigint] = column(description="Realm al que pertenece la regla RLS")
    schema_name: col[str] = column(description="Nombre del schema al que aplica la regla RLS")
    table_name: col[str] = column(description="Nombre de la tabla a la que aplica la regla RLS")
    column_name: col[str] = column(description="Nombre de la columna a la que se le aplica la regla RLS")

    # Una regla es de un realm: sin la FK, borrar el realm dejaba sus reglas sueltas.
    realm: manytoone[Realm] = relation(fields=["realm_id"], references=["id"], backref="rls_rules")
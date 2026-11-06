# Este archivo ha sido generado automáticamente por tai-sql
# No modifiques este archivo directamente

from __future__ import annotations
from typing import (
    List,
    Optional,
    Dict,
    Any,
    TYPE_CHECKING,
)
from datetime import datetime
from uuid import UUID
from sqlalchemy import false
from sqlalchemy.orm.query import Query
from pydantic import (
    Field,
    ConfigDict,
    field_validator,
    model_validator,
)

from .model import User
from .._shared import (
    PrettyModel,
    get_username,
    should_include_relation,
    get_nested_includes
)


if TYPE_CHECKING:
    from pandas import DataFrame, Series  # type: ignore[import-untyped]



class UserRead(PrettyModel):
    """DTO de lectura para User.

    No lleva `password`: son columnas hasheadas
    y su valor original no existe en ninguna parte, así que no hay nada que devolver. Para
    comprobar un candidato, `verify_<columna>()` en el modelo.

    Las columnas cifradas **sí** salen, y descifradas: `encrypt=True` protege el dato en
    reposo —de quien lea el fichero de la base de datos o un backup—, no del consumidor
    de la API. Quién puede leer qué lo deciden los permisos, no el cifrado; si el valor no
    se pudiera devolver, cifrarlo no serviría de nada.
    """
    id: UUID = Field(
        description="Identidad del usuario: la genera la base de datos y no se reutiliza",
    )
    username: str = Field(
        description="Nombre de usuario, único en su realm",
    )
    realm_id: int = Field(
        description="Realm al que pertenece el usuario",
    )
    first_name: Optional[str] = Field(
        description="Nombre del usuario",
    )
    last_name: Optional[str] = Field(
        description="Apellido del usuario",
    )
    email: Optional[str] = Field(
        description="Correo electrónico",
    )
    is_active: bool = Field(
        description="Usuario activo",
    )
    session_id: Optional[str] = Field(
        description="ID de sesión actual (para control de concurrencia)",
    )
    refresh_generation: Optional[int] = Field(
        description="Generación del refresh token vigente de la sesión",
    )
    refresh_rotated_at: Optional[datetime] = Field(
        description="Cuándo se rotó por última vez el refresh token",
    )
    password_expiration: Optional[datetime] = Field(
        description="Fecha de expiración de la contraseña",
    )
    attributes: Optional[Dict[str, Any]] = Field(
        description="Atributos adicionales del usuario (JSON)",
    )
    full_name: Optional[str] = Field(
        description="Columna calculada full_name",
    )
    created_at: datetime = Field(
        description="Fecha y hora de creación del registro en User",
    )
    created_by: str = Field(
        description="Usuario que creó el registro en User",
    )
    updated_at: datetime = Field(
        description="Fecha y hora de la última actualización del registro en User",
    )
    updated_by: str = Field(
        description="Usuario que realizó la última actualización del registro en User",
    )

    realm: Optional[RealmRead] = Field(default=None)
    user_roles: Optional[List[UserRoleRead]] = Field(default=None)



    model_config = ConfigDict(
        # Performance optimizations
        arbitrary_types_allowed=False,  # Más rápido al validar tipos estrictos
        use_enum_values=True,
        validate_assignment=False,  # Valida en cada asignación
        frozen=False,  # Si True, hace el objeto inmutable
        str_strip_whitespace=False,  # No procesa strings automáticamente
        validate_default=False,  # No valida valores por defecto
        extra="forbid",  # Más rápido que "allow" o "ignore"
        # Configuraciones adicionales de v2
        populate_by_name=True,  # Permite usar alias y nombres originales
        use_attribute_docstrings=True,  # Usa docstrings como descripciones
        validate_call=True,  # Valida llamadas a métodos
    )
    
    @classmethod
    def from_instance(
        cls,
        instance: User,
        includes: Optional[List[str]] = None,
        max_depth: int = 5,
    ) -> UserRead:
        dto_data = {
            'id': instance.id,
            'username': instance.username,
            'realm_id': instance.realm_id,
            'first_name': instance.first_name,
            'last_name': instance.last_name,
            'email': instance.email,
            'is_active': instance.is_active,
            'session_id': instance.session_id,
            'refresh_generation': instance.refresh_generation,
            'refresh_rotated_at': instance.refresh_rotated_at,
            'password_expiration': instance.password_expiration,
            'attributes': instance.attributes,
            'full_name': instance.full_name,
            'created_at': instance.created_at,
            'created_by': instance.created_by,
            'updated_at': instance.updated_at,
            'updated_by': instance.updated_by,
        }

        if includes is not None and max_depth > 0:
            if should_include_relation('realm', includes):
                nested_includes = get_nested_includes('realm', includes)
                if hasattr(instance, 'realm') and instance.realm is not None:
                    dto_data['realm'] = RealmRead.from_instance(
                        instance.realm, nested_includes, max_depth - 1
                    )
            if should_include_relation('user_roles', includes):
                nested_includes = get_nested_includes('user_roles', includes)
                if hasattr(instance, 'user_roles') and instance.user_roles is not None:
                    dto_data['user_roles'] = [
                        UserRoleRead.from_instance(reg, nested_includes, max_depth - 1) 
                        for reg in instance.user_roles
                    ]
        return cls(**dto_data)

    @classmethod
    def from_created_instance(cls, instance: User, included: set[str], excluded: str=None) -> UserRead:
        dto_data = {
            'id': instance.id,
            'username': instance.username,
            'realm_id': instance.realm_id,
            'first_name': instance.first_name,
            'last_name': instance.last_name,
            'email': instance.email,
            'is_active': instance.is_active,
            'session_id': instance.session_id,
            'refresh_generation': instance.refresh_generation,
            'refresh_rotated_at': instance.refresh_rotated_at,
            'password_expiration': instance.password_expiration,
            'attributes': instance.attributes,
            'full_name': instance.full_name,
            'created_at': instance.created_at,
            'created_by': instance.created_by,
            'updated_at': instance.updated_at,
            'updated_by': instance.updated_by,
        }
        if 'realm' in included and 'realm' != excluded:
            dto_data['realm'] = RealmRead.from_created_instance(
                instance.realm, included, 'users'
            )
        if 'user_roles' in included and 'user_roles' != excluded:
            dto_data['user_roles'] = [
                UserRoleRead.from_created_instance(reg, included, 'user') 
                for reg in instance.user_roles
            ]
        return cls(**dto_data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> UserRead:
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()




def _rechazar_padre_propio(hijos: List[Any], relacion: str, hijo: str, padre: str, field: str) -> None:
    """
    Un hijo anidado no trae la relación con su padre: cuelga del registro bajo el que se
    escribe. Con ella crearía otro padre y acabaría colgando de él (en un `update`) o ese
    padre se perdería sin error (en un `create`). Se rechaza en vez de elegir uno.
    """
    for indice, registro in enumerate(hijos):
        if getattr(registro, relacion, None) is not None:
            raise ValueError(
                f"{field}[{indice}]: un {hijo} anidado no puede traer '{relacion}'. Cuelga "
                f"del {padre} bajo el que se escribe, y con la relación se crearía otro "
                f"{padre} del que acabaría colgando. Quita '{relacion}' del hijo; si necesitas "
                f"otro {padre}, créalo aparte y escribe este {hijo} con el DAO de su tabla."
            )


class UserCreate(PrettyModel):
    """DTO de escritura para User."""
    username: str
    password: str
    realm_id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    is_active: bool = True
    session_id: Optional[str] = None
    refresh_generation: Optional[int] = None
    refresh_rotated_at: Optional[datetime] = None
    password_expiration: Optional[datetime] = None
    attributes: Optional[Dict[str, Any]] = None

    realm: Optional[RealmCreate] = None
    user_roles: Optional[List[UserRoleCreate]] = None

    model_config = ConfigDict(
        # Performance optimizations
        arbitrary_types_allowed=False,  # Más rápido al validar tipos estrictos
        use_enum_values=True,
        validate_assignment=False,  # Valida en cada asignación
        frozen=False,  # Si True, hace el objeto inmutable
        str_strip_whitespace=False,  # No procesa strings automáticamente
        validate_default=False,  # No valida valores por defecto
        extra="forbid",  # Más rápido que "allow" o "ignore"
        # Configuraciones adicionales de v2
        populate_by_name=True,  # Permite usar alias y nombres originales
        use_attribute_docstrings=True,  # Usa docstrings como descripciones
        validate_call=True,  # Valida llamadas a métodos
    )

    @model_validator(mode='after')
    def _anidados_sin_padre_propio(self) -> UserCreate:
        """Los hijos anidados cuelgan de este registro: ninguno trae su propio padre."""
        self._rechazar_padre_en_anidados()
        return self

    def _rechazar_padre_en_anidados(self) -> None:
        """
        Lanza si un hijo anidado trae la relación con su padre.

        Con ella, la fila de la relación se crearía aparte y el hijo acabaría colgando de
        ella o, aquí, la relación del padre ganaría y esa fila se perdería sin error. La
        llaman el validador y `create()`, que la repite por una DTO modificada después.
        """
        _rechazar_padre_propio(self.user_roles or [], 'user', 'UserRole', 'User', 'user_roles')
    
    def to_instance(self) -> User:
        model = User(
            username=self.username,
            realm_id=self.realm_id,
            first_name=self.first_name,
            last_name=self.last_name,
            password=self.password,
            email=self.email,
            is_active=self.is_active,
            session_id=self.session_id,
            refresh_generation=self.refresh_generation,
            refresh_rotated_at=self.refresh_rotated_at,
            password_expiration=self.password_expiration,
            attributes=self.attributes,
        )
        model.created_by = get_username()
        model.updated_by = get_username()
        if self.realm is not None:
            realm = self.realm.to_instance()
            model.realm = realm
        if self.user_roles is not None:
            user_roles = [reg.to_instance() for reg in self.user_roles]
            model.user_roles = user_roles
        return model
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> UserCreate:
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True)




class UserFilter(PrettyModel):
    """DTO de filtrado para User."""
    in_id: Optional[List[UUID]] = None
    username: Optional[str] = None
    in_username: Optional[List[str]] = None
    realm_id: Optional[int] = None
    in_realm_id: Optional[List[int]] = None
    min_realm_id: Optional[int] = None
    max_realm_id: Optional[int] = None
    first_name: Optional[str] = None
    in_first_name: Optional[List[str]] = None
    last_name: Optional[str] = None
    in_last_name: Optional[List[str]] = None
    email: Optional[str] = None
    in_email: Optional[List[str]] = None
    is_active: Optional[bool] = None
    session_id: Optional[str] = None
    in_session_id: Optional[List[str]] = None
    refresh_generation: Optional[int] = None
    in_refresh_generation: Optional[List[int]] = None
    min_refresh_generation: Optional[int] = None
    max_refresh_generation: Optional[int] = None
    min_refresh_rotated_at: Optional[datetime] = None
    max_refresh_rotated_at: Optional[datetime] = None
    min_password_expiration: Optional[datetime] = None
    max_password_expiration: Optional[datetime] = None
    full_name: Optional[str] = None
    in_full_name: Optional[List[str]] = None
    min_created_at: Optional[datetime] = None
    max_created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    in_created_by: Optional[List[str]] = None
    min_updated_at: Optional[datetime] = None
    max_updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    in_updated_by: Optional[List[str]] = None


    model_config = ConfigDict(
        # Performance optimizations
        arbitrary_types_allowed=False,  # Más rápido al validar tipos estrictos
        use_enum_values=True,
        validate_assignment=False,  # Valida en cada asignación
        frozen=False,  # Si True, hace el objeto inmutable
        str_strip_whitespace=False,  # No procesa strings automáticamente
        validate_default=False,  # No valida valores por defecto
        extra="forbid",  # Más rápido que "allow" o "ignore"
        # Configuraciones adicionales de v2
        populate_by_name=True,  # Permite usar alias y nombres originales
        use_attribute_docstrings=True,  # Usa docstrings como descripciones
        validate_call=True,  # Valida llamadas a métodos
    )
    
    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_defaults=True)

    def apply_to_query(self, query: Query) -> Query:
        if self.in_id is not None:
            query = query.where(User.id.in_(self.in_id) if self.in_id else false())
        if self.username is not None:
            if isinstance(self.username, str) and '%' in self.username:
                query = query.where(User.username.ilike(self.username))
            else:
                query = query.where(User.username == self.username)
        if self.in_username is not None:
            query = query.where(User.username.in_(self.in_username) if self.in_username else false())
        if self.realm_id is not None:
            query = query.where(User.realm_id == self.realm_id)
        if self.in_realm_id is not None:
            query = query.where(User.realm_id.in_(self.in_realm_id) if self.in_realm_id else false())
        if self.min_realm_id is not None:
            query = query.where(User.realm_id >= self.min_realm_id)
        if self.max_realm_id is not None:
            query = query.where(User.realm_id <= self.max_realm_id)
        if self.first_name is not None:
            if isinstance(self.first_name, str) and '%' in self.first_name:
                query = query.where(User.first_name.ilike(self.first_name))
            else:
                query = query.where(User.first_name == self.first_name)
        if self.in_first_name is not None:
            query = query.where(User.first_name.in_(self.in_first_name) if self.in_first_name else false())
        if self.last_name is not None:
            if isinstance(self.last_name, str) and '%' in self.last_name:
                query = query.where(User.last_name.ilike(self.last_name))
            else:
                query = query.where(User.last_name == self.last_name)
        if self.in_last_name is not None:
            query = query.where(User.last_name.in_(self.in_last_name) if self.in_last_name else false())
        if self.email is not None:
            if isinstance(self.email, str) and '%' in self.email:
                query = query.where(User.email.ilike(self.email))
            else:
                query = query.where(User.email == self.email)
        if self.in_email is not None:
            query = query.where(User.email.in_(self.in_email) if self.in_email else false())
        if self.is_active is not None:
            query = query.where(User.is_active == self.is_active)
        if self.session_id is not None:
            if isinstance(self.session_id, str) and '%' in self.session_id:
                query = query.where(User.session_id.ilike(self.session_id))
            else:
                query = query.where(User.session_id == self.session_id)
        if self.in_session_id is not None:
            query = query.where(User.session_id.in_(self.in_session_id) if self.in_session_id else false())
        if self.refresh_generation is not None:
            query = query.where(User.refresh_generation == self.refresh_generation)
        if self.in_refresh_generation is not None:
            query = query.where(User.refresh_generation.in_(self.in_refresh_generation) if self.in_refresh_generation else false())
        if self.min_refresh_generation is not None:
            query = query.where(User.refresh_generation >= self.min_refresh_generation)
        if self.max_refresh_generation is not None:
            query = query.where(User.refresh_generation <= self.max_refresh_generation)
        if self.min_refresh_rotated_at is not None:
            query = query.where(User.refresh_rotated_at >= self.min_refresh_rotated_at)
        if self.max_refresh_rotated_at is not None:
            query = query.where(User.refresh_rotated_at <= self.max_refresh_rotated_at)
        if self.min_password_expiration is not None:
            query = query.where(User.password_expiration >= self.min_password_expiration)
        if self.max_password_expiration is not None:
            query = query.where(User.password_expiration <= self.max_password_expiration)
        if self.full_name is not None:
            if isinstance(self.full_name, str) and '%' in self.full_name:
                query = query.where(User.full_name.ilike(self.full_name))
            else:
                query = query.where(User.full_name == self.full_name)
        if self.in_full_name is not None:
            query = query.where(User.full_name.in_(self.in_full_name) if self.in_full_name else false())
        if self.min_created_at is not None:
            query = query.where(User.created_at >= self.min_created_at)
        if self.max_created_at is not None:
            query = query.where(User.created_at <= self.max_created_at)
        if self.created_by is not None:
            if isinstance(self.created_by, str) and '%' in self.created_by:
                query = query.where(User.created_by.ilike(self.created_by))
            else:
                query = query.where(User.created_by == self.created_by)
        if self.in_created_by is not None:
            query = query.where(User.created_by.in_(self.in_created_by) if self.in_created_by else false())
        if self.min_updated_at is not None:
            query = query.where(User.updated_at >= self.min_updated_at)
        if self.max_updated_at is not None:
            query = query.where(User.updated_at <= self.max_updated_at)
        if self.updated_by is not None:
            if isinstance(self.updated_by, str) and '%' in self.updated_by:
                query = query.where(User.updated_by.ilike(self.updated_by))
            else:
                query = query.where(User.updated_by == self.updated_by)
        if self.in_updated_by is not None:
            query = query.where(User.updated_by.in_(self.in_updated_by) if self.in_updated_by else false())

        return query



class UserUser_rolesNestedUpdate(PrettyModel):
    """DTO para nested writes de 'user_roles' al actualizar User."""
    create: Optional[List[UserRoleCreate]] = None
    update: Optional[List[UserRoleUpdateNested]] = None
    delete: Optional[List[int]] = None

    model_config = ConfigDict(
        # Performance optimizations
        arbitrary_types_allowed=False,  # Más rápido al validar tipos estrictos
        use_enum_values=True,
        validate_assignment=False,  # Valida en cada asignación
        frozen=False,  # Si True, hace el objeto inmutable
        str_strip_whitespace=False,  # No procesa strings automáticamente
        validate_default=False,  # No valida valores por defecto
        extra="forbid",  # Más rápido que "allow" o "ignore"
        # Configuraciones adicionales de v2
        populate_by_name=True,  # Permite usar alias y nombres originales
        use_attribute_docstrings=True,  # Usa docstrings como descripciones
        validate_call=True,  # Valida llamadas a métodos
    )

    @field_validator('create')
    @classmethod
    def _altas_sin_padre_propio(cls, create):
        """Un alta anidada cuelga del registro que se actualiza: no trae `user`."""
        _rechazar_padre_propio(create or [], 'user', 'UserRole', 'User', 'user_roles.create')
        return create

    def _rechazar_padre_en_altas(self) -> None:
        """Lo mismo para una DTO modificada después de validarse: la llama el DAO."""
        self._altas_sin_padre_propio(self.create)



class UserUpdateNested(PrettyModel):
    """DTO para actualización anidada de User."""
    id: UUID
    values: UserUpdateValues

    model_config = ConfigDict(
        # Performance optimizations
        arbitrary_types_allowed=False,  # Más rápido al validar tipos estrictos
        use_enum_values=True,
        validate_assignment=False,  # Valida en cada asignación
        frozen=False,  # Si True, hace el objeto inmutable
        str_strip_whitespace=False,  # No procesa strings automáticamente
        validate_default=False,  # No valida valores por defecto
        extra="forbid",  # Más rápido que "allow" o "ignore"
        # Configuraciones adicionales de v2
        populate_by_name=True,  # Permite usar alias y nombres originales
        use_attribute_docstrings=True,  # Usa docstrings como descripciones
        validate_call=True,  # Valida llamadas a métodos
    )



class UserUpdateValues(PrettyModel):
    """DTO de actualización para User."""
    username: str = None
    realm_id: int = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: str = None
    email: Optional[str] = None
    is_active: bool = None
    session_id: Optional[str] = None
    refresh_generation: Optional[int] = None
    refresh_rotated_at: Optional[datetime] = None
    password_expiration: Optional[datetime] = None
    attributes: Optional[Dict[str, Any]] = None
    user_roles: Optional[UserUser_rolesNestedUpdate] = None

    model_config = ConfigDict(
        # Performance optimizations
        arbitrary_types_allowed=False,  # Más rápido al validar tipos estrictos
        use_enum_values=True,
        validate_assignment=False,  # Valida en cada asignación
        frozen=False,  # Si True, hace el objeto inmutable
        str_strip_whitespace=False,  # No procesa strings automáticamente
        validate_default=False,  # No valida valores por defecto
        extra="forbid",  # Más rápido que "allow" o "ignore"
        # Configuraciones adicionales de v2
        populate_by_name=True,  # Permite usar alias y nombres originales
        use_attribute_docstrings=True,  # Usa docstrings como descripciones
        validate_call=True,  # Valida llamadas a métodos
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_unset=True, exclude={
            'user_roles',
        })

    def _rechazar_anidadas_en_masivo(self) -> None:
        """
        Lanza si lleva escrituras anidadas: `update_many` no las aplica.

        Un anidado nombra hijos de **un** registro —los crea colgando de él, o los
        actualiza y borra por su clave—, y un update masivo no tiene uno, sino un filtro.
        Su `UPDATE ... SET` no las ve (`to_dict()` las deja fuera) y antes se perdían sin
        error. Lo llaman el `Update` al validarse y `update_many` antes de escribir.
        """
        anidadas = [
            nombre for nombre in ('user_roles',)
            if getattr(self, nombre) is not None
        ]
        if anidadas:
            raise ValueError(
                f"update_many no aplica escrituras anidadas ({', '.join(anidadas)}): un anidado "
                "nombra hijos de un registro y un update masivo no tiene uno, sino un filtro. "
                "Usa update() con la clave primaria de cada registro, o escribe los hijos con "
                "el DAO de su tabla (create_many, update_many, delete_many)."
            )



class UserUpdate(PrettyModel):
    """DTO de actualización completo para User."""
    filter: UserFilter
    values: UserUpdateValues

    model_config = ConfigDict(
        # Performance optimizations
        arbitrary_types_allowed=False,  # Más rápido al validar tipos estrictos
        use_enum_values=True,
        validate_assignment=False,  # Valida en cada asignación
        frozen=False,  # Si True, hace el objeto inmutable
        str_strip_whitespace=False,  # No procesa strings automáticamente
        validate_default=False,  # No valida valores por defecto
        extra="forbid",  # Más rápido que "allow" o "ignore"
        # Configuraciones adicionales de v2
        populate_by_name=True,  # Permite usar alias y nombres originales
        use_attribute_docstrings=True,  # Usa docstrings como descripciones
        validate_call=True,  # Valida llamadas a métodos
    )

    @field_validator('values')
    @classmethod
    def _sin_escrituras_anidadas(cls, values: UserUpdateValues) -> UserUpdateValues:
        """Un update masivo no lleva escrituras anidadas: se rechazan, no se descartan."""
        values._rechazar_anidadas_en_masivo()
        return values



from ..realm.dtos import (
    RealmRead,
    RealmCreate,
    RealmUpdateNested,
)
from ..user_role.dtos import (
    UserRoleRead,
    UserRoleCreate,
    UserRoleUpdateNested,
)



class UserDataFrameValidator:
    """Validador de DataFrame para el modelo User."""

    def validate_dataframe_schema(self, df: DataFrame, ignore_extra_columns: bool, fill_missing_nullable: bool) -> None:
        # Las columnas **calculadas quedan fuera**: su valor lo deriva el modelo de las
        # demás, así que exigirlas en el DataFrame es pedirle a quien llama que calcule lo
        # que el cliente calcula solo. Y una columna con default tampoco es obligatoria:
        # la rellena el modelo al escribir.
        model_columns = {
            'id': {
                'type': 'uuid',
                'nullable': False,
                'primary_key': True,
                'autoincrement': True,
                'has_default': False
            },
            'username': {
                'type': 'str',
                'nullable': False,
                'primary_key': False,
                'autoincrement': False,
                'has_default': False
            },
            'realm_id': {
                'type': 'bigint',
                'nullable': False,
                'primary_key': False,
                'autoincrement': False,
                'has_default': False
            },
            'first_name': {
                'type': 'str',
                'nullable': True,
                'primary_key': False,
                'autoincrement': False,
                'has_default': False
            },
            'last_name': {
                'type': 'str',
                'nullable': True,
                'primary_key': False,
                'autoincrement': False,
                'has_default': False
            },
            'password': {
                'type': 'str',
                'nullable': False,
                'primary_key': False,
                'autoincrement': False,
                'has_default': False
            },
            'email': {
                'type': 'str',
                'nullable': True,
                'primary_key': False,
                'autoincrement': False,
                'has_default': False
            },
            'is_active': {
                'type': 'bool',
                'nullable': False,
                'primary_key': False,
                'autoincrement': False,
                'has_default': True
            },
            'session_id': {
                'type': 'str',
                'nullable': True,
                'primary_key': False,
                'autoincrement': False,
                'has_default': False
            },
            'refresh_generation': {
                'type': 'int',
                'nullable': True,
                'primary_key': False,
                'autoincrement': False,
                'has_default': False
            },
            'refresh_rotated_at': {
                'type': 'datetime',
                'nullable': True,
                'primary_key': False,
                'autoincrement': False,
                'has_default': False
            },
            'password_expiration': {
                'type': 'datetime',
                'nullable': True,
                'primary_key': False,
                'autoincrement': False,
                'has_default': False
            },
            'attributes': {
                'type': 'dict',
                'nullable': True,
                'primary_key': False,
                'autoincrement': False,
                'has_default': False
            },
        }
        df_columns = set(df.columns)
        required_columns = set(model_columns.keys())
        extra_columns = df_columns - required_columns
        if extra_columns and not ignore_extra_columns:
            raise ValueError(f"DataFrame contiene columnas no definidas en el modelo: {list(extra_columns)}")
        missing_columns = required_columns - df_columns
        critical_missing = []
        for col in missing_columns:
            col_info = model_columns[col]
            if (not col_info['nullable'] and not col_info['autoincrement']
                and not col_info['has_default']
                and not (col_info['primary_key'] and col_info['autoincrement'])):
                critical_missing.append(col)
        if critical_missing:
            raise ValueError(f"DataFrame falta columnas requeridas (NOT NULL): {critical_missing}")
        nullable_missing = [col for col in missing_columns if col not in critical_missing]
        if nullable_missing and not fill_missing_nullable:
            import warnings
            warnings.warn(f"DataFrame falta columnas nullable: {nullable_missing}")
    
    def validate_dataframe_types(self, df: "DataFrame") -> None:
        type_compatibility = {
            'id': {
                'sqlalchemy_type': 'UUID',
                'compatible_pandas_types': [
                    'object'
                ]
            },
            'username': {
                'sqlalchemy_type': 'str',
                'compatible_pandas_types': [
                    'object', 'string', 'category'
                ]
            },
            'realm_id': {
                'sqlalchemy_type': 'int',
                'compatible_pandas_types': [
                    'int64', 'Int64', 'int32', 'Int32', 'int16', 'Int16', 'int8', 'Int8', 'object'
                ]
            },
            'first_name': {
                'sqlalchemy_type': 'str',
                'compatible_pandas_types': [
                    'object', 'string', 'category'
                ]
            },
            'last_name': {
                'sqlalchemy_type': 'str',
                'compatible_pandas_types': [
                    'object', 'string', 'category'
                ]
            },
            'password': {
                'sqlalchemy_type': 'str',
                'compatible_pandas_types': [
                    'object', 'string', 'category'
                ]
            },
            'email': {
                'sqlalchemy_type': 'str',
                'compatible_pandas_types': [
                    'object', 'string', 'category'
                ]
            },
            'is_active': {
                'sqlalchemy_type': 'bool',
                'compatible_pandas_types': [
                    'bool', 'boolean', 'object'
                ]
            },
            'session_id': {
                'sqlalchemy_type': 'str',
                'compatible_pandas_types': [
                    'object', 'string', 'category'
                ]
            },
            'refresh_generation': {
                'sqlalchemy_type': 'int',
                'compatible_pandas_types': [
                    'int64', 'Int64', 'int32', 'Int32', 'int16', 'Int16', 'int8', 'Int8', 'object'
                ]
            },
            'refresh_rotated_at': {
                'sqlalchemy_type': 'datetime',
                'compatible_pandas_types': [
                    'datetime64[ns]', 'object'
                ]
            },
            'password_expiration': {
                'sqlalchemy_type': 'datetime',
                'compatible_pandas_types': [
                    'datetime64[ns]', 'object'
                ]
            },
            'attributes': {
                'sqlalchemy_type': 'dict',
                'compatible_pandas_types': [
                    'object'
                ]
            },
            'full_name': {
                'sqlalchemy_type': 'str',
                'compatible_pandas_types': [
                    'object', 'string', 'category'
                ]
            },
        }
        type_errors = []
        for column in df.columns:
            if column in type_compatibility:
                df_dtype = str(df[column].dtype)
                compatible_types = type_compatibility[column]['compatible_pandas_types']
                sqlalchemy_type = type_compatibility[column]['sqlalchemy_type']
                if df_dtype not in compatible_types:
                    if self.can_convert_type(df[column], sqlalchemy_type):
                        continue
                    type_errors.append(
                        f"Columna '{column}': tipo '{df_dtype}' no compatible con '{sqlalchemy_type}'."
                    )
        if type_errors:
            raise TypeError("Errores de tipo:\n" + "\n".join(f"  - {e}" for e in type_errors))
    
    def can_convert_type(self, series: "Series", target_sqlalchemy_type: str) -> bool:
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas no está instalado.")
        try:
            sample = series.dropna().head(10)
            if sample.empty:
                return True
            if 'int' in target_sqlalchemy_type:
                pd.to_numeric(sample, errors='raise')
            elif 'float' in target_sqlalchemy_type or 'Numeric' in target_sqlalchemy_type:
                pd.to_numeric(sample, errors='raise')
            elif 'bool' in target_sqlalchemy_type:
                valid_bool_values = {True, False, 1, 0, '1', '0', 'true', 'false', 'True', 'False'}
                if not all(val in valid_bool_values for val in sample.unique()):
                    return False
            elif 'datetime' in target_sqlalchemy_type or 'date' in target_sqlalchemy_type:
                pd.to_datetime(sample, errors='raise')
            return True
        except:
            return False
    
    def prepare_dataframe_for_insertion(self, df: "DataFrame", ignore_extra_columns: bool, fill_missing_nullable: bool) -> "DataFrame":
        try:
            import pandas as pd
            import numpy as np
        except ImportError:
            return df
        cleaned_df = df.copy()
        model_columns = {
            'id': {
                'nullable': False,
                'autoincrement': True
            },
            'username': {
                'nullable': False,
                'autoincrement': False
            },
            'realm_id': {
                'nullable': False,
                'autoincrement': False
            },
            'first_name': {
                'nullable': True,
                'autoincrement': False
            },
            'last_name': {
                'nullable': True,
                'autoincrement': False
            },
            'password': {
                'nullable': False,
                'autoincrement': False
            },
            'email': {
                'nullable': True,
                'autoincrement': False
            },
            'is_active': {
                'nullable': False,
                'autoincrement': False
            },
            'session_id': {
                'nullable': True,
                'autoincrement': False
            },
            'refresh_generation': {
                'nullable': True,
                'autoincrement': False
            },
            'refresh_rotated_at': {
                'nullable': True,
                'autoincrement': False
            },
            'password_expiration': {
                'nullable': True,
                'autoincrement': False
            },
            'attributes': {
                'nullable': True,
                'autoincrement': False
            },
            'full_name': {
                'nullable': True,
                'autoincrement': False
            },
        }
        if ignore_extra_columns:
            extra_columns = set(cleaned_df.columns) - set(model_columns.keys())
            if extra_columns:
                cleaned_df = cleaned_df.drop(columns=list(extra_columns))
        if fill_missing_nullable:
            for col_name, col_info in model_columns.items():
                if (col_name not in cleaned_df.columns and col_info['nullable'] and not col_info['autoincrement']):
                    cleaned_df[col_name] = None
        autoincrement_columns = [
            col for col, info in model_columns.items() 
            if info['autoincrement'] and col in cleaned_df.columns
        ]
        if autoincrement_columns:
            cleaned_df = cleaned_df.drop(columns=autoincrement_columns)
        model_column_order = [col for col in model_columns.keys() if col in cleaned_df.columns]
        cleaned_df = cleaned_df[model_column_order]
        return cleaned_df
    
    def clean_records_data(self, records_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        try:
            import pandas as pd
        except ImportError:
            return records_data
        cleaned_records = []
        for record in records_data:
            cleaned_record = {}
            for key, value in record.items():
                if isinstance(value, list):
                    cleaned_record[key] = value
                elif pd.isna(value):
                    cleaned_record[key] = None
                elif hasattr(value, 'item'):
                    cleaned_record[key] = value.item()
                else:
                    cleaned_record[key] = value
            cleaned_records.append(cleaned_record)
        return cleaned_records
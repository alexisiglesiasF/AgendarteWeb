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
from sqlalchemy import false
from sqlalchemy.orm.query import Query
from pydantic import (
    Field,
    ConfigDict,
    field_validator,
    model_validator,
)

from .model import Permission
from .._shared import (
    PrettyModel,
    get_username,
    should_include_relation,
    get_nested_includes
)


if TYPE_CHECKING:
    from pandas import DataFrame, Series  # type: ignore[import-untyped]



class PermissionRead(PrettyModel):
    """DTO de lectura para Permission.

    """
    id: int = Field(
        description="Campo id de la tabla permission",
    )
    name: str = Field(
        description="Nombre del permiso (ej: usuario-read), único en su realm",
    )
    realm_id: int = Field(
        description="Realm al que pertenece el permiso",
    )
    description: Optional[str] = Field(
        description="Descripción del permiso",
    )
    type: str = Field(
        description="Tipo: api o app",
    )
    attributes: Optional[Dict[str, Any]] = Field(
        description="Atributos adicionales (JSON)",
    )
    created_at: datetime = Field(
        description="Fecha y hora de creación del registro en Permission",
    )
    created_by: str = Field(
        description="Usuario que creó el registro en Permission",
    )
    updated_at: datetime = Field(
        description="Fecha y hora de la última actualización del registro en Permission",
    )
    updated_by: str = Field(
        description="Usuario que realizó la última actualización del registro en Permission",
    )

    realm: Optional[RealmRead] = Field(default=None)
    role_permissions: Optional[List[RolePermissionRead]] = Field(default=None)



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
        instance: Permission,
        includes: Optional[List[str]] = None,
        max_depth: int = 5,
    ) -> PermissionRead:
        dto_data = {
            'id': instance.id,
            'name': instance.name,
            'realm_id': instance.realm_id,
            'description': instance.description,
            'type': instance.type,
            'attributes': instance.attributes,
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
            if should_include_relation('role_permissions', includes):
                nested_includes = get_nested_includes('role_permissions', includes)
                if hasattr(instance, 'role_permissions') and instance.role_permissions is not None:
                    dto_data['role_permissions'] = [
                        RolePermissionRead.from_instance(reg, nested_includes, max_depth - 1) 
                        for reg in instance.role_permissions
                    ]
        return cls(**dto_data)

    @classmethod
    def from_created_instance(cls, instance: Permission, included: set[str], excluded: str=None) -> PermissionRead:
        dto_data = {
            'id': instance.id,
            'name': instance.name,
            'realm_id': instance.realm_id,
            'description': instance.description,
            'type': instance.type,
            'attributes': instance.attributes,
            'created_at': instance.created_at,
            'created_by': instance.created_by,
            'updated_at': instance.updated_at,
            'updated_by': instance.updated_by,
        }
        if 'realm' in included and 'realm' != excluded:
            dto_data['realm'] = RealmRead.from_created_instance(
                instance.realm, included, 'permissions'
            )
        if 'role_permissions' in included and 'role_permissions' != excluded:
            dto_data['role_permissions'] = [
                RolePermissionRead.from_created_instance(reg, included, 'permission') 
                for reg in instance.role_permissions
            ]
        return cls(**dto_data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PermissionRead:
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


class PermissionCreate(PrettyModel):
    """DTO de escritura para Permission."""
    name: str
    type: str
    realm_id: Optional[int] = None
    description: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None

    realm: Optional[RealmCreate] = None
    role_permissions: Optional[List[RolePermissionCreate]] = None

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
    def _anidados_sin_padre_propio(self) -> PermissionCreate:
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
        _rechazar_padre_propio(self.role_permissions or [], 'permission', 'RolePermission', 'Permission', 'role_permissions')
    
    def to_instance(self) -> Permission:
        model = Permission(
            name=self.name,
            realm_id=self.realm_id,
            description=self.description,
            type=self.type,
            attributes=self.attributes,
        )
        model.created_by = get_username()
        model.updated_by = get_username()
        if self.realm is not None:
            realm = self.realm.to_instance()
            model.realm = realm
        if self.role_permissions is not None:
            role_permissions = [reg.to_instance() for reg in self.role_permissions]
            model.role_permissions = role_permissions
        return model
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PermissionCreate:
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True)




class PermissionFilter(PrettyModel):
    """DTO de filtrado para Permission."""
    in_id: Optional[List[int]] = None
    name: Optional[str] = None
    in_name: Optional[List[str]] = None
    realm_id: Optional[int] = None
    in_realm_id: Optional[List[int]] = None
    min_realm_id: Optional[int] = None
    max_realm_id: Optional[int] = None
    description: Optional[str] = None
    in_description: Optional[List[str]] = None
    type: Optional[str] = None
    in_type: Optional[List[str]] = None
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
            query = query.where(Permission.id.in_(self.in_id) if self.in_id else false())
        if self.name is not None:
            if isinstance(self.name, str) and '%' in self.name:
                query = query.where(Permission.name.ilike(self.name))
            else:
                query = query.where(Permission.name == self.name)
        if self.in_name is not None:
            query = query.where(Permission.name.in_(self.in_name) if self.in_name else false())
        if self.realm_id is not None:
            query = query.where(Permission.realm_id == self.realm_id)
        if self.in_realm_id is not None:
            query = query.where(Permission.realm_id.in_(self.in_realm_id) if self.in_realm_id else false())
        if self.min_realm_id is not None:
            query = query.where(Permission.realm_id >= self.min_realm_id)
        if self.max_realm_id is not None:
            query = query.where(Permission.realm_id <= self.max_realm_id)
        if self.description is not None:
            if isinstance(self.description, str) and '%' in self.description:
                query = query.where(Permission.description.ilike(self.description))
            else:
                query = query.where(Permission.description == self.description)
        if self.in_description is not None:
            query = query.where(Permission.description.in_(self.in_description) if self.in_description else false())
        if self.type is not None:
            if isinstance(self.type, str) and '%' in self.type:
                query = query.where(Permission.type.ilike(self.type))
            else:
                query = query.where(Permission.type == self.type)
        if self.in_type is not None:
            query = query.where(Permission.type.in_(self.in_type) if self.in_type else false())
        if self.min_created_at is not None:
            query = query.where(Permission.created_at >= self.min_created_at)
        if self.max_created_at is not None:
            query = query.where(Permission.created_at <= self.max_created_at)
        if self.created_by is not None:
            if isinstance(self.created_by, str) and '%' in self.created_by:
                query = query.where(Permission.created_by.ilike(self.created_by))
            else:
                query = query.where(Permission.created_by == self.created_by)
        if self.in_created_by is not None:
            query = query.where(Permission.created_by.in_(self.in_created_by) if self.in_created_by else false())
        if self.min_updated_at is not None:
            query = query.where(Permission.updated_at >= self.min_updated_at)
        if self.max_updated_at is not None:
            query = query.where(Permission.updated_at <= self.max_updated_at)
        if self.updated_by is not None:
            if isinstance(self.updated_by, str) and '%' in self.updated_by:
                query = query.where(Permission.updated_by.ilike(self.updated_by))
            else:
                query = query.where(Permission.updated_by == self.updated_by)
        if self.in_updated_by is not None:
            query = query.where(Permission.updated_by.in_(self.in_updated_by) if self.in_updated_by else false())

        return query



class PermissionRole_permissionsNestedUpdate(PrettyModel):
    """DTO para nested writes de 'role_permissions' al actualizar Permission."""
    create: Optional[List[RolePermissionCreate]] = None
    update: Optional[List[RolePermissionUpdateNested]] = None
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
        """Un alta anidada cuelga del registro que se actualiza: no trae `permission`."""
        _rechazar_padre_propio(create or [], 'permission', 'RolePermission', 'Permission', 'role_permissions.create')
        return create

    def _rechazar_padre_en_altas(self) -> None:
        """Lo mismo para una DTO modificada después de validarse: la llama el DAO."""
        self._altas_sin_padre_propio(self.create)



class PermissionUpdateNested(PrettyModel):
    """DTO para actualización anidada de Permission."""
    id: int
    values: PermissionUpdateValues

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



class PermissionUpdateValues(PrettyModel):
    """DTO de actualización para Permission."""
    name: str = None
    realm_id: int = None
    description: Optional[str] = None
    type: str = None
    attributes: Optional[Dict[str, Any]] = None
    role_permissions: Optional[PermissionRole_permissionsNestedUpdate] = None

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
            'role_permissions',
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
            nombre for nombre in ('role_permissions',)
            if getattr(self, nombre) is not None
        ]
        if anidadas:
            raise ValueError(
                f"update_many no aplica escrituras anidadas ({', '.join(anidadas)}): un anidado "
                "nombra hijos de un registro y un update masivo no tiene uno, sino un filtro. "
                "Usa update() con la clave primaria de cada registro, o escribe los hijos con "
                "el DAO de su tabla (create_many, update_many, delete_many)."
            )



class PermissionUpdate(PrettyModel):
    """DTO de actualización completo para Permission."""
    filter: PermissionFilter
    values: PermissionUpdateValues

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
    def _sin_escrituras_anidadas(cls, values: PermissionUpdateValues) -> PermissionUpdateValues:
        """Un update masivo no lleva escrituras anidadas: se rechazan, no se descartan."""
        values._rechazar_anidadas_en_masivo()
        return values



from ..realm.dtos import (
    RealmRead,
    RealmCreate,
    RealmUpdateNested,
)
from ..role_permission.dtos import (
    RolePermissionRead,
    RolePermissionCreate,
    RolePermissionUpdateNested,
)



class PermissionDataFrameValidator:
    """Validador de DataFrame para el modelo Permission."""

    def validate_dataframe_schema(self, df: DataFrame, ignore_extra_columns: bool, fill_missing_nullable: bool) -> None:
        # Las columnas **calculadas quedan fuera**: su valor lo deriva el modelo de las
        # demás, así que exigirlas en el DataFrame es pedirle a quien llama que calcule lo
        # que el cliente calcula solo. Y una columna con default tampoco es obligatoria:
        # la rellena el modelo al escribir.
        model_columns = {
            'id': {
                'type': 'bigint',
                'nullable': False,
                'primary_key': True,
                'autoincrement': True,
                'has_default': False
            },
            'name': {
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
            'description': {
                'type': 'str',
                'nullable': True,
                'primary_key': False,
                'autoincrement': False,
                'has_default': False
            },
            'type': {
                'type': 'str',
                'nullable': False,
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
                'sqlalchemy_type': 'int',
                'compatible_pandas_types': [
                    'int64', 'Int64', 'int32', 'Int32', 'int16', 'Int16', 'int8', 'Int8', 'object'
                ]
            },
            'name': {
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
            'description': {
                'sqlalchemy_type': 'str',
                'compatible_pandas_types': [
                    'object', 'string', 'category'
                ]
            },
            'type': {
                'sqlalchemy_type': 'str',
                'compatible_pandas_types': [
                    'object', 'string', 'category'
                ]
            },
            'attributes': {
                'sqlalchemy_type': 'dict',
                'compatible_pandas_types': [
                    'object'
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
            'name': {
                'nullable': False,
                'autoincrement': False
            },
            'realm_id': {
                'nullable': False,
                'autoincrement': False
            },
            'description': {
                'nullable': True,
                'autoincrement': False
            },
            'type': {
                'nullable': False,
                'autoincrement': False
            },
            'attributes': {
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
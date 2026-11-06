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
)

from .model import UserRole
from .._shared import (
    PrettyModel,
    get_username,
    should_include_relation,
    get_nested_includes
)


if TYPE_CHECKING:
    from pandas import DataFrame, Series  # type: ignore[import-untyped]



class UserRoleRead(PrettyModel):
    """DTO de lectura para UserRole.

    """
    id: int = Field(
        description="Campo id de la tabla user_role",
    )
    user_id: UUID = Field(
        description="Usuario",
    )
    role_id: int = Field(
        description="Rol",
    )
    created_at: datetime = Field(
        description="Fecha y hora de creación del registro en UserRole",
    )
    created_by: str = Field(
        description="Usuario que creó el registro en UserRole",
    )
    updated_at: datetime = Field(
        description="Fecha y hora de la última actualización del registro en UserRole",
    )
    updated_by: str = Field(
        description="Usuario que realizó la última actualización del registro en UserRole",
    )

    user: Optional[UserRead] = Field(default=None)
    role: Optional[RoleRead] = Field(default=None)



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
        instance: UserRole,
        includes: Optional[List[str]] = None,
        max_depth: int = 5,
    ) -> UserRoleRead:
        dto_data = {
            'id': instance.id,
            'user_id': instance.user_id,
            'role_id': instance.role_id,
            'created_at': instance.created_at,
            'created_by': instance.created_by,
            'updated_at': instance.updated_at,
            'updated_by': instance.updated_by,
        }

        if includes is not None and max_depth > 0:
            if should_include_relation('user', includes):
                nested_includes = get_nested_includes('user', includes)
                if hasattr(instance, 'user') and instance.user is not None:
                    dto_data['user'] = UserRead.from_instance(
                        instance.user, nested_includes, max_depth - 1
                    )
            if should_include_relation('role', includes):
                nested_includes = get_nested_includes('role', includes)
                if hasattr(instance, 'role') and instance.role is not None:
                    dto_data['role'] = RoleRead.from_instance(
                        instance.role, nested_includes, max_depth - 1
                    )
        return cls(**dto_data)

    @classmethod
    def from_created_instance(cls, instance: UserRole, included: set[str], excluded: str=None) -> UserRoleRead:
        dto_data = {
            'id': instance.id,
            'user_id': instance.user_id,
            'role_id': instance.role_id,
            'created_at': instance.created_at,
            'created_by': instance.created_by,
            'updated_at': instance.updated_at,
            'updated_by': instance.updated_by,
        }
        if 'user' in included and 'user' != excluded:
            dto_data['user'] = UserRead.from_created_instance(
                instance.user, included, 'user_roles'
            )
        if 'role' in included and 'role' != excluded:
            dto_data['role'] = RoleRead.from_created_instance(
                instance.role, included, 'user_roles'
            )
        return cls(**dto_data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> UserRoleRead:
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()




class UserRoleCreate(PrettyModel):
    """DTO de escritura para UserRole."""
    user_id: Optional[UUID] = None
    role_id: Optional[int] = None

    user: Optional[UserCreate] = None
    role: Optional[RoleCreate] = None

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
    
    def to_instance(self) -> UserRole:
        model = UserRole(
            user_id=self.user_id,
            role_id=self.role_id,
        )
        model.created_by = get_username()
        model.updated_by = get_username()
        if self.user is not None:
            user = self.user.to_instance()
            model.user = user
        if self.role is not None:
            role = self.role.to_instance()
            model.role = role
        return model
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> UserRoleCreate:
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True)




class UserRoleFilter(PrettyModel):
    """DTO de filtrado para UserRole."""
    in_id: Optional[List[int]] = None
    user_id: Optional[UUID] = None
    in_user_id: Optional[List[UUID]] = None
    role_id: Optional[int] = None
    in_role_id: Optional[List[int]] = None
    min_role_id: Optional[int] = None
    max_role_id: Optional[int] = None
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
            query = query.where(UserRole.id.in_(self.in_id) if self.in_id else false())
        if self.user_id is not None:
            query = query.where(UserRole.user_id == self.user_id)
        if self.in_user_id is not None:
            query = query.where(UserRole.user_id.in_(self.in_user_id) if self.in_user_id else false())
        if self.role_id is not None:
            query = query.where(UserRole.role_id == self.role_id)
        if self.in_role_id is not None:
            query = query.where(UserRole.role_id.in_(self.in_role_id) if self.in_role_id else false())
        if self.min_role_id is not None:
            query = query.where(UserRole.role_id >= self.min_role_id)
        if self.max_role_id is not None:
            query = query.where(UserRole.role_id <= self.max_role_id)
        if self.min_created_at is not None:
            query = query.where(UserRole.created_at >= self.min_created_at)
        if self.max_created_at is not None:
            query = query.where(UserRole.created_at <= self.max_created_at)
        if self.created_by is not None:
            if isinstance(self.created_by, str) and '%' in self.created_by:
                query = query.where(UserRole.created_by.ilike(self.created_by))
            else:
                query = query.where(UserRole.created_by == self.created_by)
        if self.in_created_by is not None:
            query = query.where(UserRole.created_by.in_(self.in_created_by) if self.in_created_by else false())
        if self.min_updated_at is not None:
            query = query.where(UserRole.updated_at >= self.min_updated_at)
        if self.max_updated_at is not None:
            query = query.where(UserRole.updated_at <= self.max_updated_at)
        if self.updated_by is not None:
            if isinstance(self.updated_by, str) and '%' in self.updated_by:
                query = query.where(UserRole.updated_by.ilike(self.updated_by))
            else:
                query = query.where(UserRole.updated_by == self.updated_by)
        if self.in_updated_by is not None:
            query = query.where(UserRole.updated_by.in_(self.in_updated_by) if self.in_updated_by else false())

        return query





class UserRoleUpdateNested(PrettyModel):
    """DTO para actualización anidada de UserRole."""
    id: int
    values: UserRoleUpdateValues

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



class UserRoleUpdateValues(PrettyModel):
    """DTO de actualización para UserRole."""
    user_id: UUID = None
    role_id: int = None

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
        })



class UserRoleUpdate(PrettyModel):
    """DTO de actualización completo para UserRole."""
    filter: UserRoleFilter
    values: UserRoleUpdateValues

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



from ..user.dtos import (
    UserRead,
    UserCreate,
    UserUpdateNested,
)
from ..role.dtos import (
    RoleRead,
    RoleCreate,
    RoleUpdateNested,
)



class UserRoleDataFrameValidator:
    """Validador de DataFrame para el modelo UserRole."""

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
            'user_id': {
                'type': 'uuid',
                'nullable': False,
                'primary_key': False,
                'autoincrement': False,
                'has_default': False
            },
            'role_id': {
                'type': 'bigint',
                'nullable': False,
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
            'user_id': {
                'sqlalchemy_type': 'UUID',
                'compatible_pandas_types': [
                    'object'
                ]
            },
            'role_id': {
                'sqlalchemy_type': 'int',
                'compatible_pandas_types': [
                    'int64', 'Int64', 'int32', 'Int32', 'int16', 'Int16', 'int8', 'Int8', 'object'
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
            'user_id': {
                'nullable': False,
                'autoincrement': False
            },
            'role_id': {
                'nullable': False,
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
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
)

from .model import Ingreso
from .._shared import (
    PrettyModel,
    get_username,
    should_include_relation,
    get_nested_includes
)


if TYPE_CHECKING:
    from pandas import DataFrame, Series  # type: ignore[import-untyped]



class IngresoRead(PrettyModel):
    """DTO de lectura para Ingreso.

    """
    id: int = Field(
        description="Campo id de la tabla ingreso",
    )
    id_evento: Optional[int] = Field(
        description="Evento al que pertenece el ingreso",
    )
    nombre: str = Field(
        description="Nombre del ingreso",
    )
    importe: float = Field(
        description="Monto del ingreso",
    )
    recibido: bool = Field(
        description="Indica si el ingreso ha sido recibido o no",
    )
    concepto: Optional[str] = Field(
        description="Concepto del ingreso",
    )
    created_at: datetime = Field(
        description="Fecha y hora de creación del registro en Ingreso",
    )
    created_by: str = Field(
        description="Usuario que creó el registro en Ingreso",
    )
    updated_at: datetime = Field(
        description="Fecha y hora de la última actualización del registro en Ingreso",
    )
    updated_by: str = Field(
        description="Usuario que realizó la última actualización del registro en Ingreso",
    )

    evento: Optional[EventoRead] = Field(default=None)



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
        instance: Ingreso,
        includes: Optional[List[str]] = None,
        max_depth: int = 5,
    ) -> IngresoRead:
        dto_data = {
            'id': instance.id,
            'id_evento': instance.id_evento,
            'nombre': instance.nombre,
            'importe': instance.importe,
            'recibido': instance.recibido,
            'concepto': instance.concepto,
            'created_at': instance.created_at,
            'created_by': instance.created_by,
            'updated_at': instance.updated_at,
            'updated_by': instance.updated_by,
        }

        if includes is not None and max_depth > 0:
            if should_include_relation('evento', includes):
                nested_includes = get_nested_includes('evento', includes)
                if hasattr(instance, 'evento') and instance.evento is not None:
                    dto_data['evento'] = EventoRead.from_instance(
                        instance.evento, nested_includes, max_depth - 1
                    )
        return cls(**dto_data)

    @classmethod
    def from_created_instance(cls, instance: Ingreso, included: set[str], excluded: str=None) -> IngresoRead:
        dto_data = {
            'id': instance.id,
            'id_evento': instance.id_evento,
            'nombre': instance.nombre,
            'importe': instance.importe,
            'recibido': instance.recibido,
            'concepto': instance.concepto,
            'created_at': instance.created_at,
            'created_by': instance.created_by,
            'updated_at': instance.updated_at,
            'updated_by': instance.updated_by,
        }
        if 'evento' in included and 'evento' != excluded:
            dto_data['evento'] = EventoRead.from_created_instance(
                instance.evento, included, 'ingresos'
            )
        return cls(**dto_data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> IngresoRead:
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()




class IngresoCreate(PrettyModel):
    """DTO de escritura para Ingreso."""
    nombre: str
    importe: float
    id_evento: Optional[int] = None
    recibido: bool = False
    concepto: Optional[str] = None

    evento: Optional[EventoCreate] = None

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
    
    def to_instance(self) -> Ingreso:
        model = Ingreso(
            id_evento=self.id_evento,
            nombre=self.nombre,
            importe=self.importe,
            recibido=self.recibido,
            concepto=self.concepto,
        )
        model.created_by = get_username()
        model.updated_by = get_username()
        if self.evento is not None:
            evento = self.evento.to_instance()
            model.evento = evento
        return model
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> IngresoCreate:
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True)




class IngresoFilter(PrettyModel):
    """DTO de filtrado para Ingreso."""
    in_id: Optional[List[int]] = None
    id_evento: Optional[int] = None
    in_id_evento: Optional[List[int]] = None
    min_id_evento: Optional[int] = None
    max_id_evento: Optional[int] = None
    nombre: Optional[str] = None
    in_nombre: Optional[List[str]] = None
    min_importe: Optional[float] = None
    max_importe: Optional[float] = None
    recibido: Optional[bool] = None
    concepto: Optional[str] = None
    in_concepto: Optional[List[str]] = None
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
            query = query.where(Ingreso.id.in_(self.in_id) if self.in_id else false())
        if self.id_evento is not None:
            query = query.where(Ingreso.id_evento == self.id_evento)
        if self.in_id_evento is not None:
            query = query.where(Ingreso.id_evento.in_(self.in_id_evento) if self.in_id_evento else false())
        if self.min_id_evento is not None:
            query = query.where(Ingreso.id_evento >= self.min_id_evento)
        if self.max_id_evento is not None:
            query = query.where(Ingreso.id_evento <= self.max_id_evento)
        if self.nombre is not None:
            if isinstance(self.nombre, str) and '%' in self.nombre:
                query = query.where(Ingreso.nombre.ilike(self.nombre))
            else:
                query = query.where(Ingreso.nombre == self.nombre)
        if self.in_nombre is not None:
            query = query.where(Ingreso.nombre.in_(self.in_nombre) if self.in_nombre else false())
        if self.min_importe is not None:
            query = query.where(Ingreso.importe >= self.min_importe)
        if self.max_importe is not None:
            query = query.where(Ingreso.importe <= self.max_importe)
        if self.recibido is not None:
            query = query.where(Ingreso.recibido == self.recibido)
        if self.concepto is not None:
            if isinstance(self.concepto, str) and '%' in self.concepto:
                query = query.where(Ingreso.concepto.ilike(self.concepto))
            else:
                query = query.where(Ingreso.concepto == self.concepto)
        if self.in_concepto is not None:
            query = query.where(Ingreso.concepto.in_(self.in_concepto) if self.in_concepto else false())
        if self.min_created_at is not None:
            query = query.where(Ingreso.created_at >= self.min_created_at)
        if self.max_created_at is not None:
            query = query.where(Ingreso.created_at <= self.max_created_at)
        if self.created_by is not None:
            if isinstance(self.created_by, str) and '%' in self.created_by:
                query = query.where(Ingreso.created_by.ilike(self.created_by))
            else:
                query = query.where(Ingreso.created_by == self.created_by)
        if self.in_created_by is not None:
            query = query.where(Ingreso.created_by.in_(self.in_created_by) if self.in_created_by else false())
        if self.min_updated_at is not None:
            query = query.where(Ingreso.updated_at >= self.min_updated_at)
        if self.max_updated_at is not None:
            query = query.where(Ingreso.updated_at <= self.max_updated_at)
        if self.updated_by is not None:
            if isinstance(self.updated_by, str) and '%' in self.updated_by:
                query = query.where(Ingreso.updated_by.ilike(self.updated_by))
            else:
                query = query.where(Ingreso.updated_by == self.updated_by)
        if self.in_updated_by is not None:
            query = query.where(Ingreso.updated_by.in_(self.in_updated_by) if self.in_updated_by else false())

        return query





class IngresoUpdateNested(PrettyModel):
    """DTO para actualización anidada de Ingreso."""
    id: int
    values: IngresoUpdateValues

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



class IngresoUpdateValues(PrettyModel):
    """DTO de actualización para Ingreso."""
    id_evento: Optional[int] = None
    nombre: str = None
    importe: float = None
    recibido: bool = None
    concepto: Optional[str] = None

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



class IngresoUpdate(PrettyModel):
    """DTO de actualización completo para Ingreso."""
    filter: IngresoFilter
    values: IngresoUpdateValues

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



from ..evento.dtos import (
    EventoRead,
    EventoCreate,
    EventoUpdateNested,
)



class IngresoDataFrameValidator:
    """Validador de DataFrame para el modelo Ingreso."""

    def validate_dataframe_schema(self, df: DataFrame, ignore_extra_columns: bool, fill_missing_nullable: bool) -> None:
        # Las columnas **calculadas quedan fuera**: su valor lo deriva el modelo de las
        # demás, así que exigirlas en el DataFrame es pedirle a quien llama que calcule lo
        # que el cliente calcula solo. Y una columna con default tampoco es obligatoria:
        # la rellena el modelo al escribir.
        model_columns = {
            'id': {
                'type': 'int',
                'nullable': False,
                'primary_key': True,
                'autoincrement': True,
                'has_default': False
            },
            'id_evento': {
                'type': 'int',
                'nullable': True,
                'primary_key': False,
                'autoincrement': False,
                'has_default': False
            },
            'nombre': {
                'type': 'str',
                'nullable': False,
                'primary_key': False,
                'autoincrement': False,
                'has_default': False
            },
            'importe': {
                'type': 'numeric',
                'nullable': False,
                'primary_key': False,
                'autoincrement': False,
                'has_default': False
            },
            'recibido': {
                'type': 'bool',
                'nullable': False,
                'primary_key': False,
                'autoincrement': False,
                'has_default': True
            },
            'concepto': {
                'type': 'str',
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
            'id_evento': {
                'sqlalchemy_type': 'int',
                'compatible_pandas_types': [
                    'int64', 'Int64', 'int32', 'Int32', 'int16', 'Int16', 'int8', 'Int8', 'object'
                ]
            },
            'nombre': {
                'sqlalchemy_type': 'str',
                'compatible_pandas_types': [
                    'object', 'string', 'category'
                ]
            },
            'importe': {
                'sqlalchemy_type': 'float',
                'compatible_pandas_types': [
                    'float64', 'float32', 'int64', 'Int64', 'object'
                ]
            },
            'recibido': {
                'sqlalchemy_type': 'bool',
                'compatible_pandas_types': [
                    'bool', 'boolean', 'object'
                ]
            },
            'concepto': {
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
            'id_evento': {
                'nullable': True,
                'autoincrement': False
            },
            'nombre': {
                'nullable': False,
                'autoincrement': False
            },
            'importe': {
                'nullable': False,
                'autoincrement': False
            },
            'recibido': {
                'nullable': False,
                'autoincrement': False
            },
            'concepto': {
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
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

from .model import Usuario
from .._shared import (
    PrettyModel,
    get_username,
    should_include_relation,
    get_nested_includes
)


if TYPE_CHECKING:
    from pandas import DataFrame, Series  # type: ignore[import-untyped]



class UsuarioRead(PrettyModel):
    """DTO de lectura para Usuario.

    """
    id: int = Field(
        description="Campo id de la tabla usuario",
    )
    nombre: str = Field(
        description="Nombre visible",
    )
    apellido: str = Field(
        description="Apellido visible",
    )
    email: str = Field(
        description="Campo email de la tabla usuario",
    )
    created_at: datetime = Field(
        description="Fecha y hora de creación del registro en Usuario",
    )
    created_by: str = Field(
        description="Usuario que creó el registro en Usuario",
    )
    updated_at: datetime = Field(
        description="Fecha y hora de la última actualización del registro en Usuario",
    )
    updated_by: str = Field(
        description="Usuario que realizó la última actualización del registro en Usuario",
    )

    proyectos: Optional[List[ProyectoRead]] = Field(default=None)
    eventos: Optional[List[EventoRead]] = Field(default=None)
    repertorios: Optional[List[RepertorioRead]] = Field(default=None)



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
        instance: Usuario,
        includes: Optional[List[str]] = None,
        max_depth: int = 5,
    ) -> UsuarioRead:
        dto_data = {
            'id': instance.id,
            'nombre': instance.nombre,
            'apellido': instance.apellido,
            'email': instance.email,
            'created_at': instance.created_at,
            'created_by': instance.created_by,
            'updated_at': instance.updated_at,
            'updated_by': instance.updated_by,
        }

        if includes is not None and max_depth > 0:
            if should_include_relation('proyectos', includes):
                nested_includes = get_nested_includes('proyectos', includes)
                if hasattr(instance, 'proyectos') and instance.proyectos is not None:
                    dto_data['proyectos'] = [
                        ProyectoRead.from_instance(reg, nested_includes, max_depth - 1) 
                        for reg in instance.proyectos
                    ]
            if should_include_relation('eventos', includes):
                nested_includes = get_nested_includes('eventos', includes)
                if hasattr(instance, 'eventos') and instance.eventos is not None:
                    dto_data['eventos'] = [
                        EventoRead.from_instance(reg, nested_includes, max_depth - 1) 
                        for reg in instance.eventos
                    ]
            if should_include_relation('repertorios', includes):
                nested_includes = get_nested_includes('repertorios', includes)
                if hasattr(instance, 'repertorios') and instance.repertorios is not None:
                    dto_data['repertorios'] = [
                        RepertorioRead.from_instance(reg, nested_includes, max_depth - 1) 
                        for reg in instance.repertorios
                    ]
        return cls(**dto_data)

    @classmethod
    def from_created_instance(cls, instance: Usuario, included: set[str], excluded: str=None) -> UsuarioRead:
        dto_data = {
            'id': instance.id,
            'nombre': instance.nombre,
            'apellido': instance.apellido,
            'email': instance.email,
            'created_at': instance.created_at,
            'created_by': instance.created_by,
            'updated_at': instance.updated_at,
            'updated_by': instance.updated_by,
        }
        if 'proyectos' in included and 'proyectos' != excluded:
            dto_data['proyectos'] = [
                ProyectoRead.from_created_instance(reg, included, 'usuario') 
                for reg in instance.proyectos
            ]
        if 'eventos' in included and 'eventos' != excluded:
            dto_data['eventos'] = [
                EventoRead.from_created_instance(reg, included, 'usuario') 
                for reg in instance.eventos
            ]
        if 'repertorios' in included and 'repertorios' != excluded:
            dto_data['repertorios'] = [
                RepertorioRead.from_created_instance(reg, included, 'usuario') 
                for reg in instance.repertorios
            ]
        return cls(**dto_data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> UsuarioRead:
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


class UsuarioCreate(PrettyModel):
    """DTO de escritura para Usuario."""
    nombre: str
    apellido: str
    email: str

    proyectos: Optional[List[ProyectoCreate]] = None
    eventos: Optional[List[EventoCreate]] = None
    repertorios: Optional[List[RepertorioCreate]] = None

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
    def _anidados_sin_padre_propio(self) -> UsuarioCreate:
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
        _rechazar_padre_propio(self.proyectos or [], 'usuario', 'Proyecto', 'Usuario', 'proyectos')
        _rechazar_padre_propio(self.eventos or [], 'usuario', 'Evento', 'Usuario', 'eventos')
        _rechazar_padre_propio(self.repertorios or [], 'usuario', 'Repertorio', 'Usuario', 'repertorios')
    
    def to_instance(self) -> Usuario:
        model = Usuario(
            nombre=self.nombre,
            apellido=self.apellido,
            email=self.email,
        )
        model.created_by = get_username()
        model.updated_by = get_username()
        if self.proyectos is not None:
            proyectos = [reg.to_instance() for reg in self.proyectos]
            model.proyectos = proyectos
        if self.eventos is not None:
            eventos = [reg.to_instance() for reg in self.eventos]
            model.eventos = eventos
        if self.repertorios is not None:
            repertorios = [reg.to_instance() for reg in self.repertorios]
            model.repertorios = repertorios
        return model
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> UsuarioCreate:
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True)




class UsuarioFilter(PrettyModel):
    """DTO de filtrado para Usuario."""
    in_id: Optional[List[int]] = None
    nombre: Optional[str] = None
    in_nombre: Optional[List[str]] = None
    apellido: Optional[str] = None
    in_apellido: Optional[List[str]] = None
    email: Optional[str] = None
    in_email: Optional[List[str]] = None
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
            query = query.where(Usuario.id.in_(self.in_id) if self.in_id else false())
        if self.nombre is not None:
            if isinstance(self.nombre, str) and '%' in self.nombre:
                query = query.where(Usuario.nombre.ilike(self.nombre))
            else:
                query = query.where(Usuario.nombre == self.nombre)
        if self.in_nombre is not None:
            query = query.where(Usuario.nombre.in_(self.in_nombre) if self.in_nombre else false())
        if self.apellido is not None:
            if isinstance(self.apellido, str) and '%' in self.apellido:
                query = query.where(Usuario.apellido.ilike(self.apellido))
            else:
                query = query.where(Usuario.apellido == self.apellido)
        if self.in_apellido is not None:
            query = query.where(Usuario.apellido.in_(self.in_apellido) if self.in_apellido else false())
        if self.email is not None:
            if isinstance(self.email, str) and '%' in self.email:
                query = query.where(Usuario.email.ilike(self.email))
            else:
                query = query.where(Usuario.email == self.email)
        if self.in_email is not None:
            query = query.where(Usuario.email.in_(self.in_email) if self.in_email else false())
        if self.min_created_at is not None:
            query = query.where(Usuario.created_at >= self.min_created_at)
        if self.max_created_at is not None:
            query = query.where(Usuario.created_at <= self.max_created_at)
        if self.created_by is not None:
            if isinstance(self.created_by, str) and '%' in self.created_by:
                query = query.where(Usuario.created_by.ilike(self.created_by))
            else:
                query = query.where(Usuario.created_by == self.created_by)
        if self.in_created_by is not None:
            query = query.where(Usuario.created_by.in_(self.in_created_by) if self.in_created_by else false())
        if self.min_updated_at is not None:
            query = query.where(Usuario.updated_at >= self.min_updated_at)
        if self.max_updated_at is not None:
            query = query.where(Usuario.updated_at <= self.max_updated_at)
        if self.updated_by is not None:
            if isinstance(self.updated_by, str) and '%' in self.updated_by:
                query = query.where(Usuario.updated_by.ilike(self.updated_by))
            else:
                query = query.where(Usuario.updated_by == self.updated_by)
        if self.in_updated_by is not None:
            query = query.where(Usuario.updated_by.in_(self.in_updated_by) if self.in_updated_by else false())

        return query



class UsuarioProyectosNestedUpdate(PrettyModel):
    """DTO para nested writes de 'proyectos' al actualizar Usuario."""
    create: Optional[List[ProyectoCreate]] = None
    update: Optional[List[ProyectoUpdateNested]] = None
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
        """Un alta anidada cuelga del registro que se actualiza: no trae `usuario`."""
        _rechazar_padre_propio(create or [], 'usuario', 'Proyecto', 'Usuario', 'proyectos.create')
        return create

    def _rechazar_padre_en_altas(self) -> None:
        """Lo mismo para una DTO modificada después de validarse: la llama el DAO."""
        self._altas_sin_padre_propio(self.create)

class UsuarioEventosNestedUpdate(PrettyModel):
    """DTO para nested writes de 'eventos' al actualizar Usuario."""
    create: Optional[List[EventoCreate]] = None
    update: Optional[List[EventoUpdateNested]] = None
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
        """Un alta anidada cuelga del registro que se actualiza: no trae `usuario`."""
        _rechazar_padre_propio(create or [], 'usuario', 'Evento', 'Usuario', 'eventos.create')
        return create

    def _rechazar_padre_en_altas(self) -> None:
        """Lo mismo para una DTO modificada después de validarse: la llama el DAO."""
        self._altas_sin_padre_propio(self.create)

class UsuarioRepertoriosNestedUpdate(PrettyModel):
    """DTO para nested writes de 'repertorios' al actualizar Usuario."""
    create: Optional[List[RepertorioCreate]] = None
    update: Optional[List[RepertorioUpdateNested]] = None
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
        """Un alta anidada cuelga del registro que se actualiza: no trae `usuario`."""
        _rechazar_padre_propio(create or [], 'usuario', 'Repertorio', 'Usuario', 'repertorios.create')
        return create

    def _rechazar_padre_en_altas(self) -> None:
        """Lo mismo para una DTO modificada después de validarse: la llama el DAO."""
        self._altas_sin_padre_propio(self.create)



class UsuarioUpdateNested(PrettyModel):
    """DTO para actualización anidada de Usuario."""
    id: int
    values: UsuarioUpdateValues

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



class UsuarioUpdateValues(PrettyModel):
    """DTO de actualización para Usuario."""
    nombre: str = None
    apellido: str = None
    email: str = None
    proyectos: Optional[UsuarioProyectosNestedUpdate] = None
    eventos: Optional[UsuarioEventosNestedUpdate] = None
    repertorios: Optional[UsuarioRepertoriosNestedUpdate] = None

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
            'proyectos',
            'eventos',
            'repertorios',
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
            nombre for nombre in ('proyectos', 'eventos', 'repertorios',)
            if getattr(self, nombre) is not None
        ]
        if anidadas:
            raise ValueError(
                f"update_many no aplica escrituras anidadas ({', '.join(anidadas)}): un anidado "
                "nombra hijos de un registro y un update masivo no tiene uno, sino un filtro. "
                "Usa update() con la clave primaria de cada registro, o escribe los hijos con "
                "el DAO de su tabla (create_many, update_many, delete_many)."
            )



class UsuarioUpdate(PrettyModel):
    """DTO de actualización completo para Usuario."""
    filter: UsuarioFilter
    values: UsuarioUpdateValues

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
    def _sin_escrituras_anidadas(cls, values: UsuarioUpdateValues) -> UsuarioUpdateValues:
        """Un update masivo no lleva escrituras anidadas: se rechazan, no se descartan."""
        values._rechazar_anidadas_en_masivo()
        return values



from ..proyecto.dtos import (
    ProyectoRead,
    ProyectoCreate,
    ProyectoUpdateNested,
)
from ..evento.dtos import (
    EventoRead,
    EventoCreate,
    EventoUpdateNested,
)
from ..repertorio.dtos import (
    RepertorioRead,
    RepertorioCreate,
    RepertorioUpdateNested,
)



class UsuarioDataFrameValidator:
    """Validador de DataFrame para el modelo Usuario."""

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
            'nombre': {
                'type': 'str',
                'nullable': False,
                'primary_key': False,
                'autoincrement': False,
                'has_default': False
            },
            'apellido': {
                'type': 'str',
                'nullable': False,
                'primary_key': False,
                'autoincrement': False,
                'has_default': False
            },
            'email': {
                'type': 'str',
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
            'nombre': {
                'sqlalchemy_type': 'str',
                'compatible_pandas_types': [
                    'object', 'string', 'category'
                ]
            },
            'apellido': {
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
            'nombre': {
                'nullable': False,
                'autoincrement': False
            },
            'apellido': {
                'nullable': False,
                'autoincrement': False
            },
            'email': {
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
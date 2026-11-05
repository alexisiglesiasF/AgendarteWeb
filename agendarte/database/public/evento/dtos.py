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
from datetime import datetime, time
from sqlalchemy import false
from sqlalchemy.orm.query import Query
from pydantic import (
    Field,
    ConfigDict,
    field_validator,
    model_validator,
)

from .model import Evento
from .._shared import (
    PrettyModel,
    get_username,
    should_include_relation,
    get_nested_includes
)


if TYPE_CHECKING:
    from pandas import DataFrame, Series  # type: ignore[import-untyped]



class EventoRead(PrettyModel):
    """DTO de lectura para Evento.

    """
    id: int = Field(
        description="Campo id de la tabla evento",
    )
    usuario_id: int = Field(
        description="Usuario que crea el evento",
    )
    id_proyecto: Optional[int] = Field(
        description="Proyecto al que pertenece el evento",
    )
    nombre: str = Field(
        description="Nombre del evento",
    )
    ubicacion: Optional[str] = Field(
        description="Ubicacion del evento",
    )
    tipo: str = Field(
        description="Tipo de evento",
    )
    fecha: datetime = Field(
        description="Fecha del evento",
    )
    hora: time = Field(
        description="Hora del evento",
    )
    estado: str = Field(
        description="Estado del evento",
    )
    notas: Optional[str] = Field(
        description="Notas adicionales del evento",
    )
    created_at: datetime = Field(
        description="Fecha y hora de creación del registro en Evento",
    )
    created_by: str = Field(
        description="Usuario que creó el registro en Evento",
    )
    updated_at: datetime = Field(
        description="Fecha y hora de la última actualización del registro en Evento",
    )
    updated_by: str = Field(
        description="Usuario que realizó la última actualización del registro en Evento",
    )

    proyecto: Optional[ProyectoRead] = Field(default=None)
    usuario: Optional[UsuarioRead] = Field(default=None)
    gastos: Optional[List[GastoRead]] = Field(default=None)
    ingresos: Optional[List[IngresoRead]] = Field(default=None)



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
        instance: Evento,
        includes: Optional[List[str]] = None,
        max_depth: int = 5,
    ) -> EventoRead:
        dto_data = {
            'id': instance.id,
            'usuario_id': instance.usuario_id,
            'id_proyecto': instance.id_proyecto,
            'nombre': instance.nombre,
            'ubicacion': instance.ubicacion,
            'tipo': instance.tipo,
            'fecha': instance.fecha,
            'hora': instance.hora,
            'estado': instance.estado,
            'notas': instance.notas,
            'created_at': instance.created_at,
            'created_by': instance.created_by,
            'updated_at': instance.updated_at,
            'updated_by': instance.updated_by,
        }

        if includes is not None and max_depth > 0:
            if should_include_relation('proyecto', includes):
                nested_includes = get_nested_includes('proyecto', includes)
                if hasattr(instance, 'proyecto') and instance.proyecto is not None:
                    dto_data['proyecto'] = ProyectoRead.from_instance(
                        instance.proyecto, nested_includes, max_depth - 1
                    )
            if should_include_relation('usuario', includes):
                nested_includes = get_nested_includes('usuario', includes)
                if hasattr(instance, 'usuario') and instance.usuario is not None:
                    dto_data['usuario'] = UsuarioRead.from_instance(
                        instance.usuario, nested_includes, max_depth - 1
                    )
            if should_include_relation('gastos', includes):
                nested_includes = get_nested_includes('gastos', includes)
                if hasattr(instance, 'gastos') and instance.gastos is not None:
                    dto_data['gastos'] = [
                        GastoRead.from_instance(reg, nested_includes, max_depth - 1) 
                        for reg in instance.gastos
                    ]
            if should_include_relation('ingresos', includes):
                nested_includes = get_nested_includes('ingresos', includes)
                if hasattr(instance, 'ingresos') and instance.ingresos is not None:
                    dto_data['ingresos'] = [
                        IngresoRead.from_instance(reg, nested_includes, max_depth - 1) 
                        for reg in instance.ingresos
                    ]
        return cls(**dto_data)

    @classmethod
    def from_created_instance(cls, instance: Evento, included: set[str], excluded: str=None) -> EventoRead:
        dto_data = {
            'id': instance.id,
            'usuario_id': instance.usuario_id,
            'id_proyecto': instance.id_proyecto,
            'nombre': instance.nombre,
            'ubicacion': instance.ubicacion,
            'tipo': instance.tipo,
            'fecha': instance.fecha,
            'hora': instance.hora,
            'estado': instance.estado,
            'notas': instance.notas,
            'created_at': instance.created_at,
            'created_by': instance.created_by,
            'updated_at': instance.updated_at,
            'updated_by': instance.updated_by,
        }
        if 'proyecto' in included and 'proyecto' != excluded:
            dto_data['proyecto'] = ProyectoRead.from_created_instance(
                instance.proyecto, included, 'eventos'
            )
        if 'usuario' in included and 'usuario' != excluded:
            dto_data['usuario'] = UsuarioRead.from_created_instance(
                instance.usuario, included, 'eventos'
            )
        if 'gastos' in included and 'gastos' != excluded:
            dto_data['gastos'] = [
                GastoRead.from_created_instance(reg, included, 'evento') 
                for reg in instance.gastos
            ]
        if 'ingresos' in included and 'ingresos' != excluded:
            dto_data['ingresos'] = [
                IngresoRead.from_created_instance(reg, included, 'evento') 
                for reg in instance.ingresos
            ]
        return cls(**dto_data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EventoRead:
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


class EventoCreate(PrettyModel):
    """DTO de escritura para Evento."""
    nombre: str
    tipo: str
    fecha: datetime
    hora: time
    usuario_id: Optional[int] = None
    id_proyecto: Optional[int] = None
    ubicacion: Optional[str] = None
    estado: str = "pendiente"
    notas: Optional[str] = None

    proyecto: Optional[ProyectoCreate] = None
    usuario: Optional[UsuarioCreate] = None
    gastos: Optional[List[GastoCreate]] = None
    ingresos: Optional[List[IngresoCreate]] = None

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
    def _anidados_sin_padre_propio(self) -> EventoCreate:
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
        _rechazar_padre_propio(self.gastos or [], 'evento', 'Gasto', 'Evento', 'gastos')
        _rechazar_padre_propio(self.ingresos or [], 'evento', 'Ingreso', 'Evento', 'ingresos')
    
    def to_instance(self) -> Evento:
        model = Evento(
            usuario_id=self.usuario_id,
            id_proyecto=self.id_proyecto,
            nombre=self.nombre,
            ubicacion=self.ubicacion,
            tipo=self.tipo,
            fecha=self.fecha,
            hora=self.hora,
            estado=self.estado,
            notas=self.notas,
        )
        model.created_by = get_username()
        model.updated_by = get_username()
        if self.proyecto is not None:
            proyecto = self.proyecto.to_instance()
            model.proyecto = proyecto
        if self.usuario is not None:
            usuario = self.usuario.to_instance()
            model.usuario = usuario
        if self.gastos is not None:
            gastos = [reg.to_instance() for reg in self.gastos]
            model.gastos = gastos
        if self.ingresos is not None:
            ingresos = [reg.to_instance() for reg in self.ingresos]
            model.ingresos = ingresos
        return model
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EventoCreate:
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True)




class EventoFilter(PrettyModel):
    """DTO de filtrado para Evento."""
    in_id: Optional[List[int]] = None
    usuario_id: Optional[int] = None
    in_usuario_id: Optional[List[int]] = None
    min_usuario_id: Optional[int] = None
    max_usuario_id: Optional[int] = None
    id_proyecto: Optional[int] = None
    in_id_proyecto: Optional[List[int]] = None
    min_id_proyecto: Optional[int] = None
    max_id_proyecto: Optional[int] = None
    nombre: Optional[str] = None
    in_nombre: Optional[List[str]] = None
    ubicacion: Optional[str] = None
    in_ubicacion: Optional[List[str]] = None
    tipo: Optional[str] = None
    in_tipo: Optional[List[str]] = None
    min_fecha: Optional[datetime] = None
    max_fecha: Optional[datetime] = None
    min_hora: Optional[time] = None
    max_hora: Optional[time] = None
    estado: Optional[str] = None
    in_estado: Optional[List[str]] = None
    notas: Optional[str] = None
    in_notas: Optional[List[str]] = None
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
            query = query.where(Evento.id.in_(self.in_id) if self.in_id else false())
        if self.usuario_id is not None:
            query = query.where(Evento.usuario_id == self.usuario_id)
        if self.in_usuario_id is not None:
            query = query.where(Evento.usuario_id.in_(self.in_usuario_id) if self.in_usuario_id else false())
        if self.min_usuario_id is not None:
            query = query.where(Evento.usuario_id >= self.min_usuario_id)
        if self.max_usuario_id is not None:
            query = query.where(Evento.usuario_id <= self.max_usuario_id)
        if self.id_proyecto is not None:
            query = query.where(Evento.id_proyecto == self.id_proyecto)
        if self.in_id_proyecto is not None:
            query = query.where(Evento.id_proyecto.in_(self.in_id_proyecto) if self.in_id_proyecto else false())
        if self.min_id_proyecto is not None:
            query = query.where(Evento.id_proyecto >= self.min_id_proyecto)
        if self.max_id_proyecto is not None:
            query = query.where(Evento.id_proyecto <= self.max_id_proyecto)
        if self.nombre is not None:
            if isinstance(self.nombre, str) and '%' in self.nombre:
                query = query.where(Evento.nombre.ilike(self.nombre))
            else:
                query = query.where(Evento.nombre == self.nombre)
        if self.in_nombre is not None:
            query = query.where(Evento.nombre.in_(self.in_nombre) if self.in_nombre else false())
        if self.ubicacion is not None:
            if isinstance(self.ubicacion, str) and '%' in self.ubicacion:
                query = query.where(Evento.ubicacion.ilike(self.ubicacion))
            else:
                query = query.where(Evento.ubicacion == self.ubicacion)
        if self.in_ubicacion is not None:
            query = query.where(Evento.ubicacion.in_(self.in_ubicacion) if self.in_ubicacion else false())
        if self.tipo is not None:
            if isinstance(self.tipo, str) and '%' in self.tipo:
                query = query.where(Evento.tipo.ilike(self.tipo))
            else:
                query = query.where(Evento.tipo == self.tipo)
        if self.in_tipo is not None:
            query = query.where(Evento.tipo.in_(self.in_tipo) if self.in_tipo else false())
        if self.min_fecha is not None:
            query = query.where(Evento.fecha >= self.min_fecha)
        if self.max_fecha is not None:
            query = query.where(Evento.fecha <= self.max_fecha)
        if self.min_hora is not None:
            query = query.where(Evento.hora >= self.min_hora)
        if self.max_hora is not None:
            query = query.where(Evento.hora <= self.max_hora)
        if self.estado is not None:
            if isinstance(self.estado, str) and '%' in self.estado:
                query = query.where(Evento.estado.ilike(self.estado))
            else:
                query = query.where(Evento.estado == self.estado)
        if self.in_estado is not None:
            query = query.where(Evento.estado.in_(self.in_estado) if self.in_estado else false())
        if self.notas is not None:
            if isinstance(self.notas, str) and '%' in self.notas:
                query = query.where(Evento.notas.ilike(self.notas))
            else:
                query = query.where(Evento.notas == self.notas)
        if self.in_notas is not None:
            query = query.where(Evento.notas.in_(self.in_notas) if self.in_notas else false())
        if self.min_created_at is not None:
            query = query.where(Evento.created_at >= self.min_created_at)
        if self.max_created_at is not None:
            query = query.where(Evento.created_at <= self.max_created_at)
        if self.created_by is not None:
            if isinstance(self.created_by, str) and '%' in self.created_by:
                query = query.where(Evento.created_by.ilike(self.created_by))
            else:
                query = query.where(Evento.created_by == self.created_by)
        if self.in_created_by is not None:
            query = query.where(Evento.created_by.in_(self.in_created_by) if self.in_created_by else false())
        if self.min_updated_at is not None:
            query = query.where(Evento.updated_at >= self.min_updated_at)
        if self.max_updated_at is not None:
            query = query.where(Evento.updated_at <= self.max_updated_at)
        if self.updated_by is not None:
            if isinstance(self.updated_by, str) and '%' in self.updated_by:
                query = query.where(Evento.updated_by.ilike(self.updated_by))
            else:
                query = query.where(Evento.updated_by == self.updated_by)
        if self.in_updated_by is not None:
            query = query.where(Evento.updated_by.in_(self.in_updated_by) if self.in_updated_by else false())

        return query



class EventoGastosNestedUpdate(PrettyModel):
    """DTO para nested writes de 'gastos' al actualizar Evento."""
    create: Optional[List[GastoCreate]] = None
    update: Optional[List[GastoUpdateNested]] = None
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
        """Un alta anidada cuelga del registro que se actualiza: no trae `evento`."""
        _rechazar_padre_propio(create or [], 'evento', 'Gasto', 'Evento', 'gastos.create')
        return create

    def _rechazar_padre_en_altas(self) -> None:
        """Lo mismo para una DTO modificada después de validarse: la llama el DAO."""
        self._altas_sin_padre_propio(self.create)

class EventoIngresosNestedUpdate(PrettyModel):
    """DTO para nested writes de 'ingresos' al actualizar Evento."""
    create: Optional[List[IngresoCreate]] = None
    update: Optional[List[IngresoUpdateNested]] = None
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
        """Un alta anidada cuelga del registro que se actualiza: no trae `evento`."""
        _rechazar_padre_propio(create or [], 'evento', 'Ingreso', 'Evento', 'ingresos.create')
        return create

    def _rechazar_padre_en_altas(self) -> None:
        """Lo mismo para una DTO modificada después de validarse: la llama el DAO."""
        self._altas_sin_padre_propio(self.create)



class EventoUpdateNested(PrettyModel):
    """DTO para actualización anidada de Evento."""
    id: int
    values: EventoUpdateValues

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



class EventoUpdateValues(PrettyModel):
    """DTO de actualización para Evento."""
    usuario_id: int = None
    id_proyecto: Optional[int] = None
    nombre: str = None
    ubicacion: Optional[str] = None
    tipo: str = None
    fecha: datetime = None
    hora: time = None
    estado: str = None
    notas: Optional[str] = None
    gastos: Optional[EventoGastosNestedUpdate] = None
    ingresos: Optional[EventoIngresosNestedUpdate] = None

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
            'gastos',
            'ingresos',
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
            nombre for nombre in ('gastos', 'ingresos',)
            if getattr(self, nombre) is not None
        ]
        if anidadas:
            raise ValueError(
                f"update_many no aplica escrituras anidadas ({', '.join(anidadas)}): un anidado "
                "nombra hijos de un registro y un update masivo no tiene uno, sino un filtro. "
                "Usa update() con la clave primaria de cada registro, o escribe los hijos con "
                "el DAO de su tabla (create_many, update_many, delete_many)."
            )



class EventoUpdate(PrettyModel):
    """DTO de actualización completo para Evento."""
    filter: EventoFilter
    values: EventoUpdateValues

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
    def _sin_escrituras_anidadas(cls, values: EventoUpdateValues) -> EventoUpdateValues:
        """Un update masivo no lleva escrituras anidadas: se rechazan, no se descartan."""
        values._rechazar_anidadas_en_masivo()
        return values



from ..proyecto.dtos import (
    ProyectoRead,
    ProyectoCreate,
    ProyectoUpdateNested,
)
from ..usuario.dtos import (
    UsuarioRead,
    UsuarioCreate,
    UsuarioUpdateNested,
)
from ..gasto.dtos import (
    GastoRead,
    GastoCreate,
    GastoUpdateNested,
)
from ..ingreso.dtos import (
    IngresoRead,
    IngresoCreate,
    IngresoUpdateNested,
)



class EventoDataFrameValidator:
    """Validador de DataFrame para el modelo Evento."""

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
            'usuario_id': {
                'type': 'int',
                'nullable': False,
                'primary_key': False,
                'autoincrement': False,
                'has_default': False
            },
            'id_proyecto': {
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
            'ubicacion': {
                'type': 'str',
                'nullable': True,
                'primary_key': False,
                'autoincrement': False,
                'has_default': False
            },
            'tipo': {
                'type': 'str',
                'nullable': False,
                'primary_key': False,
                'autoincrement': False,
                'has_default': False
            },
            'fecha': {
                'type': 'datetime',
                'nullable': False,
                'primary_key': False,
                'autoincrement': False,
                'has_default': False
            },
            'hora': {
                'type': 'time',
                'nullable': False,
                'primary_key': False,
                'autoincrement': False,
                'has_default': False
            },
            'estado': {
                'type': 'str',
                'nullable': False,
                'primary_key': False,
                'autoincrement': False,
                'has_default': True
            },
            'notas': {
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
            'usuario_id': {
                'sqlalchemy_type': 'int',
                'compatible_pandas_types': [
                    'int64', 'Int64', 'int32', 'Int32', 'int16', 'Int16', 'int8', 'Int8', 'object'
                ]
            },
            'id_proyecto': {
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
            'ubicacion': {
                'sqlalchemy_type': 'str',
                'compatible_pandas_types': [
                    'object', 'string', 'category'
                ]
            },
            'tipo': {
                'sqlalchemy_type': 'str',
                'compatible_pandas_types': [
                    'object', 'string', 'category'
                ]
            },
            'fecha': {
                'sqlalchemy_type': 'datetime',
                'compatible_pandas_types': [
                    'datetime64[ns]', 'object'
                ]
            },
            'hora': {
                'sqlalchemy_type': 'time',
                'compatible_pandas_types': [
                    'object'
                ]
            },
            'estado': {
                'sqlalchemy_type': 'str',
                'compatible_pandas_types': [
                    'object', 'string', 'category'
                ]
            },
            'notas': {
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
            'usuario_id': {
                'nullable': False,
                'autoincrement': False
            },
            'id_proyecto': {
                'nullable': True,
                'autoincrement': False
            },
            'nombre': {
                'nullable': False,
                'autoincrement': False
            },
            'ubicacion': {
                'nullable': True,
                'autoincrement': False
            },
            'tipo': {
                'nullable': False,
                'autoincrement': False
            },
            'fecha': {
                'nullable': False,
                'autoincrement': False
            },
            'hora': {
                'nullable': False,
                'autoincrement': False
            },
            'estado': {
                'nullable': False,
                'autoincrement': False
            },
            'notas': {
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
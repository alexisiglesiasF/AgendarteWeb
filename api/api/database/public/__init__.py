# Este archivo ha sido generado automáticamente por tai-sql
# No modifiques este archivo directamente

from __future__ import annotations
from typing import Optional

from ._session import (
    AsyncSessionManager,
    async_session_manager,
)
from .usuario.model import Usuario
from .usuario.dtos import *
from .usuario.dao import UsuarioAsyncDAO
from .proyecto.model import Proyecto
from .proyecto.dtos import *
from .proyecto.dao import ProyectoAsyncDAO
from .evento.model import Evento
from .evento.dtos import *
from .evento.dao import EventoAsyncDAO
from .repertorio.model import Repertorio
from .repertorio.dtos import *
from .repertorio.dao import RepertorioAsyncDAO
from .cancion.model import Cancion
from .cancion.dtos import *
from .cancion.dao import CancionAsyncDAO
from .gasto.model import Gasto
from .gasto.dtos import *
from .gasto.dao import GastoAsyncDAO
from .ingreso.model import Ingreso
from .ingreso.dtos import *
from .ingreso.dao import IngresoAsyncDAO
from ._base import TriggerAborted, NestedWriteError, NestedRowNotFound, NestedParentMismatch
from ._shared import (
    AggregationResult,
    AggRow,
    AggRequest,
    AggField,
    GroupByField,
    DatetimeTrunc,
    AggOrderBy,
    RLS,
    EnumModel,
    set_username,
    get_username,
    username_context,
)

_rebuild_ns = {k: v for k, v in globals().items()}
UsuarioRead.model_rebuild(_types_namespace=_rebuild_ns)
UsuarioCreate.model_rebuild(_types_namespace=_rebuild_ns)
UsuarioUpdateNested.model_rebuild(_types_namespace=_rebuild_ns)
UsuarioUpdateValues.model_rebuild(_types_namespace=_rebuild_ns)
UsuarioProyectosNestedUpdate.model_rebuild(_types_namespace=_rebuild_ns)
UsuarioEventosNestedUpdate.model_rebuild(_types_namespace=_rebuild_ns)
UsuarioRepertoriosNestedUpdate.model_rebuild(_types_namespace=_rebuild_ns)
ProyectoRead.model_rebuild(_types_namespace=_rebuild_ns)
ProyectoCreate.model_rebuild(_types_namespace=_rebuild_ns)
ProyectoUpdateNested.model_rebuild(_types_namespace=_rebuild_ns)
ProyectoUpdateValues.model_rebuild(_types_namespace=_rebuild_ns)
ProyectoEventosNestedUpdate.model_rebuild(_types_namespace=_rebuild_ns)
ProyectoRepertoriosNestedUpdate.model_rebuild(_types_namespace=_rebuild_ns)
EventoRead.model_rebuild(_types_namespace=_rebuild_ns)
EventoCreate.model_rebuild(_types_namespace=_rebuild_ns)
EventoUpdateNested.model_rebuild(_types_namespace=_rebuild_ns)
EventoUpdateValues.model_rebuild(_types_namespace=_rebuild_ns)
EventoGastosNestedUpdate.model_rebuild(_types_namespace=_rebuild_ns)
EventoIngresosNestedUpdate.model_rebuild(_types_namespace=_rebuild_ns)
RepertorioRead.model_rebuild(_types_namespace=_rebuild_ns)
RepertorioCreate.model_rebuild(_types_namespace=_rebuild_ns)
RepertorioUpdateNested.model_rebuild(_types_namespace=_rebuild_ns)
RepertorioUpdateValues.model_rebuild(_types_namespace=_rebuild_ns)
RepertorioCancionesNestedUpdate.model_rebuild(_types_namespace=_rebuild_ns)
CancionRead.model_rebuild(_types_namespace=_rebuild_ns)
CancionCreate.model_rebuild(_types_namespace=_rebuild_ns)
CancionUpdateNested.model_rebuild(_types_namespace=_rebuild_ns)
CancionUpdateValues.model_rebuild(_types_namespace=_rebuild_ns)
GastoRead.model_rebuild(_types_namespace=_rebuild_ns)
GastoCreate.model_rebuild(_types_namespace=_rebuild_ns)
GastoUpdateNested.model_rebuild(_types_namespace=_rebuild_ns)
GastoUpdateValues.model_rebuild(_types_namespace=_rebuild_ns)
IngresoRead.model_rebuild(_types_namespace=_rebuild_ns)
IngresoCreate.model_rebuild(_types_namespace=_rebuild_ns)
IngresoUpdateNested.model_rebuild(_types_namespace=_rebuild_ns)
IngresoUpdateValues.model_rebuild(_types_namespace=_rebuild_ns)



class PublicAsyncAPI:
    """
    API principal para operaciones de base de datos asíncronas.
    
    Proporciona acceso centralizado a todos los DAOs asíncronos.
    Los DAOs son stateless (classmethods), esta clase actúa como namespace.
    """

    _instance: Optional[PublicAsyncAPI] = None

    def __new__(cls) -> PublicAsyncAPI:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @property
    def session_manager(self) -> AsyncSessionManager:
        return async_session_manager
    
    @property
    def usuario(self):
        """Acceso a UsuarioAsyncDAO (classmethods)"""
        return UsuarioAsyncDAO

    @property
    def proyecto(self):
        """Acceso a ProyectoAsyncDAO (classmethods)"""
        return ProyectoAsyncDAO

    @property
    def evento(self):
        """Acceso a EventoAsyncDAO (classmethods)"""
        return EventoAsyncDAO

    @property
    def repertorio(self):
        """Acceso a RepertorioAsyncDAO (classmethods)"""
        return RepertorioAsyncDAO

    @property
    def cancion(self):
        """Acceso a CancionAsyncDAO (classmethods)"""
        return CancionAsyncDAO

    @property
    def gasto(self):
        """Acceso a GastoAsyncDAO (classmethods)"""
        return GastoAsyncDAO

    @property
    def ingreso(self):
        """Acceso a IngresoAsyncDAO (classmethods)"""
        return IngresoAsyncDAO

    @property
    def estado(self):
        return EnumModel(name="estado", values=['realizado', 'pendiente'])
    @property
    def tipo_evento(self):
        return EnumModel(name="tipo_evento", values=['show', 'ensayo', 'grabacion', 'otros'])


# Instancias globales
public_async_api = PublicAsyncAPI()


# Exportar
__all__ = [
    'PublicAsyncAPI',
    'public_async_api',
    'AsyncSessionManager',
    'async_session_manager',
    'set_username',
    'get_username',
    'username_context',
    'TriggerAborted',
    'NestedWriteError',
    'NestedRowNotFound',
    'NestedParentMismatch',
    'AggregationResult',
    'AggRow',
    'AggRequest',
    'AggField',
    'GroupByField',
    'DatetimeTrunc',
    'AggOrderBy',
    'RLS',
    'EnumModel',
    'Usuario',
    'UsuarioAsyncDAO',
    'UsuarioRead',
    'UsuarioFilter',
    'UsuarioCreate',
    'UsuarioUpdate',
    'UsuarioUpdateValues',
    'UsuarioUpdateNested',
    'Proyecto',
    'ProyectoAsyncDAO',
    'ProyectoRead',
    'ProyectoFilter',
    'ProyectoCreate',
    'ProyectoUpdate',
    'ProyectoUpdateValues',
    'ProyectoUpdateNested',
    'Evento',
    'EventoAsyncDAO',
    'EventoRead',
    'EventoFilter',
    'EventoCreate',
    'EventoUpdate',
    'EventoUpdateValues',
    'EventoUpdateNested',
    'Repertorio',
    'RepertorioAsyncDAO',
    'RepertorioRead',
    'RepertorioFilter',
    'RepertorioCreate',
    'RepertorioUpdate',
    'RepertorioUpdateValues',
    'RepertorioUpdateNested',
    'Cancion',
    'CancionAsyncDAO',
    'CancionRead',
    'CancionFilter',
    'CancionCreate',
    'CancionUpdate',
    'CancionUpdateValues',
    'CancionUpdateNested',
    'Gasto',
    'GastoAsyncDAO',
    'GastoRead',
    'GastoFilter',
    'GastoCreate',
    'GastoUpdate',
    'GastoUpdateValues',
    'GastoUpdateNested',
    'Ingreso',
    'IngresoAsyncDAO',
    'IngresoRead',
    'IngresoFilter',
    'IngresoCreate',
    'IngresoUpdate',
    'IngresoUpdateValues',
    'IngresoUpdateNested',
]
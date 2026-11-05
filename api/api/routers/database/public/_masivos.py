# Generado por tai-api: este fichero lo reescribe `tai-api generate`.
"""
El cuerpo de las actualizaciones masivas de `public`: `{filter, values}` sin relaciones.

`PATCH /<tabla>` actualiza **las filas que cumplen un filtro**. El `<Tabla>Update` de tai-sql lleva
en `values` el mismo `<Tabla>UpdateValues` que el `PATCH` por clave, con sus escrituras anidadas,
pero un anidado nombra los hijos de **un** registro y un masivo no tiene uno: tai-sql los rechaza en
`update_many` (#214), y antes se perdían en silencio o se aplicaban una vez por fila según la tabla.
Aquí `values` es `<Tabla>UpdateManyValues` —el mismo modelo sin las relaciones, que no admite
campos de más—, así que el OpenAPI no las anuncia y mandarlas es un 422 sobre `values`, con
cualquier versión de tai-sql. Lo usan el endpoint y `update_many` de `_tx`.
"""
from typing import Any, Dict, Tuple, Type

from pydantic import BaseModel, ConfigDict, create_model

from api.database.public import (
    UsuarioFilter,
    UsuarioUpdate,
    UsuarioUpdateValues,
    ProyectoFilter,
    ProyectoUpdate,
    ProyectoUpdateValues,
    EventoFilter,
    EventoUpdate,
    EventoUpdateValues,
    RepertorioFilter,
    RepertorioUpdate,
    RepertorioUpdateValues,
    CancionFilter,
    CancionUpdate,
    CancionUpdateValues,
    GastoFilter,
    GastoUpdate,
    GastoUpdateValues,
    IngresoFilter,
    IngresoUpdate,
    IngresoUpdateValues,
)


def _sin_relaciones(nombre: str, valores: Type[BaseModel], relaciones: Tuple[str, ...], doc: str) -> Type[BaseModel]:
    """`valores` sin los campos de sus relaciones: las columnas, con su tipo, su valor por defecto y su descripción."""
    campos: Dict[str, Any] = {
        campo: (info.annotation, info) for campo, info in valores.model_fields.items() if campo not in relaciones
    }
    return create_model(nombre, __config__=ConfigDict(**{**valores.model_config, "extra": "forbid"}), __doc__=doc, **campos)


UsuarioUpdateManyValues = _sin_relaciones(
    "UsuarioUpdateManyValues", UsuarioUpdateValues, ('proyectos', 'eventos', 'repertorios'),
    "Lo que cambia en las filas de `usuario` que cumplen el filtro: solo columnas.",
)


class UsuarioUpdateMany(BaseModel):
    """`PATCH /usuario`: las filas que cumplen `filter` toman `values`."""
    model_config = ConfigDict(extra="forbid")

    filter: UsuarioFilter
    values: UsuarioUpdateManyValues  # type: ignore[valid-type]

    def to_dao(self) -> UsuarioUpdate:
        """El `UsuarioUpdate` de tai-sql, con lo mismo que se envió."""
        return UsuarioUpdate(
            filter=self.filter,
            values=UsuarioUpdateValues(**self.values.model_dump(exclude_unset=True)),  # type: ignore[attr-defined]
        )

ProyectoUpdateManyValues = _sin_relaciones(
    "ProyectoUpdateManyValues", ProyectoUpdateValues, ('usuario', 'eventos', 'repertorios'),
    "Lo que cambia en las filas de `proyecto` que cumplen el filtro: solo columnas.",
)


class ProyectoUpdateMany(BaseModel):
    """`PATCH /proyecto`: las filas que cumplen `filter` toman `values`."""
    model_config = ConfigDict(extra="forbid")

    filter: ProyectoFilter
    values: ProyectoUpdateManyValues  # type: ignore[valid-type]

    def to_dao(self) -> ProyectoUpdate:
        """El `ProyectoUpdate` de tai-sql, con lo mismo que se envió."""
        return ProyectoUpdate(
            filter=self.filter,
            values=ProyectoUpdateValues(**self.values.model_dump(exclude_unset=True)),  # type: ignore[attr-defined]
        )

EventoUpdateManyValues = _sin_relaciones(
    "EventoUpdateManyValues", EventoUpdateValues, ('proyecto', 'usuario', 'gastos', 'ingresos'),
    "Lo que cambia en las filas de `evento` que cumplen el filtro: solo columnas.",
)


class EventoUpdateMany(BaseModel):
    """`PATCH /evento`: las filas que cumplen `filter` toman `values`."""
    model_config = ConfigDict(extra="forbid")

    filter: EventoFilter
    values: EventoUpdateManyValues  # type: ignore[valid-type]

    def to_dao(self) -> EventoUpdate:
        """El `EventoUpdate` de tai-sql, con lo mismo que se envió."""
        return EventoUpdate(
            filter=self.filter,
            values=EventoUpdateValues(**self.values.model_dump(exclude_unset=True)),  # type: ignore[attr-defined]
        )

RepertorioUpdateManyValues = _sin_relaciones(
    "RepertorioUpdateManyValues", RepertorioUpdateValues, ('canciones', 'usuario', 'proyecto'),
    "Lo que cambia en las filas de `repertorio` que cumplen el filtro: solo columnas.",
)


class RepertorioUpdateMany(BaseModel):
    """`PATCH /repertorio`: las filas que cumplen `filter` toman `values`."""
    model_config = ConfigDict(extra="forbid")

    filter: RepertorioFilter
    values: RepertorioUpdateManyValues  # type: ignore[valid-type]

    def to_dao(self) -> RepertorioUpdate:
        """El `RepertorioUpdate` de tai-sql, con lo mismo que se envió."""
        return RepertorioUpdate(
            filter=self.filter,
            values=RepertorioUpdateValues(**self.values.model_dump(exclude_unset=True)),  # type: ignore[attr-defined]
        )

CancionUpdateManyValues = _sin_relaciones(
    "CancionUpdateManyValues", CancionUpdateValues, ('repertorio',),
    "Lo que cambia en las filas de `cancion` que cumplen el filtro: solo columnas.",
)


class CancionUpdateMany(BaseModel):
    """`PATCH /cancion`: las filas que cumplen `filter` toman `values`."""
    model_config = ConfigDict(extra="forbid")

    filter: CancionFilter
    values: CancionUpdateManyValues  # type: ignore[valid-type]

    def to_dao(self) -> CancionUpdate:
        """El `CancionUpdate` de tai-sql, con lo mismo que se envió."""
        return CancionUpdate(
            filter=self.filter,
            values=CancionUpdateValues(**self.values.model_dump(exclude_unset=True)),  # type: ignore[attr-defined]
        )

GastoUpdateManyValues = _sin_relaciones(
    "GastoUpdateManyValues", GastoUpdateValues, ('evento',),
    "Lo que cambia en las filas de `gasto` que cumplen el filtro: solo columnas.",
)


class GastoUpdateMany(BaseModel):
    """`PATCH /gasto`: las filas que cumplen `filter` toman `values`."""
    model_config = ConfigDict(extra="forbid")

    filter: GastoFilter
    values: GastoUpdateManyValues  # type: ignore[valid-type]

    def to_dao(self) -> GastoUpdate:
        """El `GastoUpdate` de tai-sql, con lo mismo que se envió."""
        return GastoUpdate(
            filter=self.filter,
            values=GastoUpdateValues(**self.values.model_dump(exclude_unset=True)),  # type: ignore[attr-defined]
        )

IngresoUpdateManyValues = _sin_relaciones(
    "IngresoUpdateManyValues", IngresoUpdateValues, ('evento',),
    "Lo que cambia en las filas de `ingreso` que cumplen el filtro: solo columnas.",
)


class IngresoUpdateMany(BaseModel):
    """`PATCH /ingreso`: las filas que cumplen `filter` toman `values`."""
    model_config = ConfigDict(extra="forbid")

    filter: IngresoFilter
    values: IngresoUpdateManyValues  # type: ignore[valid-type]

    def to_dao(self) -> IngresoUpdate:
        """El `IngresoUpdate` de tai-sql, con lo mismo que se envió."""
        return IngresoUpdate(
            filter=self.filter,
            values=IngresoUpdateValues(**self.values.model_dump(exclude_unset=True)),  # type: ignore[attr-defined]
        )

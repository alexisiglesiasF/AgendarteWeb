# Este archivo ha sido generado automáticamente por tai-sql
# No modifiques este archivo directamente


from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING
from .._base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, time

from sqlalchemy import ForeignKeyConstraint


if TYPE_CHECKING:
    from ..proyecto.model import Proyecto
    from ..usuario.model import Usuario
    from ..gasto.model import Gasto
    from ..ingreso.model import Ingreso



class Evento(Base):
    """SQLAlchemy model for ``public.evento``."""

    __tablename__ = "evento"


    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    usuario_id: Mapped[int]
    id_proyecto: Mapped[Optional[int]]
    nombre: Mapped[str] = mapped_column(unique=True)
    ubicacion: Mapped[Optional[str]]
    tipo: Mapped[str]
    fecha: Mapped[datetime]
    hora: Mapped[time]
    estado: Mapped[str] = mapped_column(default="pendiente")
    notas: Mapped[Optional[str]]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    created_by: Mapped[str] = mapped_column(default="triplealpha")
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_by: Mapped[str] = mapped_column(default="triplealpha")




    proyecto: Mapped[Proyecto] = relationship(back_populates="eventos", foreign_keys="[Evento.id_proyecto]")
    usuario: Mapped[Usuario] = relationship(back_populates="eventos", foreign_keys="[Evento.usuario_id]")
    gastos: Mapped[List[Gasto]] = relationship(back_populates="evento", foreign_keys="[Gasto.id_evento]", passive_deletes="all")
    ingresos: Mapped[List[Ingreso]] = relationship(back_populates="evento", foreign_keys="[Ingreso.id_evento]", passive_deletes="all")

    __table_args__ = (
        ForeignKeyConstraint(
            ['id_proyecto'],
            ['public.proyecto.id'],
            ondelete='CASCADE',
            onupdate='CASCADE',
        ),
        ForeignKeyConstraint(
            ['usuario_id'],
            ['public.usuario.id'],
            ondelete='CASCADE',
            onupdate='CASCADE',
        ),
        {'schema': 'public'},
    )



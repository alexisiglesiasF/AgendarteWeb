# Este archivo ha sido generado automáticamente por tai-sql
# No modifiques este archivo directamente


from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING
from .._base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from sqlalchemy import ForeignKeyConstraint


if TYPE_CHECKING:
    from ..usuario.model import Usuario
    from ..evento.model import Evento
    from ..repertorio.model import Repertorio



class Proyecto(Base):
    """SQLAlchemy model for ``public.proyecto``."""

    __tablename__ = "proyecto"


    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_usuario: Mapped[int]
    nombre: Mapped[str] = mapped_column(unique=True)
    tipo: Mapped[Optional[str]]
    descripcion: Mapped[Optional[str]]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    created_by: Mapped[str] = mapped_column(default="triplealpha")
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_by: Mapped[str] = mapped_column(default="triplealpha")




    usuario: Mapped[Usuario] = relationship(back_populates="proyectos", foreign_keys="[Proyecto.id_usuario]")
    eventos: Mapped[List[Evento]] = relationship(back_populates="proyecto", foreign_keys="[Evento.id_proyecto]", passive_deletes="all")
    repertorios: Mapped[List[Repertorio]] = relationship(back_populates="proyecto", foreign_keys="[Repertorio.id_proyecto]", passive_deletes="all")

    __table_args__ = (
        ForeignKeyConstraint(
            ['id_usuario'],
            ['public.usuario.id'],
            ondelete='CASCADE',
            onupdate='CASCADE',
        ),
        {'schema': 'public'},
    )



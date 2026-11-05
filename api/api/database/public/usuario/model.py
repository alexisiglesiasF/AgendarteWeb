# Este archivo ha sido generado automáticamente por tai-sql
# No modifiques este archivo directamente


from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING
from .._base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime



if TYPE_CHECKING:
    from ..proyecto.model import Proyecto
    from ..evento.model import Evento
    from ..repertorio.model import Repertorio



class Usuario(Base):
    """SQLAlchemy model for ``public.usuario``."""

    __tablename__ = "usuario"


    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str]
    apellido: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    created_by: Mapped[str] = mapped_column(default="triplealpha")
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_by: Mapped[str] = mapped_column(default="triplealpha")




    proyectos: Mapped[List[Proyecto]] = relationship(back_populates="usuario", foreign_keys="[Proyecto.id_usuario]", passive_deletes="all")
    eventos: Mapped[List[Evento]] = relationship(back_populates="usuario", foreign_keys="[Evento.usuario_id]", passive_deletes="all")
    repertorios: Mapped[List[Repertorio]] = relationship(back_populates="usuario", foreign_keys="[Repertorio.usuario_id]", passive_deletes="all")

    __table_args__ = {'schema': 'public'}



# Este archivo ha sido generado automáticamente por tai-sql
# No modifiques este archivo directamente


from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING
from .._base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from sqlalchemy import ForeignKeyConstraint


if TYPE_CHECKING:
    from ..cancion.model import Cancion
    from ..usuario.model import Usuario
    from ..proyecto.model import Proyecto



class Repertorio(Base):
    """SQLAlchemy model for ``public.repertorio``."""

    __tablename__ = "repertorio"


    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    usuario_id: Mapped[int]
    id_proyecto: Mapped[Optional[int]]
    nombre: Mapped[str] = mapped_column(unique=True)
    descripcion: Mapped[Optional[str]]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    created_by: Mapped[str] = mapped_column(default="triplealpha")
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_by: Mapped[str] = mapped_column(default="triplealpha")




    canciones: Mapped[List[Cancion]] = relationship(back_populates="repertorio", foreign_keys="[Cancion.id_repertorio]", passive_deletes="all")
    usuario: Mapped[Usuario] = relationship(back_populates="repertorios", foreign_keys="[Repertorio.usuario_id]")
    proyecto: Mapped[Proyecto] = relationship(back_populates="repertorios", foreign_keys="[Repertorio.id_proyecto]")

    __table_args__ = (
        ForeignKeyConstraint(
            ['usuario_id'],
            ['public.usuario.id'],
            ondelete='CASCADE',
            onupdate='CASCADE',
        ),
        ForeignKeyConstraint(
            ['id_proyecto'],
            ['public.proyecto.id'],
            ondelete='CASCADE',
            onupdate='CASCADE',
        ),
        {'schema': 'public'},
    )



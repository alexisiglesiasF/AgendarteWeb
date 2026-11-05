# Este archivo ha sido generado automáticamente por tai-sql
# No modifiques este archivo directamente


from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from .._base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from sqlalchemy import ForeignKeyConstraint


if TYPE_CHECKING:
    from ..repertorio.model import Repertorio



class Cancion(Base):
    """SQLAlchemy model for ``public.cancion``."""

    __tablename__ = "cancion"


    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_repertorio: Mapped[Optional[int]]
    nombre: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    created_by: Mapped[str] = mapped_column(default="triplealpha")
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_by: Mapped[str] = mapped_column(default="triplealpha")




    repertorio: Mapped[Repertorio] = relationship(back_populates="canciones", foreign_keys="[Cancion.id_repertorio]")

    __table_args__ = (
        ForeignKeyConstraint(
            ['id_repertorio'],
            ['public.repertorio.id'],
            ondelete='CASCADE',
            onupdate='CASCADE',
        ),
        {'schema': 'public'},
    )



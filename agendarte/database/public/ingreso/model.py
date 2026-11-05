# Este archivo ha sido generado automáticamente por tai-sql
# No modifiques este archivo directamente


from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from .._base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from sqlalchemy import ForeignKeyConstraint, Numeric


if TYPE_CHECKING:
    from ..evento.model import Evento



class Ingreso(Base):
    """SQLAlchemy model for ``public.ingreso``."""

    __tablename__ = "ingreso"


    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_evento: Mapped[Optional[int]]
    nombre: Mapped[str] = mapped_column(unique=True)
    importe: Mapped[float] = mapped_column(Numeric(10, 2))
    recibido: Mapped[bool]
    concepto: Mapped[Optional[str]]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    created_by: Mapped[str] = mapped_column(default="triplealpha")
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_by: Mapped[str] = mapped_column(default="triplealpha")




    evento: Mapped[Evento] = relationship(back_populates="ingresos", foreign_keys="[Ingreso.id_evento]")

    __table_args__ = (
        ForeignKeyConstraint(
            ['id_evento'],
            ['public.evento.id'],
            ondelete='CASCADE',
            onupdate='CASCADE',
        ),
        {'schema': 'public'},
    )



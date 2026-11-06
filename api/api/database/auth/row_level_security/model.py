# Este archivo ha sido generado automáticamente por tai-sql
# No modifiques este archivo directamente


from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from .._base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from sqlalchemy import BigInteger, ForeignKeyConstraint, UniqueConstraint


if TYPE_CHECKING:
    from ..realm.model import Realm



class RowLevelSecurity(Base):
    """SQLAlchemy model for ``auth.row_level_security``."""

    __tablename__ = "row_level_security"


    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    realm_id: Mapped[int] = mapped_column(BigInteger)
    schema_name: Mapped[str]
    table_name: Mapped[str]
    column_name: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    created_by: Mapped[str] = mapped_column(default="triplealpha")
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_by: Mapped[str] = mapped_column(default="triplealpha")




    realm: Mapped[Realm] = relationship(back_populates="rls_rules", foreign_keys="[RowLevelSecurity.realm_id]")

    __table_args__ = (
        ForeignKeyConstraint(
            ['realm_id'],
            ['auth.realm.id'],
            ondelete='CASCADE',
            onupdate='CASCADE',
        ),
        UniqueConstraint('realm_id', 'schema_name', 'table_name', 'column_name', name='uq_row_level_security_cf468faa'),
        {'schema': 'auth'},
    )



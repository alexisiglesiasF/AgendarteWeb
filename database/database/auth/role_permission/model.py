# Este archivo ha sido generado automáticamente por tai-sql
# No modifiques este archivo directamente


from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from .._base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from sqlalchemy import BigInteger, ForeignKeyConstraint, UniqueConstraint


if TYPE_CHECKING:
    from ..role.model import Role
    from ..permission.model import Permission



class RolePermission(Base):
    """SQLAlchemy model for ``auth.role_permission``."""

    __tablename__ = "role_permission"


    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    role_id: Mapped[int] = mapped_column(BigInteger)
    permission_id: Mapped[int] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    created_by: Mapped[str] = mapped_column(default="triplealpha")
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_by: Mapped[str] = mapped_column(default="triplealpha")




    role: Mapped[Role] = relationship(back_populates="role_permissions", foreign_keys="[RolePermission.role_id]")
    permission: Mapped[Permission] = relationship(back_populates="role_permissions", foreign_keys="[RolePermission.permission_id]")

    __table_args__ = (
        ForeignKeyConstraint(
            ['role_id'],
            ['auth.role.id'],
            ondelete='CASCADE',
            onupdate='CASCADE',
        ),
        ForeignKeyConstraint(
            ['permission_id'],
            ['auth.permission.id'],
            ondelete='CASCADE',
            onupdate='CASCADE',
        ),
        UniqueConstraint('role_id', 'permission_id', name='uq_role_permission_role_id_permission_id'),
        {'schema': 'auth'},
    )



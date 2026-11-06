# Este archivo ha sido generado automáticamente por tai-sql
# No modifiques este archivo directamente


from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from .._base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from uuid import UUID

from sqlalchemy import BigInteger, ForeignKeyConstraint, UniqueConstraint, Uuid


if TYPE_CHECKING:
    from ..user.model import User
    from ..role.model import Role



class UserRole(Base):
    """SQLAlchemy model for ``auth.user_role``."""

    __tablename__ = "user_role"


    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[UUID] = mapped_column(Uuid)
    role_id: Mapped[int] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    created_by: Mapped[str] = mapped_column(default="triplealpha")
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_by: Mapped[str] = mapped_column(default="triplealpha")




    user: Mapped[User] = relationship(back_populates="user_roles", foreign_keys="[UserRole.user_id]")
    role: Mapped[Role] = relationship(back_populates="user_roles", foreign_keys="[UserRole.role_id]")

    __table_args__ = (
        ForeignKeyConstraint(
            ['user_id'],
            ['auth.user.id'],
            ondelete='CASCADE',
            onupdate='CASCADE',
        ),
        ForeignKeyConstraint(
            ['role_id'],
            ['auth.role.id'],
            ondelete='CASCADE',
            onupdate='CASCADE',
        ),
        UniqueConstraint('user_id', 'role_id', name='uq_user_role_user_id_role_id'),
        {'schema': 'auth'},
    )



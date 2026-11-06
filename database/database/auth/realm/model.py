# Este archivo ha sido generado automáticamente por tai-sql
# No modifiques este archivo directamente


from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING
from .._base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from sqlalchemy import BigInteger


if TYPE_CHECKING:
    from ..user.model import User
    from ..role.model import Role
    from ..permission.model import Permission
    from ..row_level_security.model import RowLevelSecurity



class Realm(Base):
    """SQLAlchemy model for ``auth.realm``."""

    __tablename__ = "realm"


    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[Optional[str]]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    created_by: Mapped[str] = mapped_column(default="triplealpha")
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_by: Mapped[str] = mapped_column(default="triplealpha")




    users: Mapped[List[User]] = relationship(back_populates="realm", foreign_keys="[User.realm_id]", passive_deletes="all")
    roles: Mapped[List[Role]] = relationship(back_populates="realm", foreign_keys="[Role.realm_id]", passive_deletes="all")
    permissions: Mapped[List[Permission]] = relationship(back_populates="realm", foreign_keys="[Permission.realm_id]", passive_deletes="all")
    rls_rules: Mapped[List[RowLevelSecurity]] = relationship(back_populates="realm", foreign_keys="[RowLevelSecurity.realm_id]", passive_deletes="all")

    __table_args__ = {'schema': 'auth'}



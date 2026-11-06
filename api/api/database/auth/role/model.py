# Este archivo ha sido generado automáticamente por tai-sql
# No modifiques este archivo directamente


from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING
from .._base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Dict, Any

from sqlalchemy import BigInteger, ForeignKeyConstraint, JSON, UniqueConstraint


if TYPE_CHECKING:
    from ..realm.model import Realm
    from ..role_permission.model import RolePermission
    from ..user_role.model import UserRole



class Role(Base):
    """SQLAlchemy model for ``auth.role``."""

    __tablename__ = "role"


    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str]
    realm_id: Mapped[int] = mapped_column(BigInteger)
    description: Mapped[Optional[str]]
    attributes: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    parent_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    created_by: Mapped[str] = mapped_column(default="triplealpha")
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_by: Mapped[str] = mapped_column(default="triplealpha")




    realm: Mapped[Realm] = relationship(back_populates="roles", foreign_keys="[Role.realm_id]")
    parent: Mapped[Role] = relationship(back_populates="subroles", foreign_keys="[Role.parent_id]", remote_side="[Role.id]")
    subroles: Mapped[List[Role]] = relationship(back_populates="parent", foreign_keys="[Role.parent_id]", passive_deletes="all")
    role_permissions: Mapped[List[RolePermission]] = relationship(back_populates="role", foreign_keys="[RolePermission.role_id]", passive_deletes="all")
    user_roles: Mapped[List[UserRole]] = relationship(back_populates="role", foreign_keys="[UserRole.role_id]", passive_deletes="all")

    __table_args__ = (
        ForeignKeyConstraint(
            ['realm_id'],
            ['auth.realm.id'],
            ondelete='CASCADE',
            onupdate='CASCADE',
        ),
        ForeignKeyConstraint(
            ['parent_id'],
            ['auth.role.id'],
            ondelete='RESTRICT',
            onupdate='CASCADE',
        ),
        UniqueConstraint('name', 'realm_id', name='uq_role_name_realm_id'),
        {'schema': 'auth'},
    )



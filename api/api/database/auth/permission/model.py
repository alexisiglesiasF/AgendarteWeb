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



class Permission(Base):
    """SQLAlchemy model for ``auth.permission``."""

    __tablename__ = "permission"


    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str]
    realm_id: Mapped[int] = mapped_column(BigInteger)
    description: Mapped[Optional[str]]
    type: Mapped[str]
    attributes: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    created_by: Mapped[str] = mapped_column(default="triplealpha")
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_by: Mapped[str] = mapped_column(default="triplealpha")




    realm: Mapped[Realm] = relationship(back_populates="permissions", foreign_keys="[Permission.realm_id]")
    role_permissions: Mapped[List[RolePermission]] = relationship(back_populates="permission", foreign_keys="[RolePermission.permission_id]", passive_deletes="all")

    __table_args__ = (
        ForeignKeyConstraint(
            ['realm_id'],
            ['auth.realm.id'],
            ondelete='CASCADE',
            onupdate='CASCADE',
        ),
        UniqueConstraint('name', 'realm_id', name='uq_permission_name_realm_id'),
        {'schema': 'auth'},
    )



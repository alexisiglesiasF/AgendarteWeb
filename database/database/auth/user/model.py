# Este archivo ha sido generado automáticamente por tai-sql
# No modifiques este archivo directamente


from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING
from .._base import Base, hash_value, verify_hash
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Dict, Any
from uuid import UUID

from sqlalchemy import BigInteger, FetchedValue, ForeignKeyConstraint, JSON, UniqueConstraint, Uuid
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import event


if TYPE_CHECKING:
    from ..realm.model import Realm
    from ..user_role.model import UserRole



class User(Base):
    """SQLAlchemy model for ``auth.user``."""

    __tablename__ = "user"

    def __init__(self, **kwargs):
        if 'password' in kwargs:
            password_value = kwargs.pop('password')
            self.password = password_value
        kwargs.pop('full_name', None)
        super().__init__(**kwargs)
        self._recompute_full_name()

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, server_default=FetchedValue())
    username: Mapped[str]
    realm_id: Mapped[int] = mapped_column(BigInteger)
    first_name: Mapped[Optional[str]]
    last_name: Mapped[Optional[str]]
    _password: Mapped[str] = mapped_column(name="password")
    email: Mapped[Optional[str]]
    is_active: Mapped[bool] = mapped_column(default=True)
    session_id: Mapped[Optional[str]]
    refresh_generation: Mapped[Optional[int]]
    refresh_rotated_at: Mapped[Optional[datetime]]
    password_expiration: Mapped[Optional[datetime]]
    attributes: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    _full_name: Mapped[Optional[str]] = mapped_column(name="full_name")
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    created_by: Mapped[str] = mapped_column(default="triplealpha")
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_by: Mapped[str] = mapped_column(default="triplealpha")



    @hybrid_property
    def password(self) -> Optional[str]:
        """El hash almacenado. El valor original no existe: usa `verify_password()`."""
        return self._password

    @password.setter
    def password(self, value: Optional[str]):
        """Hashea al asignar. Asignar un hash ya calculado lo volvería a hashear."""
        if value is None:
            self._password = None
        else:
            self._password = hash_value(str(value))

    def verify_password(self, value: Optional[str]) -> bool:
        """True si `value` coincide con lo almacenado en esta fila."""
        return verify_hash(value, self._password)


    @hybrid_property
    def full_name(self) -> Optional[str]:
        return self._full_name

    @full_name.setter
    def full_name(self, value: Optional[str]):
        self._full_name = value

    @full_name.expression
    def full_name(cls):
        return cls._full_name

    def _recompute_full_name(self):
        """Recompute calculated column ``full_name``."""
        self._full_name = f"{self.first_name or ''} {self.last_name or ''}".strip() if self.first_name or self.last_name else None

    realm: Mapped[Realm] = relationship(back_populates="users", foreign_keys="[User.realm_id]")
    user_roles: Mapped[List[UserRole]] = relationship(back_populates="user", foreign_keys="[UserRole.user_id]", passive_deletes="all")

    __table_args__ = (
        ForeignKeyConstraint(
            ['realm_id'],
            ['auth.realm.id'],
            ondelete='CASCADE',
            onupdate='CASCADE',
        ),
        UniqueConstraint('username', 'realm_id', name='uq_user_username_realm_id'),
        {'schema': 'auth'},
    )



@event.listens_for(User, 'before_insert')
@event.listens_for(User, 'before_update')
def _recompute_user_calculated(mapper, connection, target: User):
    """Recompute all calculated columns before insert/update."""
    target._recompute_full_name()

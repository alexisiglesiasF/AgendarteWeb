# Este archivo ha sido generado automáticamente por tai-sql
# No modifiques este archivo directamente

from __future__ import annotations
from typing import Optional

from ._session import (
    AsyncSessionManager,
    async_session_manager,
)
from .realm.model import Realm
from .realm.dtos import *
from .realm.dao import RealmAsyncDAO
from .user.model import User
from .user.dtos import *
from .user.dao import UserAsyncDAO
from .role.model import Role
from .role.dtos import *
from .role.dao import RoleAsyncDAO
from .permission.model import Permission
from .permission.dtos import *
from .permission.dao import PermissionAsyncDAO
from .user_role.model import UserRole
from .user_role.dtos import *
from .user_role.dao import UserRoleAsyncDAO
from .role_permission.model import RolePermission
from .role_permission.dtos import *
from .role_permission.dao import RolePermissionAsyncDAO
from .row_level_security.model import RowLevelSecurity
from .row_level_security.dtos import *
from .row_level_security.dao import RowLevelSecurityAsyncDAO
from ._base import TriggerAborted, NestedWriteError, NestedRowNotFound, NestedParentMismatch
from ._shared import (
    AggregationResult,
    AggRow,
    AggRequest,
    AggField,
    GroupByField,
    DatetimeTrunc,
    AggOrderBy,
    RLS,
    EnumModel,
    set_username,
    get_username,
    username_context,
)

_rebuild_ns = {k: v for k, v in globals().items()}
RealmRead.model_rebuild(_types_namespace=_rebuild_ns)
RealmCreate.model_rebuild(_types_namespace=_rebuild_ns)
RealmUpdateNested.model_rebuild(_types_namespace=_rebuild_ns)
RealmUpdateValues.model_rebuild(_types_namespace=_rebuild_ns)
RealmUsersNestedUpdate.model_rebuild(_types_namespace=_rebuild_ns)
RealmRolesNestedUpdate.model_rebuild(_types_namespace=_rebuild_ns)
RealmPermissionsNestedUpdate.model_rebuild(_types_namespace=_rebuild_ns)
RealmRls_rulesNestedUpdate.model_rebuild(_types_namespace=_rebuild_ns)
UserRead.model_rebuild(_types_namespace=_rebuild_ns)
UserCreate.model_rebuild(_types_namespace=_rebuild_ns)
UserUpdateNested.model_rebuild(_types_namespace=_rebuild_ns)
UserUpdateValues.model_rebuild(_types_namespace=_rebuild_ns)
UserUser_rolesNestedUpdate.model_rebuild(_types_namespace=_rebuild_ns)
RoleRead.model_rebuild(_types_namespace=_rebuild_ns)
RoleCreate.model_rebuild(_types_namespace=_rebuild_ns)
RoleUpdateNested.model_rebuild(_types_namespace=_rebuild_ns)
RoleUpdateValues.model_rebuild(_types_namespace=_rebuild_ns)
RoleSubrolesNestedUpdate.model_rebuild(_types_namespace=_rebuild_ns)
RoleRole_permissionsNestedUpdate.model_rebuild(_types_namespace=_rebuild_ns)
RoleUser_rolesNestedUpdate.model_rebuild(_types_namespace=_rebuild_ns)
PermissionRead.model_rebuild(_types_namespace=_rebuild_ns)
PermissionCreate.model_rebuild(_types_namespace=_rebuild_ns)
PermissionUpdateNested.model_rebuild(_types_namespace=_rebuild_ns)
PermissionUpdateValues.model_rebuild(_types_namespace=_rebuild_ns)
PermissionRole_permissionsNestedUpdate.model_rebuild(_types_namespace=_rebuild_ns)
UserRoleRead.model_rebuild(_types_namespace=_rebuild_ns)
UserRoleCreate.model_rebuild(_types_namespace=_rebuild_ns)
UserRoleUpdateNested.model_rebuild(_types_namespace=_rebuild_ns)
UserRoleUpdateValues.model_rebuild(_types_namespace=_rebuild_ns)
RolePermissionRead.model_rebuild(_types_namespace=_rebuild_ns)
RolePermissionCreate.model_rebuild(_types_namespace=_rebuild_ns)
RolePermissionUpdateNested.model_rebuild(_types_namespace=_rebuild_ns)
RolePermissionUpdateValues.model_rebuild(_types_namespace=_rebuild_ns)
RowLevelSecurityRead.model_rebuild(_types_namespace=_rebuild_ns)
RowLevelSecurityCreate.model_rebuild(_types_namespace=_rebuild_ns)
RowLevelSecurityUpdateNested.model_rebuild(_types_namespace=_rebuild_ns)
RowLevelSecurityUpdateValues.model_rebuild(_types_namespace=_rebuild_ns)



class AuthAsyncAPI:
    """
    API principal para operaciones de base de datos asíncronas.
    
    Proporciona acceso centralizado a todos los DAOs asíncronos.
    Los DAOs son stateless (classmethods), esta clase actúa como namespace.
    """

    _instance: Optional[AuthAsyncAPI] = None

    def __new__(cls) -> AuthAsyncAPI:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @property
    def session_manager(self) -> AsyncSessionManager:
        return async_session_manager
    
    @property
    def realm(self):
        """Acceso a RealmAsyncDAO (classmethods)"""
        return RealmAsyncDAO

    @property
    def user(self):
        """Acceso a UserAsyncDAO (classmethods)"""
        return UserAsyncDAO

    @property
    def role(self):
        """Acceso a RoleAsyncDAO (classmethods)"""
        return RoleAsyncDAO

    @property
    def permission(self):
        """Acceso a PermissionAsyncDAO (classmethods)"""
        return PermissionAsyncDAO

    @property
    def user_role(self):
        """Acceso a UserRoleAsyncDAO (classmethods)"""
        return UserRoleAsyncDAO

    @property
    def role_permission(self):
        """Acceso a RolePermissionAsyncDAO (classmethods)"""
        return RolePermissionAsyncDAO

    @property
    def row_level_security(self):
        """Acceso a RowLevelSecurityAsyncDAO (classmethods)"""
        return RowLevelSecurityAsyncDAO

    @property
    def permission_type(self):
        return EnumModel(name="permission_type", values=['api', 'app'])


# Instancias globales
auth_async_api = AuthAsyncAPI()


# Exportar
__all__ = [
    'AuthAsyncAPI',
    'auth_async_api',
    'AsyncSessionManager',
    'async_session_manager',
    'set_username',
    'get_username',
    'username_context',
    'TriggerAborted',
    'NestedWriteError',
    'NestedRowNotFound',
    'NestedParentMismatch',
    'AggregationResult',
    'AggRow',
    'AggRequest',
    'AggField',
    'GroupByField',
    'DatetimeTrunc',
    'AggOrderBy',
    'RLS',
    'EnumModel',
    'Realm',
    'RealmAsyncDAO',
    'RealmRead',
    'RealmFilter',
    'RealmCreate',
    'RealmUpdate',
    'RealmUpdateValues',
    'RealmUpdateNested',
    'User',
    'UserAsyncDAO',
    'UserRead',
    'UserFilter',
    'UserCreate',
    'UserUpdate',
    'UserUpdateValues',
    'UserUpdateNested',
    'Role',
    'RoleAsyncDAO',
    'RoleRead',
    'RoleFilter',
    'RoleCreate',
    'RoleUpdate',
    'RoleUpdateValues',
    'RoleUpdateNested',
    'Permission',
    'PermissionAsyncDAO',
    'PermissionRead',
    'PermissionFilter',
    'PermissionCreate',
    'PermissionUpdate',
    'PermissionUpdateValues',
    'PermissionUpdateNested',
    'UserRole',
    'UserRoleAsyncDAO',
    'UserRoleRead',
    'UserRoleFilter',
    'UserRoleCreate',
    'UserRoleUpdate',
    'UserRoleUpdateValues',
    'UserRoleUpdateNested',
    'RolePermission',
    'RolePermissionAsyncDAO',
    'RolePermissionRead',
    'RolePermissionFilter',
    'RolePermissionCreate',
    'RolePermissionUpdate',
    'RolePermissionUpdateValues',
    'RolePermissionUpdateNested',
    'RowLevelSecurity',
    'RowLevelSecurityAsyncDAO',
    'RowLevelSecurityRead',
    'RowLevelSecurityFilter',
    'RowLevelSecurityCreate',
    'RowLevelSecurityUpdate',
    'RowLevelSecurityUpdateValues',
    'RowLevelSecurityUpdateNested',
]
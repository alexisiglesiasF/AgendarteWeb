from .model import Permission

__all__ = [
    'Permission',
    'PermissionSyncDAO',
    'PermissionAsyncDAO',
    'PermissionRead',
    'PermissionFilter',
    'PermissionCreate',
    'PermissionUpdateNested',
    'PermissionUpdateValues',
    'PermissionUpdate',
]


def __getattr__(name: str):
    """Lazy import DAOs and DTOs to avoid circular imports."""
    from . import dtos, dao_sync, dao_async
    for mod in (dtos, dao_sync, dao_async):
        try:
            val = getattr(mod, name)
            globals()[name] = val
            return val
        except AttributeError:
            continue
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
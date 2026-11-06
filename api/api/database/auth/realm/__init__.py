from .model import Realm

__all__ = [
    'Realm',
    'RealmAsyncDAO',
    'RealmRead',
    'RealmFilter',
    'RealmCreate',
    'RealmUpdateNested',
    'RealmUpdateValues',
    'RealmUpdate',
]


def __getattr__(name: str):
    """Lazy import DAOs and DTOs to avoid circular imports."""
    from . import dtos, dao
    for mod in (dtos, dao):
        try:
            val = getattr(mod, name)
            globals()[name] = val
            return val
        except AttributeError:
            continue
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
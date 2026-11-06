from .model import User

__all__ = [
    'User',
    'UserAsyncDAO',
    'UserRead',
    'UserFilter',
    'UserCreate',
    'UserUpdateNested',
    'UserUpdateValues',
    'UserUpdate',
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
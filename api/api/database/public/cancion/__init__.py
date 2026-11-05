from .model import Cancion

__all__ = [
    'Cancion',
    'CancionAsyncDAO',
    'CancionRead',
    'CancionFilter',
    'CancionCreate',
    'CancionUpdateNested',
    'CancionUpdateValues',
    'CancionUpdate',
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
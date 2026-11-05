# Este archivo ha sido generado automáticamente por tai-sql
# No modifiques este archivo directamente

from __future__ import annotations
from contextvars import ContextVar, Token
from contextlib import contextmanager
from typing import Generator

_current_username: ContextVar[str] = ContextVar('_current_username', default='triplealpha')


def set_username(username: str) -> None:
    """
    Establece el nombre de usuario para auditoría en el contexto actual.

    Thread-safe y async-safe: cada thread/task mantiene su propio valor.
    En un entorno web (FastAPI, Flask, etc.), llamar a esta función en
    middleware garantiza que cada request use su propio usuario.

    Args:
        username: Nombre de usuario a establecer.
    """
    _current_username.set(username)


def get_username() -> str:
    """
    Obtiene el nombre de usuario del contexto actual.

    Returns:
        El username configurado para este contexto (default: 'triplealpha').
    """
    return _current_username.get()


@contextmanager
def username_context(username: str) -> Generator[None, None, None]:
    """
    Context manager para establecer temporalmente un username.

    Al salir del bloque, el valor anterior se restaura automáticamente.
    Útil para operaciones puntuales con un usuario distinto al del contexto.

    Ejemplo:
        ```python
        set_username("alice")
        # ... operaciones con alice ...

        with username_context("system"):
            # operaciones internas con "system"
            ...
        # aquí vuelve a ser "alice"
        ```
    """
    token: Token[str] = _current_username.set(username)
    try:
        yield
    finally:
        _current_username.reset(token)
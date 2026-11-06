# Este archivo ha sido generado automáticamente por tai-sql
# No modifiques este archivo directamente

from __future__ import annotations
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import DeclarativeBase
import bcrypt


class Base(DeclarativeBase):
    pass


class TriggerAborted(ValueError):
    """
    Un trigger del schema ha detenido la operación con `t.abort(mensaje)`.

    Es una regla de negocio que no se cumple, no un fallo: quien la reciba tiene que poder
    decírselo al usuario tal cual. `message` es el texto que escribió el trigger, sin prefijo.

    Hereda de `ValueError` porque es lo que se lanzaba antes, y el código que ya la captura
    así sigue funcionando.
    """

    #: Para reconocerla sin importar la clase: tai-api atiende a los clientes de varios schemas
    #: con un solo manejador, y cada uno tiene la suya.
    tai_trigger_abort = True

    def __init__(self, message: str):
        self.message = message
        super().__init__(f"Trigger abortado: {message}")


class NestedWriteError(Exception):
    """
    Una escritura anidada del `update` no se puede aplicar al registro que se actualiza.

    Un anidado nombra hijos **de ese registro**: los crea colgando de él, o los actualiza y
    los borra por su clave. Lo que no casa con eso no se ignora —hasta 0.7.21 un hijo que
    no se encontraba se saltaba sin error— y se lanza una de sus dos subclases. La
    transacción se deshace entera: ni el padre ni los demás hijos quedan escritos.

    - `message`: el texto para quien hizo la petición, con la solución.
    - `field`: dónde está en el payload, con la forma del JSON (`resenas.delete.0`,
      `libros.update.0.values.resenas.update.1`; en una uno a uno, sin índice). Lo
      construye cada nivel al subir, así que es la ruta completa desde el registro raíz.
    - `table`: la tabla del hijo. `key`: su clave, tal como llegó.
    - `reason`: `'not_found'` o `'parent_mismatch'`.
    """

    #: Para reconocerla sin importar la clase, como `tai_trigger_abort`: tai-api atiende a
    #: los clientes de varios schemas con un solo manejador, y cada uno tiene la suya.
    tai_nested_write = True
    reason: str = ''

    def __init__(self, message: str, *, field: str, table: str, key=None):
        self.message = message
        self.field = field
        self.table = table
        self.key = key
        super().__init__(message)

    def _under(self, prefix: str) -> 'NestedWriteError':
        """La misma excepción, vista desde el padre: antepone su tramo a `field`."""
        self.field = f'{prefix}.{self.field}'
        return self


class NestedRowNotFound(NestedWriteError, LookupError):
    """
    Un `update` o `delete` anidado nombra una fila que no está bajo el registro que se
    actualiza: no existe, cuelga de otro padre o la regla de RLS no la alcanza.

    Los tres casos son el mismo a propósito —para quien llama, esa fila no es hija de este
    registro— y distinguirlos delataría filas que la regla oculta. Es lo que tai-api
    responde con un 404.
    """

    reason = 'not_found'


class NestedParentMismatch(NestedWriteError, ValueError):
    """
    Un `update` anidado cambia las columnas que unen el hijo con su padre: lo sacaría del
    registro bajo el que se ha nombrado. Para mover una fila de padre se usa el DAO de su
    tabla. Es una petición inválida (un 422 en tai-api), no una fila que falte.
    """

    reason = 'parent_mismatch'


# ── Hashing ──────────────────────────────────────────────────────────────────
#
# Distinto del cifrado de arriba y no intercambiable: esto es de ida. El valor original
# no queda en ninguna parte, así que no se puede leer — solo comprobar si un candidato
# coincide. No lleva clave: el salt va dentro del propio hash, y por eso dos filas con
# el mismo valor guardan textos distintos.

def hash_value(value: str) -> str:
    """Hashea un valor. Devuelve None si el valor es None."""
    if value is None:
        return None
    return bcrypt.hashpw(value.encode(), bcrypt.gensalt()).decode()


#: Un hash bcrypt válido, del mismo coste que `gensalt()` por defecto (12), que no
#: corresponde a nada. Sirve para comprobar un candidato cuando la fila no existe: sin
#: él, «no existe» respondía al instante y «no coincide» tras el bcrypt (~200 ms), y esa
#: diferencia basta para averiguar desde fuera qué usuarios hay. Si algún día se sube el
#: coste de `gensalt()`, hay que regenerarlo con el mismo.
HASH_DE_RELLENO = "$2b$12$diGTNtGT.nEOuDdpfJHsD.4nO.d3Pk41jUWW9/OizA//1Aa3So30S"


def verify_hash(value: str, hashed: str) -> bool:
    """
    Comprueba si un valor corresponde a un hash.

    Devuelve False ante cualquier entrada que no sea comparable —None, o un hash con un
    formato que bcrypt no reconoce, como el de una fila que aún no se ha migrado— en vez
    de propagar la excepción: quien pregunta esto está autenticando, y un error ahí es un
    «no» y no una caída.
    """
    if value is None or hashed is None:
        return False
    try:
        return bcrypt.checkpw(value.encode(), hashed.encode())
    except (ValueError, TypeError):
        return False


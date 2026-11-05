# Generado por tai-api: este fichero lo reescribe `tai-api generate`.
"""
Los filtros que llegan **en el cuerpo** de una petición de `public`: el `filter` de
`PATCH /<tabla>` y de `update_many`/`delete_many` en `_tx`, y el `filters` de `POST /<tabla>/agg`.

**Un `in_<campo>` con la lista vacía no casa con ninguna fila.** Es lo que dice el filtro —«que
`<campo>` sea uno de estos cero valores»—, pero el DAO de tai-sql (hasta 0.7.21) trata la lista
vacía como «sin filtro» y no filtra por esa columna. Y la comprobación de filtro vacío de los
masivos no lo para, porque hay una clave. Sin esto, `{"filter": {"in_x": []}, "values": …}`
actualizaba **todas** las filas que alcanza el usuario sin pedir `confirm_all`, y una agregación
con `{"filters": {"in_x": []}}` contaba la tabla entera en vez de nada.

- **En una escritura masiva**, el endpoint responde 0 **sin llamar al DAO**: no se escribe nada, con
  cualquier versión de tai-sql.
- **En una agregación**, se llama al DAO con una regla más que no alcanza ninguna fila (`RLS` con
  la lista vacía, que el DAO traduce a `WHERE false`). La respuesta es exactamente la de un filtro
  que no casa con nada —una fila con `count_* = 0` y lo demás `null` sin `group_by`, ninguna con
  él, y los mismos `meta`—, y la operación se valida igual: una que no se puede aplicar sigue
  siendo un 422.

En la query string no pasa: una lista vacía no viaja (`?in_x=` es `[""]`).
"""
from typing import Any, Dict, List, Optional

from api.database.public import RLS
from api.database.public._shared import get_model_by_name


def con_in_vacio(filtro: Optional[Dict[str, Any]]) -> Optional[str]:
    """El primer `in_<campo>` del filtro con la lista vacía, o `None` si no tiene ninguno."""
    for clave, valor in (filtro or {}).items():
        if clave.startswith("in_") and isinstance(valor, (list, tuple, set)) and len(valor) == 0:
            return clave
    return None


def sin_filas(tabla: str, filtro: Optional[Dict[str, Any]], reglas: Optional[List[Any]]) -> Optional[List[Any]]:
    """
    Las reglas con que leer `tabla`: `reglas`, y si el filtro lleva un `in_` vacío, una más que
    no alcanza ninguna fila. Es la de una lectura con el filtro (`agg`); una escritura no llama al
    DAO (`con_in_vacio`).
    """
    campo = con_in_vacio(filtro)
    if campo is None:
        return reglas
    ninguna = RLS(
        target_model=get_model_by_name(f"public.{tabla}"),
        target_column=campo[len("in_"):],
        values=[],
    )
    return [*(reglas or []), ninguna]
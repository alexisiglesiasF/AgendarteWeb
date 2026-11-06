# Generado por tai-api: este fichero lo reescribe `tai-api generate`.
"""
agendarte-api - RBAC Models
Generado automáticamente por tai-api auth init

Modelos Pydantic unificados para la API de gestión RBAC.
Independientes del backend de autenticación (Database / Keycloak).
"""
from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Any, Dict, Optional, List

#: Lo que guarda Keycloak por «cero valores». Una regla RLS distingue dos cosas que Keycloak no:
#:
#: - `null`: **no aplica**. El usuario no tiene el atributo y la regla no le filtra.
#: - `[]`: **cero valores**. La regla aplica y no ve ninguna fila.
#:
#: Keycloak no guarda un atributo vacío —lo borra—, así que `[]` se convertía en «no aplica» y el
#: usuario veía todo. En su lugar se guarda este valor, que `build_rls_rules` y la lectura de
#: `/rbac` vuelven a traducir a `[]`. En modo Database se guarda `[]` tal cual.
RLS_SIN_VALORES = "__tai_api:sin_valores__"


def rls_valores(valores: Any) -> Optional[List[Any]]:
    """Un valor de regla tal como lo guarda el backend → `None` (no aplica), `[]` (cero) o sus valores."""
    if valores is None:
        return None
    lista = list(valores) if isinstance(valores, (list, tuple, set)) else [valores]
    return [v for v in lista if v != RLS_SIN_VALORES]


class RBACUserCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    username: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    is_active: bool = True
    roles: List[str] = []
    # Cada regla RLS: `null` u omitida, no aplica; `[]`, cero valores (no ve nada); o sus valores.

    @property
    def attributes(self) -> Dict[str, Any]:
        """
        Los atributos de las reglas que aplican. Una lista vacía **se guarda**: es «cero valores», no
        «sin regla». Antes se descartaba, y un usuario dado de alta con `[]` lo veía todo.
        """
        attrs: Dict[str, Any] = {}
        return attrs


class RBACUserUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    roles: Optional[List[str]] = None

    @property
    def attributes(self) -> Optional[Dict[str, Any]]:
        """
        Los cambios de las reglas RLS, con tres estados por regla:

        - **omitida**: no se toca;
        - **`null`**: deja de aplicar (se quita el atributo);
        - **`[]` o valores**: se guardan; `[]` es «cero valores».

        `None` si no se toca ninguna. Antes `null` y omitida eran lo mismo, y una regla con valores
        no se podía volver a «no aplica».
        """
        attrs: Dict[str, Any] = {}
        return attrs or None


class RBACUser(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    is_active: bool = True
    roles: List[str] = []
    # `null`: la regla no aplica a este usuario; `[]`: aplica con cero valores (no ve nada).

    @model_validator(mode="before")
    @classmethod
    def _extract_rls_from_attributes(cls, data: Any) -> Any:
        """Extrae campos RLS del dict attributes al nivel superior del modelo."""
        if isinstance(data, dict):
            attributes = data.pop("attributes", None) or {}
        return data


class RBACRoleInfo(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: List[str] = []
    parent_role_name: Optional[str] = None


class RBACRLS(BaseModel):
    target_schema: str
    target_model: str
    target_field: str
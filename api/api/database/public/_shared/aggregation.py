# Este archivo ha sido generado automáticamente por tai-sql
# No modifiques este archivo directamente

from __future__ import annotations
import re
from datetime import date, time
from enum import Enum
from typing import (
    List,
    Optional,
    Dict,
    Literal,
    Any,
    Union,
)
from pydantic import Field
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy.sql.elements import ColumnElement
from tai_alphi import Alphi

from .utils import PrettyModel

# Logger
logger = Alphi.get_logger_by_name("agendarte-api")

# General Enum class
class EnumModel:

    def __init__(self, name: str, values: List[str]):
        self.name = name
        self.values = values
    
    def find_many(self) -> List[str]:
        """
        Devuelve una lista de los valores del Enum.
        
        Returns:
            List[str]: Lista de valores del Enum
        """
        logger.info(f"Obteniendo valores del Enum '{self.name}' - {len(self.values)} valores disponibles")
        return self.values


class DatetimeTrunc(str, Enum):
    """
    Nivel de truncación temporal para GROUP BY sobre campos DATETIME/TIMESTAMP.

    Se aplica mediante DATE_TRUNC o DATE_BIN en la consulta SQL.
    La clave resultante en AggRow.group sigue el patrón
    '<campo>_<trunc>' (ej: 'created_at_month', 'created_at_30min').

    Valores estándar (DATE_TRUNC): year, quarter, month, week, day, hour, minute.
    Intervalos personalizados (DATE_BIN): 15min, 30min, 3h, 6h, 12h.
    """

    year    = "year"
    quarter = "quarter"
    month   = "month"
    week    = "week"
    day     = "day"
    h12     = "12h"
    h6      = "6h"
    h3      = "3h"
    hour    = "hour"
    min30   = "30min"
    min15   = "15min"
    minute  = "minute"


class GroupByField(PrettyModel):
    """
    Definición de un campo de agrupación para el método agg.

    Para campos DATETIME o TIMESTAMP el atributo trunc es obligatorio; de lo
    contrario la consulta agruparía por timestamp exacto, lo que rara vez es
    útil y produce un grupo por registro. En cualquier otro tipo es un error:
    ignorarlo agruparía por otra cosa de la que se pidió.
    Los campos de tipo FLOAT, DOUBLE, DECIMAL, NUMERIC y REAL están prohibidos
    porque son tipos continuos que generan grupos de cardinalidad altísima.

    Examples:
        ```python
        # Campo discreto simple (str equivalente)
        GroupByField(field="status")

        # Campo datetime con truncación mensual
        GroupByField(field="created_at", trunc=DatetimeTrunc.month)
        ```
    """

    field: str = Field(
        description=(
            "Nombre del campo del modelo por el que se agrupa. "
            "Debe existir en el modelo y no ser de tipo continuo (FLOAT, DOUBLE, DECIMAL, NUMERIC, REAL)."
        )
    )
    trunc: Optional[DatetimeTrunc] = Field(
        default=None,
        description=(
            "Nivel de truncación temporal. "
            "Obligatorio cuando el campo es de tipo DATETIME o TIMESTAMP. "
            "En cualquier otro tipo es un error, también en DATE (ya tiene precisión de día)."
        )
    )

    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True,
    }


class AggField(PrettyModel):
    """
    Definición de un campo o expresión aritmética a agregar.

    Reemplaza el formato dict anterior ``{"expr": "...", "as": "..."}``.

    Examples:
        ```python
        # Campo simple (equivalente a pasar un str)
        AggField(expr="price")

        # Expresión con alias
        AggField(expr="revenue-cost", alias="profit")

        # Expresión compleja
        AggField(expr="(price*quantity)*1.21", alias="total_with_vat")
        ```
    """

    expr: str = Field(
        description=(
            "Nombre de campo simple (ej: 'price') o expresión aritmética "
            "(ej: 'revenue-cost', 'price*quantity', '(a+b)/2'). "
            "Los operadores soportados son: +, -, *, /, %, ()."
        )
    )
    alias: Optional[str] = Field(
        default=None,
        description=(
            "Alias personalizado para la clave del resultado. "
            "Si se omite se genera automáticamente como '<operacion>_<expr_limpia>' "
            "(ej: para expr='price' y operación 'sum' → 'sum_price'). "
            "Con alias 'profit' y operación 'sum' → 'sum_profit'."
        )
    )

    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True,
    }


class AggOrderBy(PrettyModel):
    """
    Criterio de ordenación para el resultado de una agregación.

    Referencia una columna calculada por su operación y campo, equivalente a
    ORDER BY <operation>_<field> en SQL.

    Examples:
        ```python
        # Ordenar por count_id descendente (top más vendidos)
        AggOrderBy(operation="count", field="id")

        # Ordenar por sum_revenue ascendente
        AggOrderBy(operation="sum", field="revenue", direction="asc")
        ```
    """

    operation: Literal["sum", "mean", "max", "min", "count"] = Field(
        description="Operación de agregación cuyo resultado se usa para ordenar."
    )
    field: str = Field(
        description=(
            "Nombre del campo o alias usado en la agregación. "
            "Debe coincidir con el field_key generado: el alias si se proporcionó, "
            "el nombre del campo en caso contrario."
        )
    )
    direction: Literal["asc", "desc"] = Field(
        default="desc",
        description="Dirección de ordenación: 'desc' (mayor a menor) o 'asc' (menor a mayor)."
    )

    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True,
    }


class AggRequest(PrettyModel):
    """
    Input para el método agg. Encapsula qué calcular y sobre qué dimensiones agrupar.

    Los filtros de filas (WHERE) se siguen pasando como kwargs al método,
    ya que son específicos de cada modelo generado.

    Examples:
        ```python
        # Agregación global sin GROUP BY
        AggRequest(aggregations={"sum": ["price"], "count": ["id"]})

        # Con GROUP BY por campo discreto y datetime truncado
        AggRequest(
            aggregations={"sum": [AggField(expr="revenue-cost", alias="profit")], "count": ["id"]},
            group_by=["status", GroupByField(field="created_at", trunc=DatetimeTrunc.month)]
        )

        # Top 10 productos más vendidos (ranking)
        AggRequest(
            aggregations={"count": ["id"]},
            group_by=["referencia_producto"],
            order_by=[AggOrderBy(operation="count", field="id")],
            limit=10
        )
        ```
    """

    aggregations: Dict[
        Literal["sum", "mean", "max", "min", "count"],
        List[Union[str, AggField]]
    ] = Field(
        description=(
            "Mapa de operación → lista de campos o expresiones a agregar. "
            "Operaciones soportadas: sum, mean, max, min, count. "
            "Cada elemento puede ser un nombre de campo (str) o un AggField con alias opcional."
        )
    )
    group_by: Optional[List[Union[str, GroupByField]]] = Field(
        default=None,
        description=(
            "Campos por los que agrupar los resultados (equivale a GROUP BY en SQL). "
            "Un str se interpreta como GroupByField(field=str, trunc=None). "
            "Campos DATETIME/TIMESTAMP requieren GroupByField con trunc explícito. "
            "Campos FLOAT/DOUBLE/DECIMAL/NUMERIC/REAL no están permitidos."
        )
    )
    order_by: Optional[List[AggOrderBy]] = Field(
        default=None,
        description=(
            "Criterios de ordenación aplicados al resultado (equivale a ORDER BY en SQL). "
            "Cada elemento referencia una columna calculada por operation + field. "
            "Combinado con limit permite obtener rankings (ej: top 10 por conteo)."
        )
    )
    limit: Optional[int] = Field(
        default=None,
        ge=1,
        description=(
            "Número máximo de filas a devolver (equivale a LIMIT en SQL). "
            "Combinado con order_by permite obtener rankings."
        )
    )

    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True,
    }


class AggRow(PrettyModel):
    """
    Una fila del resultado de agregación.

    Sin GROUP BY siempre existe exactamente una fila con group={}.
    Con GROUP BY existe una fila por cada combinación de valores de agrupación.
    """

    group: Dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Valores de los campos de agrupación para esta fila. "
            "Vacío cuando no se usó GROUP BY. "
            "Para campos datetime con truncación la clave sigue el patrón "
            "'<campo>_<trunc>' (ej: 'created_at_month': datetime(2024, 1, 1))."
        )
    )
    data: Dict[str, Optional[Union[int, float, str]]] = Field(
        description=(
            "Resultados de las agregaciones para esta fila. "
            "Las claves siguen el patrón '<operacion>_<campo_o_alias>' "
            "(ej: 'sum_price', 'count_id', 'sum_profit' si se usó alias)."
        )
    )

    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True,
        "arbitrary_types_allowed": True,
    }


class AggregationResult(PrettyModel):
    """
    Resultado estructurado para operaciones de agregación, con o sin GROUP BY.

    Sin GROUP BY: rows contiene exactamente una fila con group={}.
    Con GROUP BY: rows contiene una fila por cada grupo encontrado.

    Examples:
        ```python
        # Sin GROUP BY
        result = dao.agg(AggRequest(aggregations={"sum": ["price"], "count": ["id"]}))
        result.rows[0].data  # {"sum_price": 1000.0, "count_id": 50}

        # Con GROUP BY por campo discreto
        result = dao.agg(AggRequest(
            aggregations={"sum": ["revenue"], "count": ["id"]},
            group_by=["status"]
        ))
        for row in result.rows:
            print(row.group)  # {"status": "active"}
            print(row.data)   # {"sum_revenue": 8500.0, "count_id": 42}

        # Con GROUP BY por datetime truncado
        result = dao.agg(AggRequest(
            aggregations={"sum": [AggField(expr="revenue-cost", alias="profit")]},
            group_by=[GroupByField(field="created_at", trunc=DatetimeTrunc.month)]
        ))
        for row in result.rows:
            print(row.group)  # {"created_at_month": datetime(2024, 1, 1, 0, 0)}
            print(row.data)   # {"sum_profit": 3200.0}
        ```
    """

    success: bool = Field(
        description=(
            "True si la consulta se ejecutó con todo lo pedido. Es todo o nada: si una "
            "sola parte de la petición no se puede hacer —un campo que no existe, un tipo "
            "que no admite la operación, un group_by o un order_by imposibles— success es "
            "False, no se consulta nada y errors dice por qué."
        )
    )
    rows: List[AggRow] = Field(
        default_factory=list,
        description=(
            "Filas del resultado. "
            "Sin GROUP BY contiene exactamente una fila (o ninguna si no hay registros). "
            "Con GROUP BY contiene una fila por cada combinación de valores de agrupación."
        )
    )
    group_by: List[str] = Field(
        default_factory=list,
        description=(
            "Nombres de los campos de agrupación efectivamente aplicados, en el orden usado. "
            "Para campos datetime truncados refleja el nombre del campo original (no la clave compuesta)."
        )
    )
    processed_fields: List[str] = Field(
        default_factory=list,
        description="Lista de campos y expresiones procesados correctamente en las agregaciones."
    )
    warnings: List[str] = Field(
        default_factory=list,
        description=(
            "Advertencias que no cambian el resultado (ej: una operación pedida sin ningún "
            "campo). Nada que se haya pedido y no se haya hecho va aquí: eso es un error."
        )
    )
    errors: List[str] = Field(
        default_factory=list,
        description=(
            "Por qué no se pudo hacer la petición (ej: campo inexistente, tipo que no admite "
            "la operación, tipo continuo en group_by, datetime sin trunc). "
            "Si hay alguno, success=False y rows está vacío."
        )
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Información de diagnóstico: total_operations, valid_operations, "
            "total_expressions, operations_summary."
        )
    )

    def has_warnings(self) -> bool:
        """Retorna True si hay advertencias."""
        return len(self.warnings) > 0

    def has_errors(self) -> bool:
        """Retorna True si hay errores."""
        return len(self.errors) > 0

    def get_summary(self) -> str:
        """Retorna un resumen legible de la operación."""
        if not self.success:
            return f"Operación fallida: {len(self.errors)} errores encontrados"

        parts = [f"Operación exitosa: {len(self.processed_fields)} campos procesados, {len(self.rows)} filas"]
        if self.group_by:
            parts.append(f"agrupado por {self.group_by}")
        if self.has_warnings():
            parts.append(f"{len(self.warnings)} advertencias")
        if self.has_errors():
            parts.append(f"{len(self.errors)} errores no críticos")

        return ", ".join(parts)

    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "rows": [{"group": {}, "data": {"sum_price": 150.50, "count_id": 25}}],
                    "group_by": [],
                    "processed_fields": ["price", "id"],
                    "warnings": [],
                    "errors": [],
                    "metadata": {"total_operations": 2, "valid_operations": 2, "total_expressions": 2}
                },
                {
                    "success": True,
                    "rows": [
                        {"group": {"status": "active"},   "data": {"sum_revenue": 8500.0, "count_id": 42}},
                        {"group": {"status": "inactive"}, "data": {"sum_revenue": 1200.0, "count_id": 8}}
                    ],
                    "group_by": ["status"],
                    "processed_fields": ["revenue", "id"],
                    "warnings": [],
                    "errors": [],
                    "metadata": {"total_operations": 2, "valid_operations": 2, "total_expressions": 2}
                },
                {
                    "success": False,
                    "rows": [],
                    "group_by": [],
                    "processed_fields": [],
                    "warnings": [],
                    "errors": ["Campo 'price' es de tipo FLOAT: no está permitido en group_by"],
                    "metadata": {"total_operations": 1, "valid_operations": 0, "total_expressions": 0}
                }
            ]
        }
    }


class ExpressionParser:
    """
    Parser seguro para expresiones aritméticas en agregaciones SQLAlchemy.
    
    Soporta operaciones aritméticas básicas sobre columnas de modelos SQLAlchemy
    con validación estricta de seguridad.
    
    Examples:
        >>> # Expresión simple
        >>> expr = ExpressionParser.parse("field1/field2", MyModel)
        >>> 
        >>> # Expresión compleja
        >>> expr = ExpressionParser.parse("(revenue-cost)/quantity", MyModel)
        >>> 
        >>> # Con constantes
        >>> expr = ExpressionParser.parse("price*1.21", MyModel)
    """
    
    # Límites de seguridad
    MAX_EXPRESSION_LENGTH = 200
    MAX_TOKENS = 50
    MAX_NESTED_PARENS = 5
    
    # Operadores permitidos y sus funciones
    OPERATORS = {
        '+': lambda a, b: a + b,
        '-': lambda a, b: a - b,
        '*': lambda a, b: a * b,
        '/': lambda a, b: a / b,
        '%': lambda a, b: a % b,
    }
    
    # Precedencia de operadores (mayor número = mayor precedencia)
    PRECEDENCE = {
        '+': 1,
        '-': 1,
        '*': 2,
        '/': 2,
        '%': 2,
    }
    
    # Pattern para tokenizar: campos, números, operadores, paréntesis
    TOKEN_PATTERN = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*|\d+\.?\d*|[+\-*/%()])')
    
    @classmethod
    def parse(cls, expression: str, model: DeclarativeMeta) -> ColumnElement:
        """
        Parsea una expresión aritmética y la convierte en una expresión SQLAlchemy.
        
        Args:
            expression: String con la expresión aritmética (ej: "field1/field2")
            model: Modelo SQLAlchemy (clase que hereda de DeclarativeBase)
            
        Returns:
            Expresión SQLAlchemy compilada lista para usar en queries
            
        Raises:
            ValueError: Si la expresión es inválida, insegura o contiene campos inexistentes
            
        Examples:
            >>> from sqlalchemy import select, func
            >>> expr = ExpressionParser.parse("price/quantity", Product)
            >>> query = select(func.avg(expr))
        """
        # Validaciones de seguridad
        cls._validate_safety(expression)
        
        # Tokenizar
        tokens = cls._tokenize(expression)
        
        # Validar tokens
        cls._validate_tokens(tokens, model)
        
        # Convertir a notación postfija (RPN) usando Shunting Yard
        postfix = cls._to_postfix(tokens)
        
        # Evaluar y construir expresión SQLAlchemy
        return cls._evaluate_postfix(postfix, model)
    
    @classmethod
    def _validate_safety(cls, expression: str) -> None:
        """
        Valida que la expresión cumple con los límites de seguridad.
        
        Args:
            expression: La expresión a validar
            
        Raises:
            ValueError: Si la expresión excede los límites de seguridad
        """
        if not expression or not expression.strip():
            raise ValueError("La expresión no puede estar vacía")
        
        if len(expression) > cls.MAX_EXPRESSION_LENGTH:
            raise ValueError(
                f"Expresión demasiado larga. Máximo {cls.MAX_EXPRESSION_LENGTH} caracteres"
            )
        
        # Contar profundidad de paréntesis anidados
        depth = 0
        max_depth = 0
        for char in expression:
            if char == '(':
                depth += 1
                max_depth = max(max_depth, depth)
            elif char == ')':
                depth -= 1
                if depth < 0:
                    raise ValueError("Paréntesis desbalanceados: más ')' que '('")
        
        if depth != 0:
            raise ValueError("Paréntesis desbalanceados: más '(' que ')'")
        
        if max_depth > cls.MAX_NESTED_PARENS:
            raise ValueError(
                f"Demasiados paréntesis anidados. Máximo {cls.MAX_NESTED_PARENS} niveles"
            )
    
    @classmethod
    def _tokenize(cls, expression: str) -> List[str]:
        """
        Divide la expresión en tokens individuales.
        
        Args:
            expression: La expresión a tokenizar
            
        Returns:
            Lista de tokens (campos, números, operadores, paréntesis)
            
        Raises:
            ValueError: Si la expresión contiene caracteres inválidos
        """
        # Eliminar espacios en blanco
        expression = expression.strip().replace(' ', '')
        
        # Tokenizar usando regex
        tokens = cls.TOKEN_PATTERN.findall(expression)
        
        if len(tokens) > cls.MAX_TOKENS:
            raise ValueError(
                f"Demasiados tokens. Máximo {cls.MAX_TOKENS} tokens"
            )
        
        # Verificar que se parseó toda la expresión
        reconstructed = ''.join(tokens)
        if reconstructed != expression:
            invalid_chars = set(expression) - set(reconstructed)
            raise ValueError(
                f"Expresión contiene caracteres inválidos: {', '.join(repr(c) for c in invalid_chars)}"
            )
        
        return tokens
    
    @classmethod
    def _validate_tokens(cls, tokens: List[str], model: DeclarativeMeta) -> None:
        """
        Valida que todos los tokens sean seguros y válidos.
        
        Args:
            tokens: Lista de tokens a validar
            model: Modelo SQLAlchemy para validar nombres de campos
            
        Raises:
            ValueError: Si algún token es inválido o inseguro
        """
        if not tokens:
            raise ValueError("No se encontraron tokens en la expresión")
        
        for token in tokens:
            # Permitir paréntesis
            if token in '()':
                continue
            
            # Permitir operadores
            if token in cls.OPERATORS:
                continue
            
            # Permitir números (enteros o decimales)
            if re.match(r'^\d+\.?\d*$', token):
                continue
            
            # Debe ser un campo válido del modelo
            if not hasattr(model, token):
                raise ValueError(
                    f"Campo '{token}' no existe en el modelo {model.__name__}"
                )
            
            # Verificar que es una columna (no una relación u otro atributo)
            attr = getattr(model, token)
            if not hasattr(attr, 'type'):
                raise ValueError(
                    f"'{token}' no es una columna válida en {model.__name__}"
                )
    
    @classmethod
    def _to_postfix(cls, tokens: List[str]) -> List[str]:
        """
        Convierte tokens en notación infija a notación postfija usando el algoritmo Shunting Yard.
        
        Args:
            tokens: Lista de tokens en notación infija
            
        Returns:
            Lista de tokens en notación postfija (RPN)
            
        Raises:
            ValueError: Si hay errores de sintaxis en la expresión
        """
        output = []
        operator_stack = []
        
        for token in tokens:
            # Número o campo: añadir directamente a output
            if token not in '()' and token not in cls.OPERATORS:
                output.append(token)
            
            # Operador: aplicar reglas de precedencia
            elif token in cls.OPERATORS:
                while (operator_stack and 
                       operator_stack[-1] != '(' and 
                       operator_stack[-1] in cls.PRECEDENCE and
                       cls.PRECEDENCE[operator_stack[-1]] >= cls.PRECEDENCE[token]):
                    output.append(operator_stack.pop())
                operator_stack.append(token)
            
            # Paréntesis izquierdo: push al stack
            elif token == '(':
                operator_stack.append(token)
            
            # Paréntesis derecho: pop hasta encontrar '('
            elif token == ')':
                while operator_stack and operator_stack[-1] != '(':
                    output.append(operator_stack.pop())
                if not operator_stack:
                    raise ValueError("Paréntesis desbalanceados")
                operator_stack.pop()  # Remover '('
        
        # Vaciar el stack de operadores
        while operator_stack:
            if operator_stack[-1] in '()':
                raise ValueError("Paréntesis desbalanceados")
            output.append(operator_stack.pop())
        
        return output
    
    @classmethod
    def _evaluate_postfix(cls, postfix: List[str], model: DeclarativeMeta) -> ColumnElement:
        """
        Evalúa la expresión en notación postfija y construye la expresión SQLAlchemy.
        
        Args:
            postfix: Lista de tokens en notación postfija
            model: Modelo SQLAlchemy
            
        Returns:
            Expresión SQLAlchemy compilada
            
        Raises:
            ValueError: Si la expresión es sintácticamente incorrecta
        """
        stack = []
        
        for token in postfix:
            # Operador: pop dos operandos, aplicar operación, push resultado
            if token in cls.OPERATORS:
                if len(stack) < 2:
                    raise ValueError(
                        "Expresión inválida: operador sin suficientes operandos"
                    )
                
                right = stack.pop()
                left = stack.pop()
                
                # Aplicar operación SQLAlchemy
                result = cls.OPERATORS[token](left, right)
                stack.append(result)
            
            # Número literal
            elif re.match(r'^\d+\.?\d*$', token):
                value = float(token) if '.' in token else int(token)
                stack.append(value)
            
            # Campo del modelo
            else:
                column = getattr(model, token)
                stack.append(column)
        
        # Debe quedar exactamente un elemento en el stack
        if len(stack) != 1:
            raise ValueError(
                "Expresión inválida: " + 
                ("demasiados operandos" if len(stack) > 1 else "sin operandos")
            )
        
        return stack[0]
    
    @classmethod
    def get_field_name(cls, expression: str) -> str:
        """
        Genera un nombre de campo limpio para usar como label en la agregación.
        
        Args:
            expression: La expresión original
            
        Returns:
            Nombre limpio para usar como label (ej: "field1_field2" para "field1/field2")
            
        Examples:
            >>> ExpressionParser.get_field_name("field1/field2")
            'field1_field2'
            >>> ExpressionParser.get_field_name("(revenue-cost)/quantity")
            '_revenue_cost__quantity'
        """
        # Reemplazar operadores y paréntesis con guiones bajos
        clean = re.sub(r'[^a-zA-Z0-9_]', '_', expression)
        # Eliminar guiones bajos consecutivos
        clean = re.sub(r'_+', '_', clean)
        # Eliminar guiones bajos al inicio/final
        clean = clean.strip('_')
        return clean if clean else 'expr'


# Las cinco operaciones de agregación, en el orden en que se documentan.
AGG_OPERATIONS = ('count', 'sum', 'mean', 'max', 'min')

#: Qué agregaciones admite cada columna de un modelo: `{columna: (tipo, operaciones)}`. Lo
#: escribe el generador en cada DAO (`_AGG_COLUMNS`), a partir del tipo del schema —no del
#: tipo SQLAlchemy, que no distingue un enumerado ni una columna cifrada de un texto—.
AggColumns = Dict[str, tuple]


def agg_field_error(model_name: str, columns: AggColumns, field: str, operation: str) -> Optional[str]:
    """
    Por qué no se puede aplicar `operation` a la columna `field`, o `None` si se puede.

    Una agregación que no se puede hacer **es un error**, no un aviso: antes se descartaba
    con un aviso y el resultado llegaba sin esa clave, y quien solo miraba `rows` (tai-api,
    que respondía 200) no se enteraba de que faltaba.
    """
    if field not in columns:
        return f"Campo '{field}' no existe en modelo {model_name}"
    tipo, admitidas = columns[field]
    if operation not in admitidas:
        return (
            f"Campo '{field}' de tipo '{tipo}' no es válido para '{operation}': "
            f"admite {', '.join(admitidas)}"
        )
    return None


def agg_expression_error(model_name: str, columns: AggColumns, expression: str) -> Optional[str]:
    """
    Por qué no se puede usar `expression` como expresión aritmética, o `None` si se puede.

    `ExpressionParser` comprueba la sintaxis y que los nombres sean columnas; esto, que lo
    sean **numéricas** —las que admiten `sum`—. Sin ello `titulo * 2` llegaba al motor y
    volvía como un error de base de datos.
    """
    for token in ExpressionParser._tokenize(expression):
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', token):
            continue
        if token not in columns:
            return f"Campo '{token}' no existe en modelo {model_name}"
        tipo, admitidas = columns[token]
        if 'sum' not in admitidas:
            return (
                f"Campo '{token}' de tipo '{tipo}' no es válido en una expresión aritmética: "
                f"solo admite columnas numéricas"
            )
    return None


def agg_value(operation: str, value: Any) -> Optional[Union[int, float, str]]:
    """
    El valor de una agregación tal y como va en `AggRow.data`.

    `count` es un entero (0 si no hay filas); `sum`, `mean` y el `max`/`min` de un número,
    un float; el de una fecha u hora, su ISO; el de un texto, el texto.
    """
    if value is None:
        return 0 if operation == 'count' else None
    if operation == 'count':
        return int(value)
    if isinstance(value, (date, time)):   # datetime es subclase de date
        return value.isoformat()
    if isinstance(value, str):
        return value
    return float(value)


OPERATION_FUNCTIONS = {
    'sum':   func.sum,
    'mean':  func.avg,
    'max':   func.max,
    'min':   func.min,
    'count': func.count,
}

# Tipos no permitidos en GROUP BY (continuos — cardinalidad altísima, semánticamente inútil)
GROUP_BY_FORBIDDEN_TYPES = ['FLOAT', 'DOUBLE', 'REAL', 'DECIMAL', 'NUMERIC']
# Tipos que requieren trunc obligatorio en GROUP BY
GROUP_BY_DATETIME_TYPES  = ['DATETIME', 'TIMESTAMP']
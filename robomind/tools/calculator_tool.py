"""Safe arithmetic evaluator. No eval, no exec.

Supports: + - * / // % ** unary- and a whitelisted set of math functions.
"""
from __future__ import annotations

import ast
import math
import operator
from typing import Any

from ..core.models import ToolResult
from .base import BaseTool


_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}
_SAFE_FUNCS = {
    "abs": abs, "min": min, "max": max, "round": round, "pow": pow,
    "sqrt": math.sqrt, "exp": math.exp, "log": math.log, "log10": math.log10,
    "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "asin": math.asin, "acos": math.acos, "atan": math.atan,
    "atan2": math.atan2,
    "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
    "radians": math.radians, "degrees": math.degrees,
    "floor": math.floor, "ceil": math.ceil, "fabs": math.fabs,
}
_SAFE_NAMES = {"pi": math.pi, "e": math.e, "tau": math.tau}
_MAX_POW = 1000  # prevent 10**100000 DoS


def _eval(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _eval(node.body)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise ValueError(f"unsupported constant: {node.value!r}")
    if isinstance(node, ast.BinOp):
        op = _BIN_OPS.get(type(node.op))
        if op is None:
            raise ValueError(f"unsupported binary op: {type(node.op).__name__}")
        a, b = _eval(node.left), _eval(node.right)
        if isinstance(node.op, ast.Pow) and (abs(a) > 1 and abs(b) > _MAX_POW):
            raise ValueError("exponent too large")
        return op(a, b)
    if isinstance(node, ast.UnaryOp):
        op = _UNARY_OPS.get(type(node.op))
        if op is None:
            raise ValueError(f"unsupported unary op: {type(node.op).__name__}")
        return op(_eval(node.operand))
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name) or node.func.id not in _SAFE_FUNCS:
            raise ValueError("only whitelisted functions allowed")
        if node.keywords:
            raise ValueError("keyword arguments not allowed")
        args = [_eval(a) for a in node.args]
        return float(_SAFE_FUNCS[node.func.id](*args))
    if isinstance(node, ast.Name):
        if node.id in _SAFE_NAMES:
            return float(_SAFE_NAMES[node.id])
        raise ValueError(f"unknown name: {node.id!r}")
    raise ValueError(f"unsupported expression: {type(node).__name__}")


def safe_eval(expr: str) -> float:
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as exc:
        raise ValueError(f"syntax error: {exc.msg}") from None
    return _eval(tree)


class CalculatorTool(BaseTool):
    name = "calculator"
    description = "Evaluate a safe arithmetic expression."
    safety_class = "compute"

    args_schema = {"expr": "str — e.g. '2 * sqrt(16) + sin(pi/2)'"}
    output_schema = {"value": "float"}

    def run(self, *, step_id: str = "calc", expr: str = "", **_: Any) -> ToolResult:
        if not expr:
            return ToolResult(step_id=step_id, ok=False, error="expr required")
        try:
            value = safe_eval(expr)
        except ValueError as exc:
            return ToolResult(step_id=step_id, ok=False, error=str(exc))
        return ToolResult(step_id=step_id, ok=True,
                          value={"expr": expr, "value": value})
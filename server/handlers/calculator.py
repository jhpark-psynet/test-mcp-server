"""안전한 계산기 핸들러 (AST 기반)."""
import ast
import operator
from typing import Any, Dict


# 허용된 연산자 매핑
SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

# 허용된 함수 매핑
SAFE_FUNCS = {
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
}


def safe_eval(expr: str) -> float:
    """AST 기반 안전한 수식 평가.

    Args:
        expr: 수학 표현식 (예: "2 + 2", "10 * 5 + 3")

    Returns:
        계산 결과

    Raises:
        ValueError: 허용되지 않은 연산 또는 구문
        SyntaxError: 잘못된 구문
    """
    # 빈 문자열 체크
    if not expr or not expr.strip():
        raise ValueError("Empty expression")

    try:
        # Parse expression into AST
        node = ast.parse(expr, mode="eval").body
    except SyntaxError as e:
        raise SyntaxError(f"Invalid syntax: {e}")

    def eval_node(n):
        """Recursively evaluate AST node."""
        # Number
        if isinstance(n, ast.Constant):
            if isinstance(n.value, (int, float)):
                return n.value
            raise ValueError(f"Unsupported constant type: {type(n.value)}")

        # Binary operation (e.g., 2 + 3)
        if isinstance(n, ast.BinOp):
            op_type = type(n.op)
            if op_type not in SAFE_OPS:
                raise ValueError(f"Unsupported operator: {op_type.__name__}")
            left = eval_node(n.left)
            right = eval_node(n.right)
            return SAFE_OPS[op_type](left, right)

        # Unary operation (e.g., -5)
        if isinstance(n, ast.UnaryOp):
            op_type = type(n.op)
            if op_type not in SAFE_OPS:
                raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
            operand = eval_node(n.operand)
            return SAFE_OPS[op_type](operand)

        # Function call (e.g., abs(-5))
        if isinstance(n, ast.Call):
            if not isinstance(n.func, ast.Name):
                raise ValueError("Only simple function names are allowed")
            func_name = n.func.id
            if func_name not in SAFE_FUNCS:
                raise ValueError(f"Unsupported function: {func_name}")
            args = [eval_node(arg) for arg in n.args]
            return SAFE_FUNCS[func_name](*args)

        # Unsupported node type
        raise ValueError(f"Unsupported expression: {type(n).__name__}")

    try:
        result = eval_node(node)
        return float(result)
    except ZeroDivisionError:
        raise ValueError("Division by zero")
    except Exception as e:
        raise ValueError(f"Evaluation error: {str(e)}")


def calculator_handler(arguments: Dict[str, Any]) -> str:
    """Handle calculator tool execution with safe evaluation.

    Args:
        arguments: Tool arguments with 'expression' field

    Returns:
        Calculation result or error message
    """
    expression = arguments.get("expression", "")

    try:
        result = safe_eval(expression)
        # Format result nicely
        if result == int(result):
            return f"Result: {int(result)}"
        else:
            return f"Result: {result:.6g}"
    except (ValueError, SyntaxError) as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

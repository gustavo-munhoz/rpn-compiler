from parser.ast_node import ASTNode
from .types import SemanticType
from .errors import SemanticError


def _is_number(s: str) -> bool:
    try:
        float(s)
        return True
    except (ValueError, TypeError):
        return False


def _visit_literal(node: ASTNode):
    node.eval_type = SemanticType.FLOAT if '.' in node.label else SemanticType.INT
    node.const_value = float(node.label) if node.eval_type == SemanticType.FLOAT else int(node.label)


class SemanticAnalyzer:
    """
    Percorre a AST para realizar a análise semântica, checando tipos,
    regras de negócio e realizando otimizações como constant folding.
    """

    def __init__(self, auto_cast: bool = True):
        self.auto_cast = auto_cast

    def analyze(self, node: ASTNode, line_index: int = 0):
        if node.label == '<program>':
            self._visit_program(node)
        elif node.label == '<program_tail>':
            self._visit_program_tail(node, line_index)
        elif _is_number(node.label):
            _visit_literal(node)
        elif node.label in ['+', '-', '*', '/', '|', '%', '^']:
            self._visit_binary_op(node, line_index)
        elif node.label == 'RES':
            self._visit_res(node, line_index)
        elif node.label == 'MEM':
            self._visit_mem(node, line_index)
        elif node.label == 'IF':
            self._visit_if(node, line_index)
        elif node.label == 'THEN':
            self._visit_then(node, line_index)
        elif node.label == 'ELSE':
            self._visit_else(node, line_index)
        elif node.label == 'FOR':
            self._visit_for(node, line_index)
        else:
            raise SemanticError(f"No semantic analysis rule found for node: '{node.label}'", node.token)

    def _visit_program(self, node: ASTNode):
        if not node.children:
            node.eval_type = SemanticType.VOID
            return

        expr_node = node.children[0]
        tail_node = node.children[1]

        self.analyze(expr_node, 0)
        self.analyze(tail_node, 1)

        node.eval_type = SemanticType.VOID

    def _visit_program_tail(self, node: ASTNode, line_index: int):
        if not node.children:
            node.eval_type = SemanticType.VOID
            return

        expr_node = node.children[0]
        next_tail_node = node.children[1]

        self.analyze(expr_node, line_index)
        self.analyze(next_tail_node, line_index + 1)

        node.eval_type = SemanticType.VOID

    def _visit_binary_op(self, node: ASTNode, line_index: int):
        if len(node.children) != 2:
            raise SemanticError(
                f"Binary operator '{node.label}' expects 2 operands, but received {len(node.children)}.", node.token)

        left_child, right_child = node.children
        self.analyze(left_child, line_index)
        self.analyze(right_child, line_index)

        left_type, right_type = left_child.eval_type, right_child.eval_type

        if left_type not in (SemanticType.INT, SemanticType.FLOAT) or right_type not in (
                SemanticType.INT, SemanticType.FLOAT):
            raise SemanticError(
                f"Operator '{node.label}' expects numeric operands, but received {left_type.name} and {right_type.name}.",
                node.token)

        if not self.auto_cast and left_type != right_type:
            raise SemanticError(
                f"Incompatible types for '{node.label}': {left_type.name} and {right_type.name}. (Automatic casting disabled)",
                node.token)

        if node.label == '^':
            if right_type is not SemanticType.INT: raise SemanticError(
                f"The exponent ('^') must be an INT, but got {right_type.name}.", right_child.token)
            if right_child.const_value is not None and right_child.const_value < 0: raise SemanticError(
                f"The exponent ('^') must be a non-negative integer.", right_child.token)

        elif node.label in ('/', '|', '%'):
            if right_child.const_value == 0: raise SemanticError("Division by literal zero.", right_child.token)

        if node.label in ('/', '%'):
            node.eval_type = SemanticType.INT
        elif node.label == '^':
            node.eval_type = left_type
        elif left_type == SemanticType.FLOAT or right_type == SemanticType.FLOAT:
            node.eval_type = SemanticType.FLOAT
        else:
            node.eval_type = SemanticType.INT

        if self.auto_cast and left_type != right_type:
            if left_type == SemanticType.INT: left_child.needs_cast_to_float = True
            if right_type == SemanticType.INT: right_child.needs_cast_to_float = True

        if left_child.const_value is not None and right_child.const_value is not None:
            left_val, right_val = left_child.const_value, right_child.const_value
            op, result = node.label, 0.0
            if op == '+':
                result = left_val + right_val
            elif op == '-':
                result = left_val - right_val
            elif op == '*':
                result = left_val * right_val
            elif op == '^':
                result = left_val ** right_val
            elif op == '%':
                result = left_val % right_val
            elif op == '|' and right_val != 0:
                result = left_val / right_val
            elif op == '/' and right_val != 0:
                result = left_val // right_val
            node.const_value = int(result) if node.eval_type == SemanticType.INT and result == int(result) else float(
                result)

    def _visit_res(self, node: ASTNode, line_index: int):
        if len(node.children) != 1: raise SemanticError("'RES' expects 1 operand.", node.token)
        child = node.children[0]
        self.analyze(child, line_index)

        if child.eval_type is not SemanticType.INT:
            raise SemanticError(f"'RES' expects an INT operand, but received {child.eval_type.name}.", child.token)

        if child.const_value is not None:
            n_value = int(child.const_value)
            if n_value <= 0:
                raise SemanticError("'RES' operand must be a positive integer (e.g., 1, 2...).", child.token)
            if n_value > line_index:
                raise SemanticError(
                    f"Cannot 'RES' {n_value} lines back. Only {line_index} previous result(s) are available.",
                    child.token)

        node.eval_type = SemanticType.FLOAT

    def _visit_mem(self, node: ASTNode, line_index: int):
        if len(node.children) == 1:
            child = node.children[0]
            self.analyze(child, line_index)
            if child.eval_type not in (SemanticType.INT, SemanticType.FLOAT):
                raise SemanticError(f"'MEM' (write) expects a numeric operand, but received {child.eval_type.name}.",
                                    child.token)
            node.eval_type = child.eval_type
        elif len(node.children) == 0:
            node.eval_type = SemanticType.FLOAT
        else:
            raise SemanticError("'MEM' expects 0 or 1 operands.", node.token)

    def _visit_if(self, node: ASTNode, line_index: int):
        if len(node.children) != 1: raise SemanticError("'IF' expects 1 operand (the condition).", node.token)
        condition = node.children[0]
        self.analyze(condition, line_index)
        if condition.eval_type not in (SemanticType.INT, SemanticType.FLOAT):
            raise SemanticError(f"The IF condition must be numeric, but got type {condition.eval_type.name}.",
                                condition.token)
        node.eval_type = SemanticType.VOID

    def _visit_then(self, node: ASTNode, line_index: int):
        if len(node.children) != 2: raise SemanticError("'THEN' expects 2 operands.", node.token)
        if_node, then_branch = node.children
        self.analyze(if_node, line_index)
        self.analyze(then_branch, line_index)
        if if_node.label != 'IF':
            raise SemanticError(f"The first operand for 'THEN' must be 'IF',"
                                f" but got '{if_node.label}'.", if_node.token)
        node.eval_type = SemanticType.VOID

    def _visit_else(self, node: ASTNode, line_index: int):
        if len(node.children) != 2:
            raise SemanticError("'ELSE' expects 2 operands.", node.token)

        then_node, else_branch = node.children
        self.analyze(then_node, line_index)
        self.analyze(else_branch, line_index)

        if then_node.label != 'THEN':
            raise SemanticError(f"The first operand for 'ELSE' must be 'THEN', but got '{then_node.label}'.",
                                then_node.token)

        node.eval_type = SemanticType.VOID

    def _visit_for(self, node: ASTNode, line_index: int):
        if len(node.children) != 2: raise SemanticError("'FOR' expects 2 operands.", node.token)
        iterations, body_expr = node.children
        self.analyze(iterations, line_index)
        self.analyze(body_expr, line_index)
        if iterations.eval_type != SemanticType.INT:
            raise SemanticError(
                f"The first operand for FOR (iterations) must be INT, but got {iterations.eval_type.name}.",
                iterations.token)
        node.eval_type = SemanticType.VOID

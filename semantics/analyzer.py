from parser.ast_node import ASTNode
from .types import SemanticType, SignType
from .errors import SemanticError
from semantics.annotated_ast import AnnotatedASTNode
from typing import List


class SemanticAnalyzer:
    """
    Percorre a AST do parser e retorna uma nova árvore anotada,
    com informações de tipo e sinal, aplicando as regras semânticas da linguagem.
    """

    def __init__(self):
        pass

    def analyze(self, node: ASTNode, line_index: int = 0) -> AnnotatedASTNode:
        """
        Método despachante principal. Ele delega a construção do nó anotado
        para o método de construção (_build_...) apropriado.
        """

        if node.label == '<program>':
            return self._build_program_node(node)
        elif self._is_number(node.label):
            return self._build_literal_node(node)
        elif node.label in ['+', '-', '*', '/', '|', '%', '^']:
            return self._build_binary_op_node(node, line_index)
        elif node.label == 'RES':
            return self._build_res_node(node, line_index)
        elif node.label == 'MEM':
            return self._build_mem_node(node, line_index)
        elif node.label == 'IF':
            return self._build_if_node(node, line_index)
        elif node.label == 'THEN':
            return self._build_then_node(node, line_index)
        elif node.label == 'ELSE':
            return self._build_else_node(node, line_index)
        elif node.label == 'FOR':
            return self._build_for_node(node, line_index)
        elif node.label == '<program_tail>':
            return AnnotatedASTNode(label=node.label, children=[], eval_type=SemanticType.VOID, sign=SignType.UNKNOWN,
                                    original_token=node.token)
        else:
            raise SemanticError(f"No semantic analysis rule found for node: '{node.label}'", node.token)

    def _is_number(self, s: str) -> bool:
        try:
            float(s); return True
        except (ValueError, TypeError):
            return False

    def _get_sign_from_literal(self, value_str: str) -> SignType:
        value = float(value_str)
        if value > 0: return SignType.POSITIVE
        if value < 0: return SignType.NEGATIVE
        return SignType.ZERO

    def _build_literal_node(self, node: ASTNode) -> AnnotatedASTNode:
        eval_type = SemanticType.FLOAT if '.' in node.label else SemanticType.INT
        sign = self._get_sign_from_literal(node.label)
        return AnnotatedASTNode(label=node.label, children=[], eval_type=eval_type, sign=sign,
                                original_token=node.token)

    def _build_program_node(self, node: ASTNode) -> AnnotatedASTNode:
        """
        Constrói o nó para a raiz do programa, gerenciando a contagem de linhas
        de forma segura para programas de uma ou mais linhas.
        """
        annotated_children = []

        if node.children:
            line_idx = 0
            first_expr_node = node.children[0]
            annotated_children.append(self.analyze(first_expr_node, line_idx))

            if len(node.children) > 1:
                current_tail = node.children[1]
                line_idx = 1
                while current_tail and current_tail.children:
                    annotated_children.append(self.analyze(current_tail.children[0], line_idx))
                    current_tail = current_tail.children[1] if len(current_tail.children) > 1 else None
                    line_idx += 1

        for final_expr_node in annotated_children:
            if final_expr_node.label in ('IF', 'THEN'):
                raise SemanticError(
                    f"Incomplete conditional: '{final_expr_node.label}' is not a valid top-level expression.",
                    final_expr_node.original_token
                )

        return AnnotatedASTNode(label=node.label, children=annotated_children, eval_type=SemanticType.VOID,
                                sign=SignType.UNKNOWN, original_token=node.token)

    def _build_binary_op_node(self, node: ASTNode, line_index: int) -> AnnotatedASTNode:
        left_child = self.analyze(node.children[0], line_index)
        right_child = self.analyze(node.children[1], line_index)

        op = node.label
        if left_child.eval_type not in (SemanticType.INT, SemanticType.FLOAT) or right_child.eval_type not in (
        SemanticType.INT, SemanticType.FLOAT):
            raise SemanticError(f"Operator '{op}' expects numeric operands.", node.token)

        result_type = left_child.eval_type
        if op == '^':
            if right_child.eval_type is not SemanticType.INT:
                raise SemanticError(f"The exponent ('^') must be an INT.", right_child.original_token)
            if self._is_number(right_child.label) and int(right_child.label) < 0:
                raise SemanticError(f"The exponent ('^') must be a non-negative integer literal.",
                                    right_child.original_token)
            result_type = left_child.eval_type
        else:
            if op in ('/', '|', '%') and self._is_number(right_child.label) and float(right_child.label) == 0:
                raise SemanticError(f"Division by literal zero for operator '{op}'.", right_child.original_token)

            if op in ('%', '|'):
                result_type = SemanticType.FLOAT

            elif op == '/':
                result_type = SemanticType.INT

            elif left_child.eval_type == SemanticType.FLOAT or right_child.eval_type == SemanticType.FLOAT:
                result_type = SemanticType.FLOAT
                if left_child.eval_type != right_child.eval_type:
                    if left_child.eval_type == SemanticType.INT: left_child.needs_cast_to_float = True
                    if right_child.eval_type == SemanticType.INT: right_child.needs_cast_to_float = True
            else:
                result_type = SemanticType.INT

        return AnnotatedASTNode(label=op, children=[left_child, right_child], eval_type=result_type,
                                sign=SignType.UNKNOWN, original_token=node.token)

    def _build_res_node(self, node: ASTNode, line_index: int) -> AnnotatedASTNode:
        child = self.analyze(node.children[0], line_index)
        if child.eval_type is not SemanticType.INT:
            raise SemanticError(f"'RES' expects an INT operand.", child.original_token)
        if self._is_number(child.label):
            n_value = int(child.label)
            if n_value <= 0: raise SemanticError("'RES' operand must be a positive integer.", child.original_token)
            if n_value > line_index: raise SemanticError(
                f"Cannot 'RES' {n_value} lines back. Only {line_index} previous result(s) are available.",
                child.original_token)
        return AnnotatedASTNode(label=node.label, children=[child], eval_type=SemanticType.FLOAT, sign=SignType.UNKNOWN,
                                original_token=node.token)

    def _build_mem_node(self, node: ASTNode, line_index: int) -> AnnotatedASTNode:
        if node.children:
            child = self.analyze(node.children[0], line_index)
            if child.eval_type not in (SemanticType.INT, SemanticType.FLOAT):
                raise SemanticError("'MEM' (write) expects a numeric operand.", child.original_token)
            return AnnotatedASTNode(label=node.label, children=[child], eval_type=child.eval_type, sign=child.sign,
                                    original_token=node.token)
        else:
            return AnnotatedASTNode(label=node.label, children=[], eval_type=SemanticType.FLOAT, sign=SignType.UNKNOWN,
                                    original_token=node.token)

    def _build_if_node(self, node: ASTNode, line_index: int) -> AnnotatedASTNode:
        condition = self.analyze(node.children[0], line_index)
        if condition.eval_type not in (SemanticType.INT, SemanticType.FLOAT):
            raise SemanticError("IF condition must be numeric.", condition.original_token)
        return AnnotatedASTNode(label=node.label, children=[condition], eval_type=SemanticType.VOID,
                                sign=SignType.UNKNOWN, original_token=node.token)

    def _build_then_node(self, node: ASTNode, line_index: int) -> AnnotatedASTNode:
        # Este método não é chamado pelo despachante, mas serve para a recursão interna
        if_node = self.analyze(node.children[0], line_index)
        then_branch = self.analyze(node.children[1], line_index)
        if if_node.label != 'IF':
            raise SemanticError(f"The first operand for 'THEN' must be 'IF', but got '{if_node.label}'.",
                                if_node.original_token)

        return AnnotatedASTNode(label=node.label, children=[if_node, then_branch], eval_type=then_branch.eval_type,
                                sign=then_branch.sign, original_token=node.token)

    def _build_else_node(self, node: ASTNode, line_index: int) -> AnnotatedASTNode:

        then_node_annotated = self.analyze(node.children[0], line_index)
        else_branch_annotated = self.analyze(node.children[1], line_index)

        if then_node_annotated.label != 'THEN':
            raise SemanticError(f"The first operand for 'ELSE' must be 'THEN', but got '{then_node_annotated.label}'.",
                                then_node_annotated.original_token)

        then_type = then_node_annotated.eval_type
        else_type = else_branch_annotated.eval_type

        if then_type != else_type:
            raise SemanticError(
                f"Incompatible types in conditional branches: THEN branch has type {then_type.name}, but ELSE branch has type {else_type.name}. Types must be identical.",
                node.token)

        return AnnotatedASTNode(label=node.label, children=[then_node_annotated, else_branch_annotated],
                                eval_type=then_type, sign=SignType.UNKNOWN, original_token=node.token)

    def _build_for_node(self, node: ASTNode, line_index: int) -> AnnotatedASTNode:
        iterations = self.analyze(node.children[0], line_index)
        body_expr = self.analyze(node.children[1], line_index)

        if iterations.eval_type is not SemanticType.INT:
            raise SemanticError(f"The loop count for 'FOR' must be an INT, but got {iterations.eval_type.name}.",
                                iterations.original_token)

        return AnnotatedASTNode(label=node.label, children=[iterations, body_expr], eval_type=body_expr.eval_type,
                                sign=body_expr.sign, original_token=node.token)

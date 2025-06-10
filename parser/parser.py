from collections import deque
from dataclasses import dataclass
from lexer.tokens import TokenType, Token
from parser.table import M, P
from parser.errors import LL1SyntaxError
from parser.ast_node import ASTNode
from typing import List


@dataclass
class Build:
    lhs: str
    arity: int
    rule_id: int


class LL1Parser:
    def __init__(self, table=M, productions=P):
        self.table = table
        self.prod = productions

    @staticmethod
    def _err(msg: str, tok: Token):
        raise LL1SyntaxError(msg, tok.line, tok.col, tok.src_line)

    def parse(self, token_iterable: List[Token]):
        tokens = deque(token_iterable)
        sym_stack: list = [TokenType.EOF, "<program>"]
        ast_stack: list[ASTNode] = []

        while sym_stack:
            top = sym_stack.pop()

            if isinstance(top, Build):
                match top.rule_id:
                    case 2:
                        ast_stack.pop()
                        rpn_node = ast_stack.pop()
                        ast_stack.pop()
                        ast_stack.append(rpn_node)

                    case 3:
                        mem_keyword_node = ast_stack.pop()
                        ast_stack.append(ASTNode(label=mem_keyword_node.label,
                                                 children=[],
                                                 token=mem_keyword_node.token))

                    case 4:
                        tail_or_op_node = ast_stack.pop()
                        operand1_node = ast_stack.pop()

                        if tail_or_op_node.label == '<rpn_tail>':
                            operand2_node = tail_or_op_node.children[0]
                            op_node = tail_or_op_node.children[1]
                            ast_stack.append(ASTNode(label=op_node.label,
                                                     children=[operand1_node, operand2_node],
                                                     token=op_node.token))
                        else:
                            op_node = tail_or_op_node
                            ast_stack.append(ASTNode(label=op_node.label,
                                                     children=[operand1_node],
                                                     token=op_node.token))

                    case 5 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16:
                        pass

                    case 1 | 6 | 17 | 18:
                        children = [ast_stack.pop() for _ in range(top.arity)][::-1]
                        if top.lhs == '<program>' and not children:
                            ast_stack.append(ASTNode(top.lhs, [], None))
                        else:
                            ast_stack.append(ASTNode(top.lhs, children, children[0].token if children else None))

                continue

            la_tok = tokens[0]
            la_type = la_tok.type

            if isinstance(top, TokenType):
                if top == la_type:
                    token = tokens.popleft()
                    if top is not TokenType.EOF:
                        ast_stack.append(ASTNode(label=token.lexeme, token=token))
                    continue
                self._err(f"Expected {top.name}, found {la_type.name}", la_tok)

            prod_num = self.table.get(top, {}).get(la_type)
            if prod_num is None:
                expected_tokens = ", ".join(t.name for t in self.table.get(top, {}))
                self._err(f"Unexpected {la_type.name}; expected one of: {expected_tokens}", la_tok)

            _, rhs = self.prod[prod_num]
            if not isinstance(rhs, list):
                rhs = [rhs] if rhs else []

            sym_stack.append(Build(top, len(rhs), prod_num))
            for sym in reversed(rhs):
                if isinstance(sym, str) and sym in TokenType.__members__:
                    sym_stack.append(TokenType[sym])
                else:
                    sym_stack.append(sym)

        if len(ast_stack) != 1:
            raise RuntimeError(f"AST construction failed. Final stack size: {len(ast_stack)}")

        return ast_stack[0]

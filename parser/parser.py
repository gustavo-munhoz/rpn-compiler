from collections import deque
from dataclasses import dataclass
from lexer.tokens import TokenType
from parser.table import M, P
from parser.errors import LL1SyntaxError
from parser.ast_node import ASTNode


@dataclass
class Build:
    lhs: str
    arity: int


class LL1Parser:
    def __init__(self, table=M, productions=P):
        self.table = table
        self.prod = productions

    @staticmethod
    def _err(msg: str, tok):
        raise LL1SyntaxError(msg, tok.line, tok.col, tok.src_line)

    def parse(self, token_iterable):
        tokens = deque(token_iterable)
        sym_stack = [TokenType.EOF, "<program>"]
        ast_stack: list[ASTNode] = []

        while sym_stack:
            top = sym_stack.pop()

            if isinstance(top, Build):
                children = [ast_stack.pop() for _ in range(top.arity)][::-1]
                ast_stack.append(ASTNode(top.lhs, children))
                continue

            la_tok = tokens[0]
            la_type = la_tok.type

            if isinstance(top, TokenType):
                if top == la_type:
                    tokens.popleft()
                    if top is not TokenType.EOF:
                        ast_stack.append(ASTNode(f"{la_type.name}:{la_tok.lexeme}"))
                    continue
                self._err(f"Expected {top.name}, found {la_type.name}", la_tok)

            prod_num = self.table.get(top, {}).get(la_type)
            if prod_num is None:
                exp = ", ".join(t.name for t in self.table.get(top, {}))
                self._err(f"Unexpected {la_type.name}; expected one of: {exp}", la_tok)

            _, rhs = self.prod[prod_num]
            if isinstance(rhs, str):
                rhs = [rhs]

            sym_stack.append(Build(top, len(rhs)))
            for sym in reversed(rhs):
                if isinstance(sym, str) and sym in TokenType.__members__:
                    sym_stack.append(TokenType[sym])
                else:
                    sym_stack.append(sym)

        if len(ast_stack) != 1:
            raise RuntimeError("AST construction failed")

        return ast_stack[0]

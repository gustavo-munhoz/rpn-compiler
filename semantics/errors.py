from lexer.tokens import Token
from typing import Optional


class SemanticError(Exception):
    def __init__(self, msg: str, token: Optional[Token]):
        if token is None:
            full_msg = f"SemanticError: {msg}"
            super().__init__(full_msg)
            return

        self.msg = msg
        self.line = token.line
        self.col = token.col
        self.src_line = token.src_line

        pointer = " " * (self.col - 1) + "^"
        full_msg = (
            f"\n{self.src_line.rstrip()}\033[31m\n{pointer}\n"
            f"SemanticError: {self.msg} (line {self.line}, col {self.col})\033[0m\n"
        )
        super().__init__(full_msg)

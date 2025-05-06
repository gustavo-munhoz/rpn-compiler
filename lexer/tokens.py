from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    L_PAREN = auto()
    R_PAREN = auto()
    NUM_INT = auto()
    NUM_FLOAT = auto()
    ARITHMETIC_OP = auto()
    KEYWORD = auto()
    EOF = auto()


@dataclass
class Token:
    type: TokenType
    lexeme: str
    line: int
    col: int

    def __repr__(self) -> str:
        return f"<{self.type.name} {self.lexeme!r} @{self.line}:{self.col}>"

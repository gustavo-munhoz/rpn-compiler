from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    L_PAREN = auto()
    R_PAREN = auto()
    NUM_INT = auto()
    NUM_FLOAT = auto()
    ARITHMETIC_OP = auto()
    KW_RES = auto()
    KW_MEM = auto()
    KW_IF = auto()
    KW_THEN = auto()
    KW_ELSE = auto()
    KW_FOR = auto()
    EOF = auto()


@dataclass(slots=True)
class Token:
    type: TokenType
    lexeme: str
    line: int
    col: int
    src_line: str = ""

    def __repr__(self) -> str:
        return f"<{self.type.name} {self.lexeme!r} @{self.line}:{self.col}>"

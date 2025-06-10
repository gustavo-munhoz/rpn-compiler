from enum import Enum, auto


class SemanticType(Enum):
    INT = auto()
    FLOAT = auto()
    VOID = auto()
    ANY = auto()
    ERROR = auto()
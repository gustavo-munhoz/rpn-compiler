from enum import Enum, auto


class SemanticType(Enum):
    INT = auto()
    FLOAT = auto()
    VOID = auto()


class SignType(Enum):
    POSITIVE = auto()
    NEGATIVE = auto()
    ZERO = auto()
    UNKNOWN = auto()

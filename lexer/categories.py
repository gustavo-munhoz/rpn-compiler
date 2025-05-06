from enum import Enum, auto


class InputCategory(Enum):
    L_PAREN = auto()
    R_PAREN = auto()
    DIGIT = auto()
    DOT = auto()
    MINUS_OP = auto()
    OP_BIN = auto()
    SPACE = auto()
    EOF = auto()
    OTHER = auto()


def classify(c: str | None) -> InputCategory:
    if c is None:
        return InputCategory.EOF

    if c == '(':
        return InputCategory.L_PAREN

    if c == ')':
        return InputCategory.R_PAREN

    if c.isdigit():
        return InputCategory.DIGIT

    if c == '.':
        return InputCategory.DOT

    if c == '-':
        return InputCategory.MINUS_OP

    if c in "+*/|%^":
        return InputCategory.OP_BIN

    if c in ' \t\n\r':
        return InputCategory.SPACE

    return InputCategory.OTHER

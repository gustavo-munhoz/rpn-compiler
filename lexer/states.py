from enum import Enum, auto


class State(Enum):
    START = auto()
    INVALID = auto()

    # PARENTHESIS
    L_PAREN = auto()
    R_PAREN = auto()

    # NUMBERS
    NUM_INT = auto()
    FLOAT_POINT = auto()
    NUM_FRAC = auto()

    # ARITHMETIC OPERATORS
    OP_MINUS = auto()
    BIN_OP = auto()

    # RES
    SEQ_R = auto()
    SEQ_RE = auto()
    KW_RES = auto()

    # MEM
    SEQ_M = auto()
    SEQ_ME = auto()
    KW_MEM = auto()

    # IF
    SEQ_I = auto()
    KW_IF = auto()

    # THEN
    SEQ_T = auto()
    SEQ_TH = auto()
    SEQ_THE = auto()
    KW_THEN = auto()

    # ELSE
    SEQ_E = auto()
    SEQ_EL = auto()
    SEQ_ELS = auto()
    KW_ELSE = auto()

    # FOR
    SEQ_F = auto()
    SEQ_FO = auto()
    KW_FOR = auto()

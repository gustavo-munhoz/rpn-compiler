from .states import State as S
from .categories import InputCategory as C

T = {
    # PARENTHESIS
    (S.START, C.L_PAREN): S.L_PAREN,
    (S.START, C.R_PAREN): S.R_PAREN,

    # NUMBERS
    (S.START, C.DIGIT): S.NUM_INT,
    (S.NUM_INT, C.DIGIT): S.NUM_INT,
    (S.NUM_INT, C.DOT): S.FLOAT_POINT,
    (S.FLOAT_POINT, C.DIGIT): S.NUM_FRAC,
    (S.NUM_FRAC, C.DIGIT): S.NUM_FRAC,

    # OPERATORS
    (S.START, '-'): S.OP_MINUS,
    (S.OP_MINUS, C.DIGIT): S.NUM_INT,
    (S.START, C.OP_BIN): S.BIN_OP,

    # RES
    (S.START, 'R'): S.SEQ_R,
    (S.SEQ_R, 'E'): S.SEQ_RE,
    (S.SEQ_RE, 'S'): S.KW_RES,

    # MEM
    (S.START, 'M'): S.SEQ_M,
    (S.SEQ_M, 'E'): S.SEQ_ME,
    (S.SEQ_ME, 'M'): S.KW_MEM,

    # IF
    (S.START, 'I'): S.SEQ_I,
    (S.SEQ_I, 'F'): S.KW_IF,

    # THEN
    (S.START, 'T'): S.SEQ_T,
    (S.SEQ_T, 'H'): S.SEQ_TH,
    (S.SEQ_TH, 'E'): S.SEQ_THE,
    (S.SEQ_THE, 'N'): S.KW_THEN,

    # ELSE
    (S.START, 'E'): S.SEQ_E,
    (S.SEQ_E, 'L'): S.SEQ_EL,
    (S.SEQ_EL, 'S'): S.SEQ_ELS,
    (S.SEQ_ELS, 'E'): S.KW_ELSE,

    # FOR
    (S.START, 'F'): S.SEQ_F,
    (S.SEQ_F, 'O'): S.SEQ_FO,
    (S.SEQ_FO, 'R'): S.KW_FOR,
}

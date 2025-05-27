from lexer.tokens import TokenType

P = {
    1: ("<program>", ["<expr>", "<program_tail>"]),
    2: ("<expr>", ["L_PAREN", "<rpn>", "R_PAREN"]),
    3: ("<rpn>", ["KW_MEM"]),
    4: ("<rpn>", ["<operand>", "<rpn_tail>"]),
    5: ("<rpn_tail>", ["<op_unary>"]),
    6: ("<rpn_tail>", ["<operand>", "<op_binary>"]),
    7: ("<operand>", ["NUM_INT"]),
    8: ("<operand>", ["NUM_FLOAT"]),
    9: ("<operand>", ["<expr>"]),
    10: ("<op_unary>", ["KW_MEM"]),
    11: ("<op_unary>", ["KW_RES"]),
    12: ("<op_unary>", ["KW_IF"]),
    13: ("<op_binary>", ["KW_THEN"]),
    14: ("<op_binary>", ["KW_ELSE"]),
    15: ("<op_binary>", ["KW_FOR"]),
    16: ("<op_binary>", ["ARITHMETIC_OP"]),
    17: ("<program_tail>", ["<expr>", "<program_tail>"]),
    18: ("<program_tail>", []),
}

M = {
    "<program>": {
        TokenType.L_PAREN: 1
    },
    "<expr>": {
        TokenType.L_PAREN: 2
    },
    "<rpn>": {
        TokenType.KW_MEM: 3,
        TokenType.NUM_INT: 4,
        TokenType.NUM_FLOAT: 4,
        TokenType.L_PAREN: 4
    },
    "<rpn_tail>": {
        TokenType.KW_MEM: 5,
        TokenType.KW_RES: 5,
        TokenType.KW_IF: 5,
        TokenType.NUM_INT: 6,
        TokenType.NUM_FLOAT: 6,
        TokenType.L_PAREN: 6
    },
    "<operand>": {
        TokenType.NUM_INT: 7,
        TokenType.NUM_FLOAT: 8,
        TokenType.L_PAREN: 9
    },
    "<op_unary>": {
        TokenType.KW_MEM: 10,
        TokenType.KW_RES: 11,
        TokenType.KW_IF: 12
    },
    "<op_binary>": {
        TokenType.KW_THEN: 13,
        TokenType.KW_ELSE: 14,
        TokenType.KW_FOR: 15,
        TokenType.ARITHMETIC_OP: 16
    },
    "<program_tail>": {
        TokenType.L_PAREN: 17,
        TokenType.EOF: 18
    }
}

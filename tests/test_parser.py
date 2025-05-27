import pytest

from lexer.dfa import Lexer
from lexer.tokens import Token, TokenType
from parser.parser import LL1Parser
from parser.errors import LL1SyntaxError


def lex_and_parse(src: str):
    """Convenience helper: returns the AST root or raises LL1SyntaxError."""
    lexer = Lexer(src)
    tokens = list(lexer)

    if not tokens or tokens[-1].type is not TokenType.EOF:
        tokens.append(Token(TokenType.EOF, "", 0, 0))

    parser = LL1Parser()
    return parser.parse(tokens)


# ─────────────────────────────  SUCCESS  ─────────────────────────────
@pytest.mark.parametrize(
    "source",
    [
        "(1 2 +)",
        "((1 2 +) 3 *)",
        "(5 RES)",
        "(MEM)"
    ],
)
def test_valid_programs(source):
    ast = lex_and_parse(source)
    assert ast.label == "<program>"
    assert ast.children, "AST should not be empty"


# ─────────────────────────────  ERRORS  ───────────────────────────────
@pytest.mark.parametrize(
    "source",
    [
        "(1 2 +",
        "(1 + 2)",
        "(1 THEN)",
    ],
)
def test_invalid_programs_raise(source):
    with pytest.raises(LL1SyntaxError):
        lex_and_parse(source)

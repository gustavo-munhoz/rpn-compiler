import sys
from pathlib import Path

from lexer.dfa import Lexer
from lexer.tokens import Token, TokenType
from lexer.errors import LexError
from parser.parser import LL1Parser
from parser.errors import LL1SyntaxError
from parser.render import render_ast

GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0m"


def main(src_path_str: str) -> None:
    src_path = Path(src_path_str)
    if not src_path.is_file():
        print(f"{RED}[ERROR] File not found: {src_path}{RESET}")
        sys.exit(1)

    code = src_path.read_text(encoding="utf8")

    lexer = Lexer(code)
    tokens = [tok for tok in lexer]

    if not tokens or tokens[-1].type is not TokenType.EOF:
        if tokens:
            last = tokens[-1]
            line, col = last.line, last.col + len(last.lexeme)
            src_line = getattr(last, "src_line", "")
        else:
            line = col = 1
            src_line = ""
        tokens.append(Token(TokenType.EOF, "", line, col, src_line))

    parser = LL1Parser()

    try:
        ast_root = parser.parse(tokens)
    except (LexError, LL1SyntaxError) as e:
        sys.tracebacklimit = 0
        print(e)
        sys.exit(1)

    print(f"{GREEN}Syntax OK ✔{RESET}")

    out_png = src_path.with_suffix("").with_name(src_path.stem + "_ast.png")
    graph = render_ast(ast_root)
    graph.render(out_png.with_suffix("").as_posix(), format="png", cleanup=True)
    print(f"{GREEN}AST image saved to {out_png}{RESET}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"{RED}[ERROR] Usage: python -m main <source_file>{RESET}")
        sys.exit(1)
    main(sys.argv[1])

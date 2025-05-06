import sys
from pathlib import Path

from lexer.dfa import Lexer
from lexer.errors import LexError


GREEN = "\033[32m"; RED = "\033[31m"; RESET = "\033[0m"


def main(src_path_str: str) -> None:
    src_path = Path(src_path_str)

    if not src_path.is_file():
        print(f"{RED}[ERROR] File not found: {src_path}{RESET}")
        sys.exit(1)

    code = src_path.read_text(encoding="utf8")
    out_path = src_path.with_name(src_path.stem + "_output" + src_path.suffix)

    lexer = Lexer(code)
    tokens: list[str] = []

    try:
        for tok in lexer:
            tokens.append(f"{tok}\n")

    except LexError as e:
        sys.tracebacklimit = 0
        print(e)
        sys.exit(1)

    out_path.write_text("".join(tokens), encoding="utf8")
    print(f"\n{GREEN}[INFO] Tokens saved to {out_path}{RESET}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"{RED}[ERROR] Usage: python3 main.py <Source‑File>{RESET}")
        sys.exit(1)

    main(sys.argv[1])
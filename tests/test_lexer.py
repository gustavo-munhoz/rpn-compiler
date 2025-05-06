from pathlib import Path
from lexer.dfa import Lexer
from lexer.errors import LexError

import pytest

SAMPLES = Path("samples")
CASES = ["test1", "test2", "test3"]


def run_lexer(code: str) -> str:
    return "".join(f"{tok}\n" for tok in Lexer(code))


def load(path: Path) -> str:
    return path.read_text(encoding="utf8")


@pytest.mark.parametrize("case", CASES)
def test_text_file(case):
    src = load(SAMPLES / f"{case}/{case}.txt")
    want = load(SAMPLES / f"{case}/{case}_expected.txt")

    got = run_lexer(src)

    assert got == want, f"Mismatch in {case}"


def test_fail_case():
    src = load(SAMPLES / "test_fail/test_fail.txt")
    with pytest.raises(LexError):
        run_lexer(src)

from __future__ import annotations
from collections.abc import Iterator

from .transition_table import T
from .categories import classify
from .states import State as S
from .tokens import Token, TokenType
from .errors import LexError


ACCEPTING_STATES = {
    S.L_PAREN: TokenType.L_PAREN,
    S.R_PAREN: TokenType.R_PAREN,
    S.NUM_INT: TokenType.NUM_INT,
    S.NUM_FRAC: TokenType.NUM_FLOAT,
    S.BIN_OP: TokenType.ARITHMETIC_OP,
    S.OP_MINUS: TokenType.ARITHMETIC_OP,
    S.KW_RES: TokenType.KEYWORD,
    S.KW_MEM: TokenType.KEYWORD,
    S.KW_IF: TokenType.KEYWORD,
    S.KW_THEN: TokenType.KEYWORD,
    S.KW_ELSE: TokenType.KEYWORD,
    S.KW_FOR: TokenType.KEYWORD,
}

WHITESPACE = " \t\r\n"


class Lexer(Iterator[Token]):
    def __init__(self, src: str):
        self.src = src
        self.pos = 0
        self.line = 1
        self.col = 1
        self.state = S.START
        self.lexeme: list[str] = []
        self.pending_token: Token | None = None

    def _current_line_text(self) -> str:
        start = self.src.rfind('\n', 0, self.pos) + 1
        end = self.src.find('\n', self.pos)
        if end == -1:
            end = len(self.src)
        return self.src[start:end]

    def _peek(self):
        return self.src[self.pos] if self.pos < len(self.src) else None

    def _advance(self):
        char = self._peek()
        if char is not None:
            self.pos += 1
            if char == "\n":
                self.line += 1
                self.col = 1

            else:
                self.col += 1

        return char

    def _emit(self, token_type: TokenType) -> None:
        lex = "".join(self.lexeme)
        token = Token(token_type, lex, self.line, self.col - len(lex))
        self.pending_token = token
        self.lexeme.clear()
        self.state = S.START

    def _step(self) -> None:
        char = self._peek()

        if self.state is S.START and char in WHITESPACE:
            self._advance()
            return

        category = classify(char)
        next = (
            T.get((self.state, category)) or
            T.get((self.state, (char or '').upper()))
        )

        if next is None:
            if self.state in ACCEPTING_STATES:
                self._emit(ACCEPTING_STATES[self.state])
                return

            raise LexError(
                f"Unexpected character: '{char}'",
                self.line,
                self.col,
                self._current_line_text()
            )

        if char is not None:
            self.lexeme.append(char)
            self._advance()

        self.state = next

    def __next__(self) -> Token:
        if self.pending_token:
            token, self.pending_token = self.pending_token, None
            return token

        while self.pos <= len(self.src):
            if self.pos == len(self.src):
                if self.state in ACCEPTING_STATES and self.lexeme:
                    self._emit(ACCEPTING_STATES[self.state])
                    token, self.pending_token = self.pending_token, None
                    return token

                if self.state is S.START:
                    raise StopIteration

                raise LexError(
                    f"Incomplete lexeme",
                    self.line,
                    self.col,
                    self.src[self.line]
                )

            self._step()

            if self.pending_token:
                token, self.pending_token = self.pending_token, None
                return token

        raise StopIteration

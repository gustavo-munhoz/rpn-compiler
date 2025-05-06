class LexError(Exception):
    def __init__(self, msg: str, line: int, col: int, src_line: str):
        super().__init__(msg)
        self.msg = msg
        self.line = line
        self.col = col
        self.src_line = src_line

    def __str__(self) -> str:
        pointer = " " * (self.col - 1) + "^"
        return (
            f"\n{self.src_line.rstrip()}\033[31m\n{pointer}\n"
            f"LexError: {self.msg} (line {self.line}, col {self.col})\033[0m\n"
        )

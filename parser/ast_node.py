from dataclasses import dataclass, field
from typing import List, Optional

from semantics.types import SemanticType
from lexer.tokens import Token


@dataclass
class ASTNode:
    label: str
    children: List["ASTNode"] = field(default_factory=list)

    token: Optional[Token] = None

    eval_type: Optional[SemanticType] = None
    needs_cast_to_float: bool = False
    const_value: Optional[int | float] = None

    def add(self, *kids):
        self.children.extend(kids)

    def __repr__(self):
        if self.eval_type:
            return f"<ASTNode label={self.label!r} type={self.eval_type.name}>"
        return f"<ASTNode label={self.label!r}>"

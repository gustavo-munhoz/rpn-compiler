from dataclasses import dataclass, field
from typing import List


@dataclass
class ASTNode:
    label: str
    children: List["ASTNode"] = field(default_factory=list)

    def add(self, *kids):
        self.children.extend(kids)

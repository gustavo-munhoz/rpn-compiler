from dataclasses import dataclass
from typing import List, Optional

from lexer.tokens import Token
from .types import SemanticType, SignType


@dataclass
class AnnotatedASTNode:
    """Nó da árvore que contém as anotações da análise semântica."""
    label: str
    children: List["AnnotatedASTNode"]
    eval_type: SemanticType
    sign: SignType
    original_token: Optional[Token] = None
    needs_cast_to_float: bool = False

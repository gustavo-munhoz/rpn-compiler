import pytest

from semantics.analyzer import SemanticAnalyzer, AnnotatedASTNode, SemanticError
from semantics.types import SemanticType, SignType
from parser.ast_node import ASTNode
from lexer.tokens import Token


@pytest.fixture
def analyzer() -> SemanticAnalyzer:
    """Retorna uma nova instância do SemanticAnalyzer para cada teste."""
    return SemanticAnalyzer()


def test_literal_int(analyzer: SemanticAnalyzer):
    node = ASTNode(label="123")
    result = analyzer.analyze(node)
    assert result.eval_type == SemanticType.INT
    assert result.sign == SignType.POSITIVE


def test_literal_float(analyzer: SemanticAnalyzer):
    node = ASTNode(label="-10.5")
    result = analyzer.analyze(node)
    assert result.eval_type == SemanticType.FLOAT
    assert result.sign == SignType.NEGATIVE


def test_literal_zero(analyzer: SemanticAnalyzer):
    node = ASTNode(label="0")
    result = analyzer.analyze(node)
    assert result.eval_type == SemanticType.INT
    assert result.sign == SignType.ZERO


# --- Testes para Operadores Binários ---

def test_binary_op_int_int(analyzer: SemanticAnalyzer):
    ast = ASTNode("+", [ASTNode("5"), ASTNode("3")])
    result = analyzer.analyze(ast)
    assert result.eval_type == SemanticType.INT
    assert result.sign == SignType.UNKNOWN  # Sinal de expressão é desconhecido


def test_binary_op_float_float(analyzer: SemanticAnalyzer):
    ast = ASTNode("*", [ASTNode("2.5"), ASTNode("4.0")])
    result = analyzer.analyze(ast)
    assert result.eval_type == SemanticType.FLOAT


def test_binary_op_autocasting(analyzer: SemanticAnalyzer):
    ast = ASTNode("-", [ASTNode("10"), ASTNode("0.5")])
    result = analyzer.analyze(ast)
    assert result.eval_type == SemanticType.FLOAT
    # Verifica se o nó INT foi marcado para cast
    assert result.children[0].needs_cast_to_float is True
    assert result.children[1].needs_cast_to_float is False


def test_binary_op_division_by_zero_error(analyzer: SemanticAnalyzer):
    ast = ASTNode("/", [ASTNode("100"), ASTNode("0")])
    with pytest.raises(SemanticError) as err:
        analyzer.analyze(ast)
    assert "Division by literal zero" in str(err.value)


def test_binary_op_exponent_type_error(analyzer: SemanticAnalyzer):
    ast = ASTNode("^", [ASTNode("10"), ASTNode("2.0")])
    with pytest.raises(SemanticError) as err:
        analyzer.analyze(ast)
    assert "exponent ('^') must be an INT" in str(err.value)


# --- Testes para o Operador RES ---

def test_res_valid(analyzer: SemanticAnalyzer):
    # Simula a análise de uma expressão na linha 2 (índice 1) que usa RES
    ast = ASTNode("RES", [ASTNode("1")])
    result = analyzer.analyze(ast, line_index=1)
    assert result.eval_type == SemanticType.FLOAT
    assert result.sign == SignType.UNKNOWN


def test_res_out_of_bounds_error(analyzer: SemanticAnalyzer):
    ast = ASTNode("RES", [ASTNode("3")])
    with pytest.raises(SemanticError) as err:
        # Tenta acessar 3 linhas atrás, mas estamos apenas na linha 2 (índice 1)
        analyzer.analyze(ast, line_index=1)
    assert "Cannot 'RES' 3 lines back" in str(err.value)


def test_res_operand_not_int_error(analyzer: SemanticAnalyzer):
    ast = ASTNode("RES", [ASTNode("1.0")])
    with pytest.raises(SemanticError) as err:
        analyzer.analyze(ast)
    assert "'RES' expects an INT operand" in str(err.value)


# --- Testes para Estruturas de Controle ---

def test_for_loop_valid(analyzer: SemanticAnalyzer):
    # (5 (10.0) FOR) -> o corpo é um float, então o resultado do laço é float
    ast = ASTNode("FOR", [ASTNode("5"), ASTNode("10.0")])
    result = analyzer.analyze(ast)
    assert result.eval_type == SemanticType.FLOAT


def test_for_loop_counter_not_int_error(analyzer: SemanticAnalyzer):
    ast = ASTNode("FOR", [ASTNode("5.0"), ASTNode("10")])
    with pytest.raises(SemanticError) as err:
        analyzer.analyze(ast)
    assert "loop count for 'FOR' must be an INT" in str(err.value)


def test_if_then_else_valid(analyzer: SemanticAnalyzer):
    # ((1 IF) (10) THEN (20) ELSE)
    node_if = ASTNode("IF", [ASTNode("1")])
    node_then = ASTNode("THEN", [node_if, ASTNode("10")])
    ast = ASTNode("ELSE", [node_then, ASTNode("20")])
    result = analyzer.analyze(ast)
    assert result.eval_type == SemanticType.INT


def test_if_then_else_type_mismatch_error(analyzer: SemanticAnalyzer):
    # Força os tipos dos ramos a serem diferentes (assumindo que auto_cast não se aplica aqui)
    # Esta é a lógica que implementamos: IF/ELSE precisa de tipos idênticos
    node_if = ASTNode("IF", [ASTNode("1")])
    node_then = ASTNode("THEN", [node_if, ASTNode("10")])  # Ramo THEN é INT
    ast = ASTNode("ELSE", [node_then, ASTNode("20.0")])  # Ramo ELSE é FLOAT

    # Temporariamente desativa o autocast para este teste específico
    analyzer.auto_cast = False
    with pytest.raises(SemanticError) as err:
        analyzer.analyze(ast)
    assert "Incompatible types in conditional branches" in str(err.value)


def test_incomplete_then_is_error(analyzer: SemanticAnalyzer):
    incomplete_then_node = ASTNode("THEN", [ASTNode("IF", [ASTNode("1")]), ASTNode("10")])

    program_ast = ASTNode("<program>", children=[incomplete_then_node])

    with pytest.raises(SemanticError) as err:
        analyzer.analyze(program_ast)

    assert "Incomplete conditional" in str(err.value)


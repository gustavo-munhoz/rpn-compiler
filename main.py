import sys
from pathlib import Path
import argparse

from lexer.dfa import Lexer
from lexer.tokens import Token, TokenType
from lexer.errors import LexError
from parser.ast_node import ASTNode
from parser.parser import LL1Parser
from parser.errors import LL1SyntaxError
from parser.render import render_ast, render_annotated_ast
from semantics.analyzer import SemanticAnalyzer
from semantics.errors import SemanticError

from generator.generator import CodeGenerator, generate_full_header, generate_data_segment

GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0m"


def render_image(src_path, ast):
    out_png = src_path.with_suffix("").with_name(src_path.stem + "_ast.png")
    graph = render_ast(ast)
    graph.render(out_png.with_suffix("").as_posix(), format="png", cleanup=True)
    print(f"{GREEN}AST image saved to {out_png}{RESET}")


def write_assembly_file(code: str, src_path: Path):
    """Salva o código assembly final em um arquivo .asm."""
    output_file = src_path.with_suffix(".asm")
    output_file.write_text(code, encoding="utf8")
    print(f"{GREEN}Assembly file saved to {output_file}{RESET}")


def count_program_lines(program_node: ASTNode) -> int:
    """
    Percorre a AST gerada pela gramática para contar o número total de linhas/expressões.
    """
    # Se o programa estiver vazio ou malformado
    if not program_node or program_node.label != '<program>' or not program_node.children:
        return 0

    # A primeira linha está sempre presente
    count = 1

    # Pega o início da "cauda" recursiva do programa
    current_tail = program_node.children[1]

    # Percorre a "lista encadeada" de <program_tail>
    while current_tail and current_tail.label == '<program_tail>' and current_tail.children:
        count += 1
        # Avança para o próximo nó <program_tail>
        current_tail = current_tail.children[1]

    return count


def main(src_path_str: str, auto_cast: bool) -> None:
    src_path = Path(src_path_str)
    if not src_path.is_file():
        print(f"{RED}[ERROR] File not found: {src_path}{RESET}")
        sys.exit(1)

    code = src_path.read_text(encoding="utf8")

    try:
        # --- FASE 1: LEXER ---
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

        # --- FASE 2: PARSER ---
        parser = LL1Parser()
        ast_root = parser.parse(tokens)
        print(f"{GREEN}Syntax OK ✔{RESET}")
        render_image(src_path, ast_root)

        # --- FASE 3: ANÁLISE SEMÂNTICA ---
        analyzer = SemanticAnalyzer()
        annotated_ast_root = analyzer.analyze(ast_root)
        print(f"{GREEN}Semantics OK ✔{RESET}")

        out_png = src_path.with_suffix("").with_name(src_path.stem + "_annotated_ast.png")
        graph = render_annotated_ast(annotated_ast_root)
        graph.render(out_png.with_suffix("").as_posix(), format="png", cleanup=True)
        print(f"{GREEN}Annotated AST image saved to {out_png}{RESET}")

        # --- FASE 4: GERAÇÃO DE CÓDIGO ---
        print("Starting code generation...")
        code_gen = CodeGenerator()
        code_gen.generate(ast_root)
        print(f"{GREEN}Code Generation OK ✔{RESET}")

        # --- FASE 5: MONTAGEM DO ARQUIVO FINAL ---
        header = generate_full_header()
        main_code = code_gen.get_main_code()
        temp_defs = code_gen.get_temp_definitions()

        # O tamanho do array de resultados é 2 bytes por linha
        num_lines = count_program_lines(ast_root)
        results_byte_count = num_lines * 2
        data_seg = generate_data_segment(results_byte_count, temp_defs)

        end_loop = "end:\n\trjmp end\n"

        full_assembly = header + main_code + "\n" + end_loop + data_seg

        write_assembly_file(full_assembly, src_path)

    except (LexError, LL1SyntaxError, SemanticError) as e:
        sys.tracebacklimit = 0
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    cli_parser = argparse.ArgumentParser(description="Compilador para a linguagem RPN.")
    cli_parser.add_argument("source_file", help="O arquivo de código fonte para compilar.")
    cli_parser.add_argument("--no-cast", action="store_false", dest="auto_cast",
                            help="Desativa o type casting automático de INT para FLOAT.")

    args = cli_parser.parse_args()

    main(args.source_file, args.auto_cast)

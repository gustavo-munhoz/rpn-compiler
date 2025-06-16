import struct

from .subroutines.add_f16 import ADD_F16
from .subroutines.div_f16 import DIV_F16
from .subroutines.div_int_f16 import DIV_INT_F16
from .subroutines.is_f16_zero import IS_F16_ZERO
from .subroutines.mem import SET_MEM, GET_MEM
from .subroutines.mod_f16 import MOD_F16
from .subroutines.mul_f16 import MUL_F16
from .subroutines.pow_f16 import POW_F16
from .subroutines.res_op import RES_OP
from .subroutines.sub_f16 import SUB_F16
from .subroutines.utils import USART_CONFIG, PRINT_F16, SERIAL_COMM
from parser.ast_node import ASTNode


class TempVarManager:
    """
    Gerencia a criação de variáveis temporárias e suas definições para o segmento de dados.
    """

    def __init__(self):
        self.count = 0
        self.definitions = []

    def new_temp(self) -> str:
        """Cria um novo nome de variável temporária e armazena sua definição."""
        self.count += 1
        temp_name = f"T{self.count}"
        # Armazena a definição para ser usada no segmento de dados depois
        self.definitions.append(f"{temp_name}_L: .byte 1")
        self.definitions.append(f"{temp_name}_H: .byte 1")
        return temp_name

    def get_temp_variables_definitions(self) -> str:
        """Retorna todas as definições de variáveis como uma única string."""
        return "\n".join(self.definitions)


def float_to_ieee754_half(value: float) -> tuple[int, int]:
    """
    Converte um float para dois bytes (low, high) no formato IEEE 754 half-precision.
    """
    # 'e' é o especificador de formato para half-precision float (16 bits)
    # '<' garante o byte order little-endian, se necessário (geralmente padrão)
    packed_bytes = struct.pack('<e', value)
    low_byte = packed_bytes[0]
    high_byte = packed_bytes[1]
    return low_byte, high_byte


def generate_full_header():
    header_parts = [
        '.include "m328Pdef.inc"',
        '.macro store',
        '\tldi\tR16, @1',
        '\tsts\t@0, R16',
        '.endm',
        USART_CONFIG,
        '\trjmp main',
        PRINT_F16,
        SERIAL_COMM,
        ADD_F16,
        SUB_F16,
        MUL_F16,
        DIV_F16,
        DIV_INT_F16,
        MOD_F16,
        POW_F16,
        RES_OP,
        SET_MEM,
        GET_MEM,
        IS_F16_ZERO,
        '\nmain:'
    ]

    return '\n'.join(header_parts) + '\n'


def generate_data_segment(results_size: int, temp_vars_defs: str):
    """Monta a string para o segmento de dados (.dseg) do assembly."""
    return f"""
.dseg
{temp_vars_defs}

results: .byte {results_size}
    .equ lo8_results = ((results) & 0xFF)
    .equ hi8_results = (((results) >> 8) & 0xFF)
storeVal: .byte 2
    .equ BUFFER_ADDR = 0x100
    .equ BUFFER_SIZE = 11
"""


class LabelGenerator:
    """Gera nomes de labels únicos para saltos no assembly."""

    def __init__(self):
        self.count = 0

    def new_label(self, prefix: str = "L") -> str:
        self.count += 1
        return f"{prefix}_{self.count}"


class CodeGenerator:
    """
    Percorre a AST anotada e gera o código assembly final.
    """

    def __init__(self):
        self.main_code = []
        self.temp_manager = TempVarManager()
        self.label_gen = LabelGenerator()
        self.op_map = {
            '+': 'add_f16', '-': 'sub_f16', '*': 'mul_f16', '^': 'pow_f16',
            '|': 'div_f16', '/': 'div_int_f16', '%': 'mod_f16'
        }

    def get_main_code(self) -> str:
        """Retorna o corpo principal do código assembly gerado."""
        return "\n".join(self.main_code)

    def get_temp_definitions(self) -> str:
        """Retorna as definições de .byte para todas as variáveis temporárias usadas."""
        return "\n".join(self.temp_manager.definitions)

    def generate(self, ast_root: ASTNode):
        """
        Ponto de entrada que inicia a geração de código, navegando a
        estrutura recursiva de <program> e <program_tail>.
        """
        if not ast_root or ast_root.label != '<program>' or not ast_root.children:
            return

        current_expr_node = ast_root.children[0]
        current_tail_node = ast_root.children[1]
        line_index = 0

        self._process_line(current_expr_node, line_index)

        line_index = 1
        while current_tail_node and current_tail_node.label == '<program_tail>' and current_tail_node.children:
            current_expr_node = current_tail_node.children[0]
            self._process_line(current_expr_node, line_index)

            current_tail_node = current_tail_node.children[1]
            line_index += 1

    def _process_line(self, line_node: ASTNode, line_index: int):
        """
        Método auxiliar que gera o código para uma única linha de expressão,
        salvando e imprimindo seu resultado final.
        """
        self.main_code.append(f"\n; --- Line {line_index + 1} ---")

        final_loc = self._generate_expression(line_node, line_index)

        if not final_loc:
            return

        # Adiciona código para salvar o resultado final no array 'results'
        self.main_code.append(f"; Store result of line {line_index + 1} from {final_loc} into results array")
        self.main_code.append(self._generate_load_operand(final_loc, "r24", "r25"))

        offset = line_index * 2
        self.main_code.append(f"    STS results+{offset}, r24")
        self.main_code.append(f"    STS results+{offset + 1}, r25")

        # Adiciona código para imprimir o resultado via serial
        self.main_code.append("    RCALL print_f16")

    def _generate_expression(self, node: ASTNode, line_index: int) -> str:
        """
        Método despachante recursivo que lida com a otimização de forma segura.
        """
        if node.const_value is not None:
            temp_var = self.temp_manager.new_temp()
            self.main_code.append(f"; Attempting to use constant folded value: {node.const_value}")

            try:
                # --- CORREÇÃO AQUI ---
                # Garante que o valor seja um float antes de passá-lo para a função de empacotamento.
                const_as_float = float(node.const_value)

                low, high = float_to_ieee754_half(const_as_float)

                # Se for bem-sucedido, gera o código otimizado.
                # Usamos o node.const_value original para a chamada do _generate_load_operand
                # que também espera uma string de um número.
                self.main_code.append(self._generate_load_operand(str(node.const_value), "r24", "r25"))
                self.main_code.append(f"    STS {temp_var}_L, r24")
                self.main_code.append(f"    STS {temp_var}_H, r25")
                return temp_var

            except (OverflowError, struct.error):
                # Agora capturamos ambos os erros possíveis.
                # Se der erro, o valor é grande demais ou de tipo incorreto.
                self.main_code.append(
                    f"; Constant value {node.const_value} is out of range for 16-bit float. Generating full expression instead.")
                pass

        if self._is_number(node.label):
            return self._generate_literal(node)
        elif node.label in self.op_map:
            return self._generate_binary_op(node, line_index)
        elif node.label == 'ELSE':
            return self._generate_if_then_else(node, line_index)
        elif node.label == 'FOR':
            return self._generate_for(node, line_index)
        elif node.label == 'RES':
            return self._generate_res(node, line_index)
        elif node.label == 'MEM':
            return self._generate_mem(node, line_index)

        raise NotImplementedError(f"Code generation for node '{node.label}' is not implemented.")

    def _is_number(self, s: str) -> bool:
        try:
            float(s); return True
        except (ValueError, TypeError):
            return False

    def _generate_literal(self, node: ASTNode) -> str:
        # Literais não geram código sozinhos, apenas retornam seu valor como uma string.
        # O nó pai que os usa é responsável por gerar o LDI.
        return node.label

    def _generate_load_operand(self, operand_loc: str, reg_low: str, reg_high: str) -> str:
        if self._is_number(operand_loc):
            value = float(operand_loc)
            low, high = float_to_ieee754_half(value)
            return f"    LDI {reg_low}, {low}\n    LDI {reg_high}, {high}"
        else:
            return f"    LDS {reg_low}, {operand_loc}_L\n    LDS {reg_high}, {operand_loc}_H"

    def _generate_binary_op(self, node: ASTNode, line_index: int) -> str:
        left_loc = self._generate_expression(node.children[0], line_index)
        right_loc = self._generate_expression(node.children[1], line_index)

        subroutine = self.op_map[node.label]
        temp_result = self.temp_manager.new_temp()

        code = [
            f"; Binary op: {left_loc} {node.label} {right_loc}",
            self._generate_load_operand(left_loc, "r24", "r25"),
            self._generate_load_operand(right_loc, "r22", "r23"),
            f"    RCALL {subroutine}",
            f"    STS {temp_result}_L, r24",
            f"    STS {temp_result}_H, r25"
        ]
        self.main_code.extend(code)
        return temp_result

    def _generate_if_then_else(self, node: ASTNode, line_index: int) -> str:
        then_node = node.children[0]
        else_branch = node.children[1]
        if_node = then_node.children[0]
        then_branch = then_node.children[1]
        condition = if_node.children[0]

        else_label = self.label_gen.new_label("else")
        end_if_label = self.label_gen.new_label("endif")

        # Cria uma variável temporária para guardar o resultado da expressão.
        temp_final = self.temp_manager.new_temp()

        # Avalia a condição
        condition_loc = self._generate_expression(condition, line_index)
        self.main_code.append(f"; IF-ELSE expression")
        self.main_code.append(self._generate_load_operand(condition_loc, "r24", "r25"))
        self.main_code.append("    RCALL is_f16_zero")
        self.main_code.append(f"    BREQ {else_label}")

        # Bloco THEN
        then_loc = self._generate_expression(then_branch, line_index)
        self.main_code.append(self._generate_load_operand(then_loc, "r24", "r25"))
        self.main_code.append(f"    STS {temp_final}_L, r24")  # Salva o resultado na temp
        self.main_code.append(f"    STS {temp_final}_H, r25")
        self.main_code.append(f"    RJMP {end_if_label}")

        # Bloco ELSE
        self.main_code.append(f"{else_label}:")
        else_loc = self._generate_expression(else_branch, line_index)
        self.main_code.append(self._generate_load_operand(else_loc, "r24", "r25"))
        self.main_code.append(f"    STS {temp_final}_L, r24")  # Salva o resultado na temp
        self.main_code.append(f"    STS {temp_final}_H, r25")

        self.main_code.append(f"{end_if_label}:")

        # Retorna a localização do resultado final.
        return temp_final

    def _generate_for(self, node: ASTNode, line_index: int) -> str:
        iterations_node, body_node = node.children

        loop_start_label = self.label_gen.new_label("for_start")
        loop_end_label = self.label_gen.new_label("for_end")

        # Cria uma variável temporária ANTES do laço para guardar o último resultado.
        temp_for_result = self.temp_manager.new_temp()

        # Configura o contador do loop
        self.main_code.append(f"; FOR loop setup")
        iterations_loc = self._generate_expression(iterations_node, line_index)
        self.main_code.append(self._generate_load_operand(iterations_loc, "r24", "r25"))
        self.main_code.append("    MOV r22, r24")
        self.main_code.append("    MOV r23, r25")
        self.main_code.append("    RCALL f16_to_uint16")
        self.main_code.append("    MOV r20, r26 ; Usando r20 como contador")

        self.main_code.append(f"{loop_start_label}:")
        self.main_code.append("    TST r20")
        self.main_code.append(f"    BREQ {loop_end_label}")

        # Executa o corpo e obtém a localização do resultado da iteração
        body_result_loc = self._generate_expression(body_node, line_index)
        # Salva o resultado desta iteração na nossa variável temporária
        self.main_code.append(self._generate_load_operand(body_result_loc, "r24", "r25"))
        self.main_code.append(f"    STS {temp_for_result}_L, r24")
        self.main_code.append(f"    STS {temp_for_result}_H, r25")

        self.main_code.append("    DEC r20")
        self.main_code.append(f"    RJMP {loop_start_label}")

        self.main_code.append(f"{loop_end_label}:")

        # Retorna a localização do último valor calculado.
        return temp_for_result

    def _generate_res(self, node: ASTNode, line_index: int) -> str:
        child_node = node.children[0]
        n_value = int(child_node.label)

        target_line_index = line_index - n_value

        temp_result = self.temp_manager.new_temp()
        code = [
            f"; RES op: get result from {n_value} lines back (accessing results index {target_line_index})",
            f"    LDI r24, {target_line_index}",
            "    RCALL res_op",
            f"    STS {temp_result}_L, r24",
            f"    STS {temp_result}_H, r25",
        ]
        self.main_code.extend(code)
        return temp_result

    def _generate_mem(self, node: ASTNode, line_index: int) -> str:
        temp_result = self.temp_manager.new_temp()

        if node.children:
            operand_loc = self._generate_expression(node.children[0], line_index)
            code = [
                f"; MEM write",
                self._generate_load_operand(operand_loc, "r24", "r25"),
                "    RCALL set_mem",
                f"    STS {temp_result}_L, r24",
                f"    STS {temp_result}_H, r25"
            ]
        # MEM de leitura (não tem filhos)
        else:
            code = [
                f"; MEM read",
                "    RCALL get_mem",
                f"    STS {temp_result}_L, r24",
                f"    STS {temp_result}_H, r25"
            ]

        self.main_code.extend(code)
        return temp_result

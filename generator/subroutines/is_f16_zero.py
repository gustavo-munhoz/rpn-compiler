IS_F16_ZERO = """
;-----------------------------------------------------
; is_f16_zero: Checa se r25:r24 é +/- 0.0
; Entrada:   r25:r24 - valor float16
; Saída:     Flag Z do SREG é setada se o valor for zero.
; Registradores modificados (clobbers): r16
;-----------------------------------------------------
is_f16_zero:
    push r16
    mov r16, r25
    andi r16, 0x7F
    or r16, r24
    pop r16
    ret
"""
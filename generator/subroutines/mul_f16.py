MUL_F16 = """
;---------------------------------------------------------
; mul_f16: Multiplicação de dois half-precision IEEE-754
; Entradas: Operando A em R25:R24, Operando B em R23:R22
; Saída: Resultado em R25:R24
; Callee-Saved: r18-r21, r26-r27, r30-r31
; Volatile: r0, r1, r16, r17, r28, r29
;---------------------------------------------------------
mul_f16:
    push r18
    push r19
    push r20
    push r21
    push r26
    push r27
    push r30
    push r31

    ; --- Calcular Sinal do Resultado -> r20 (Callee-Saved) ---
    mov R20, R25
    andi R20, 0x80    ; Sinal A
    mov R21, R23
    andi R21, 0x80    ; Sinal B
    eor R20, R21      ; r20 = Sinal Resultado (0x00 ou 0x80)

    ; --- Extrair Expoentes -> r26, r27 (Callee-Saved) ---
    mov R26, R25
    andi R26, 0x7C    ; Isolar bits de expoente A
    lsr R26
    lsr R26           ; r26 = Expoente A (0-31, com bias)
    mov R27, R23
    andi R27, 0x7C    ; Isolar bits de expoente B
    lsr R27
    lsr R27           ; r27 = Expoente B (0-31, com bias)

    ; --- Checar Operandos Zero --- 
    tst R26
    brne check_b_zero
    mov R28, R24
    mov R29, R25
    andi R29, 0x03
    or R28, R29
    brne check_b_zero
    mov R25, R20
    ldi R24, 0x00
    rjmp mul_cleanup

check_b_zero:
    tst R27
    brne extract_mantissas
    mov R28, R22
    mov R29, R23
    andi R29, 0x03
    or R28, R29
    brne extract_mantissas
    mov R25, R20
    ldi R24, 0x00
    rjmp mul_cleanup

extract_mantissas:
    ; --- Extrair Mantissas (11 bits com implícito) ---
    mov R18, R24
    mov R19, R25
    andi R19, 0x03
    ldi R21, 1
    tst R26
    brne norm_a
    mov R26, R21
    rjmp extract_b
norm_a:
    ori R19, 0x04

extract_b:
    mov R16, R22
    mov R17, R23
    andi R17, 0x03
    ldi R21, 1
    tst R27
    brne norm_b
    mov R27, R21
    rjmp calc_exp
norm_b:
    ori R17, 0x04

calc_exp:
    add R26, R27
    subi R26, 15

    ; --- Multiplicar Mantissas (32 bits) ---
    clr R28
    clr R29
    clr R30
    clr R31
    mul R18, R16      ; AL * BL
    mov R28, r0
    mov R29, r1
    mul R18, R17      ; AL * BH
    add R29, r0
    adc R30, r1
    clr r0
    adc r31, r0
    mul R19, R16      ; AH * BL
    add R29, r0
    adc R30, r1
    clr r0
    adc r31, r0
    mul R19, R17      ; AH * BH
    add R30, r0
    adc R31, r1

    sbrc r30, 5
    rjmp mul_did_overflow
mul_no_overflow:
    rjmp mantissa_ready
mul_did_overflow:
    lsr r31
    ror r30
    ror r29
    ror r28
    inc r26
mantissa_ready:

mul_check_exponent:
    mov r19, r28
    or  r19, r29
    or  r19, r30
    or  r19, r31
    brne check_exp_non_zero
    mov R25, R20
    ldi R24, 0x00
    rjmp mul_cleanup
check_exp_non_zero:
    cpi R26, 31
    brsh exponent_overflow_final
    cpi R26, 1
    brsh pack_result_new
exponent_underflow_final:
    ldi R24, 0x00
    mov R25, R20
    rjmp mul_cleanup
exponent_overflow_final:
    ldi R24, 0x00
    ldi R25, 0x7C
    or R25, R20
    rjmp mul_cleanup

pack_result_new:
    mov R25, R20
    mov R21, R26
    lsl R21
    lsl R21
    andi R21, 0x7C
    or R25, R21
    mov R21, R30
    andi R21, 0x0C
    lsr R21
    lsr R21
    or R25, R21
    mov R21, R30
    andi R21, 0x03
    lsl R21
    lsl R21
    lsl R21
    lsl R21
    lsl R21
    lsl R21
    mov R24, R21
    mov R21, R29
    andi R21, 0xFC
    lsr R21
    lsr R21
    or R24, R21

mul_cleanup:
    pop r31
    pop r30
    pop r27
    pop r26
    pop r21
    pop r20
    pop r19
    pop r18
    ret
"""
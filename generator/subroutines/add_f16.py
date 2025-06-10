ADD_F16 = """
;---------------------------------------------------------
; add_f16: Adição de dois half-precision IEEE-754
; Entradas: Operando A em R25:R24, Operando B em R23:R22
; Saída: Resultado em R25:R24
; Callee-Saved: r18, r19, r20, r21, r26, r27, r30
; Volatile: r2, r16, r17, r28, r29
;---------------------------------------------------------
add_f16:
    push R18
    push R19
    push R20
    push R21
    push R26
    push R27
    push R30

    ; Extrair Sinais -> r28, r29 (Volatile)
    mov R28, R25
    andi R28, 0x80
    mov R29, R23
    andi R29, 0x80\n

    ; Extrair Expoentes -> r26, r27 (Callee-Saved)
    mov R26, R25
    andi R26, 0x7C
    lsr R26
    lsr R26
    mov R27, R23
    andi R27, 0x7C
    lsr R27
    lsr R27\n

    ; Extrair Mantissas -> r19:r18(A), r17:r16(B)
    mov R18, R24
    mov R19, R25
    andi R19, 0x03
    tst R26
    brne add_norm_a
    ldi r16, 1
    mov R26, r16
    rjmp add_extract_b
add_norm_a:
    ori R19, 0x04

add_extract_b:
    mov R16, R22
    mov R17, R23
    andi R17, 0x03
    tst R27
    brne add_norm_b
    ldi r16, 1
    mov R27, r16
    rjmp align_mantissas_start
add_norm_b:
    ori R17, 0x04

align_mantissas_start:
    cp R26, R27
    brsh exp_a_ge_b
    ; Expoente B > A, deslocar A à direita
    mov R30, R27
    mov r2, R27
    sub r2, R26
shift_a_loop:
    tst r2
    breq align_done
    lsr R19
    ror R18
    dec r2
    rjmp shift_a_loop
    rjmp align_done\n
exp_a_ge_b:
    ; Expoente A >= B, deslocar B à direita
    mov R30, R26
    mov r2, R26
    sub r2, R27
shift_b_loop:
    tst r2
    breq align_done
    lsr R17
    ror R16
    dec r2
    rjmp shift_b_loop\n
align_done:\n

    ; Adicionar / Subtrair Mantissas
    ; Guarda Sinal em r21 (Callee-Saved)
    cp R28, R29
    breq same_signs\n
    ; --- Sinais Diferentes ---
    mov R20, R19        ; Guardar cópia de r19:r18 para comparação
    cp R19, R17
    brne mantissa_cmp_decided
    cp R18, R16
    brne mantissa_cmp_decided
    ; Mantissas iguais, resultado é zero
    clr R18
    clr R19
    clr R30
    clr r21
    rjmp pack_result\n
mantissa_cmp_decided:
    brlo b_greater_sub
a_ge_b_sub:
    ; A >= B, subtrair B de A
    sub R18, R16
    sbc R19, R17
    mov r21, R28        ; Sinal de A
    rjmp normalize_after_sub\n
b_greater_sub:
    ; B > A, subtrair A de B
    sub R16, R18
    sbc R17, R19
    mov r21, R29        ; Sinal de B
    mov R18, R16        ; Mover resultado para r19:r18
    mov R19, R17
    rjmp normalize_after_sub\n
same_signs:
    ; --- Sinais Iguais (Adição) ---
    add R18, R16
    adc R19, R17
    mov r21, R28
    rjmp normalize_check_add\n

normalize_check_add:
    ; Verificar se resultado é zero
    mov R16, R19
    or R16, R18
    brne check_add_overflow
    clr R30
    rjmp pack_result\n
check_add_overflow:
    sbrc R19, 3         ; Verificar overflow (bit 11)
    rjmp adjust_add_overflow
    rjmp add_normalize_loop_entry\n
normalize_after_sub:
    ; Verificar se resultado é zero
    mov R16, R19
    or R16, R18
    brne add_normalize_loop_entry
    clr R30
    clr r21             ; Zero positivo
    rjmp pack_result\n
add_normalize_loop_entry:
    ; Normalizar resultado (bit implícito em R19 bit 2)
add_normalize_loop:
    sbrc R19, 2         ; Verificar se bit implícito está em posição
    rjmp normalize_done
    ; Deslocar mantissa à esquerda até posicionar bit implícito
    lsl R18
    rol R19
    ; Ajustar expoente
    dec R30
    ; Verificar denormalização
    cpi R30, 1
    brsh add_normalize_loop  ; Se R30 >= 1, continuar normalizando
handle_denormalized:
    ; Resultado denormalizado, retornar zero
    clr R19
    clr R18
    clr R30
    rjmp pack_result\n
adjust_add_overflow:
    lsr R19
    ror R18
    inc R30
    cpi R30, 31
    brsh handle_overflow
normalize_done:
    rjmp pack_result\n
handle_overflow:
    ldi R19, 0x00
    ldi R18, 0x00
    ldi R30, 31
    rjmp pack_result\n

pack_result:
    mov R16, R30
    lsl R16
    lsl R16
    andi R16, 0x7C      ; Expoente em bits 6-2
    ; Montar byte alto do resultado
    mov R25, R16        ; Bits de expoente
    mov R16, R19
    andi R16, 0x03      ; Bits 1-0 da mantissa alta
    or R25, R16         ; Combinar expoente com mantissa alta
    or R25, r21         ; Aplicar bit de sinal
    mov R24, R18

add_cleanup:
    pop R30
    pop R27
    pop R26
    pop R21
    pop R20
    pop R19
    pop R18
    ret
"""

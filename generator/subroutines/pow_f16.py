POW_F16 = """
;-----------------------------------------------------
; pow_f16: Potência A^B, onde B é float16 representando int >= 1
; Entrada Base A: r25:r24
; Entrada Expo B: r23:r22
; Saida: r25:r24 = A^B
; Usa: r0,r1,r2,r16-r23,r26-r31
; Chama: f16_to_uint16, mul_f16
;-----------------------------------------------------
pow_f16:
    push r0
    push r1
    push r2
    push r3
    push r16
    push r17
    push r18
    push r19
    push r20
    push r21
    push r22
    push r23
    push r26
    push r27
    push r28
    push r29
    push r30
    push r31
    ; --- Converter Expoente B (float) para uint16 --- 
    call f16_to_uint16   ; Entrada r23:r22, Saída b_int em r27:r26

    ; --- Salvar Base A (CurrentPower) e Inicializar Result --- 
    mov r21, r24         ; Copiar A low para CurrentPower low (r21)
    mov r20, r25         ; Copiar A high para CurrentPower high (r20)
    ; --- Checar se b_int == 1 --- 
    ldi r16, 1           ; Comparar b_int com 1
    ldi r17, 0
    cp r26, r16          ; Compara low byte
    cpc r27, r17         ; Compara high byte
    breq pow_cleanup     ; Se b_int == 1, A (resultado) já está em r25:r24. Fim.

    ; --- Inicializar Resultado = 1.0 --- 
    ldi r25, 0x3C        ; Result high = 0x3C
    ldi r24, 0x00        ; Result low = 0x00

    ; --- Loop de Exponenciação por Quadrado --- 
pow_loop:
    ; Checar se b_int == 0
    mov r16, r26         ; Usar r16 como temp
    or r16, r27          ; Testar se r27:r26 é zero
    breq pow_loop_end    ; Se b_int == 0, fim do loop
    ; Checar se b_int é ímpar (testar bit 0 de r26)
    sbrc r26, 0          ; Pular instrução seguinte se bit 0 de r26 for 0 (par)
    rcall pow_mult_result; Se for ímpar, multiplicar Result por CurrentPower
pow_square_base_prep:
    ; --- Calcular CurrentPower = CurrentPower * CurrentPower --- 
    ; Guardar Result (r25:r24) na pilha antes de usar regs para CP*CP
    push r25
    push r24
    ; CP está em r20:r21
    mov r25, r20         ; Mover CP para entrada A (r25:r24)
    mov r24, r21
    mov r23, r20         ; Mover CP para entrada B (r23:r22)
    mov r22, r21
    call mul_f16         ; r25:r24 = CP * CP
    ; Guardar novo CurrentPower em r20:r21
    mov r20, r25
    mov r21, r24
    ; Restaurar Result da pilha para r25:r24
    pop r24
    pop r25
    ; --- Shift b_int >> 1 --- 
    lsr r26              ; Desloca low byte para direita
    ror r27              ; Rotaciona high byte com carry do lsr
    rjmp pow_loop        ; Volta ao início do loop

; --- Sub-rotina para Result = Result * CurrentPower --- 
; Chamada com rcall, precisa retornar com ret
; Entradas: Result(r25:r24), CP(r20:r21)
; Saida: Novo Result(r25:r24)
; Clobbers: r22, r23, e regs usados por mul_f16
pow_mult_result:
    mov r23, r20
    mov r22, r21
    ; Result (r25:r24) já está na entrada A
    call mul_f16         ; r25:r24 = Result * CP
    ret

pow_loop_end:
    ; O resultado final está em r25:r24
pow_cleanup:
    pop r31
    pop r30
    pop r29
    pop r28
    pop r27
    pop r26
    pop r23
    pop r22
    pop r21
    pop r20
    pop r19
    pop r18
    pop r17
    pop r16
    pop r3
    pop r2
    pop r1
    pop r0
    ret
    
;-----------------------------------------------------
; f16_to_uint16: Converte float16 para uint16_t
; Entrada: r23:r22 (float16)
; Saída:   r27:r26 (uint16_t)
; Modifica: r16, r17, r18, r19
;-----------------------------------------------------
f16_to_uint16:
    mov r18, r23        ; Byte alto de B
    andi r18, 0x7C      ; Isolar bits do expoente
    lsr r18
    lsr r18             ; r18 = Exp (15 a 30)

    ; Extrair mantissa M (10 bits)
    mov r16, r22        ; M7-M0
    mov r17, r23
    andi r17, 0x03      ; M9-M8

    ; Construir mantissa inteira de 11 bits: IntM = (1 << 10) | M
    ori r17, 0x04       ; Adicionar '1' implícito (bit 10 = bit 2 de r17)
    ; Mantissa IntM em r17:r16

    ; Calcular quantidade de shift: shift = E - 10 = (Exp - 15) - 10 = Exp - 25
    mov r19, r18        ; r19 = Exp
    subi r19, 25        ; r19 = shift = E - 10
    ; Se shift >= 0 (E >= 10), shift left. Se shift < 0 (E < 10), shift right.

    cpi r19, 0
    brge f16tu16_lsl    ; Se shift >= 0, pular para left shift

    ; --- Shift Direita (shift < 0, E < 10) ---
f16tu16_rsr:
    neg r19             ; shift_count = -shift = 10 - E
f16tu16_rsr_loop:
    tst r19
    breq f16tu16_done   ; Se contador == 0, terminou
    lsr r17             ; Shift IntM (r17:r16) >> 1
    ror r16
    dec r19
    rjmp f16tu16_rsr_loop

    ; --- Shift Esquerda (shift >= 0, E >= 10) ---
f16tu16_lsl:
f16tu16_lsl_loop:
    tst r19
    breq f16tu16_done   ; Se contador == 0, terminou
    lsl r16             ; Shift IntM (r17:r16) << 1
    rol r17
    dec r19
    rjmp f16tu16_lsl_loop

f16tu16_done:
    ; Resultado uint16 está em r17:r16
    mov r26, r16        ; Mover resultado low byte para r26
    mov r27, r17        ; Mover resultado high byte para r27
    ret                 ; Retorna uint16_t em r27:r26
"""
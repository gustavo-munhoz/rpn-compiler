DIV_INT_F16 = """
;-----------------------------------------------------
; div_int_f16: Divisão inteira de float16
; Entrada A: r25:r24 (float16)
; Entrada B: r23:r22 (float16)
; Saida:     r25:r24 = float16(trunc(A/B))
; Callee-Saved: r18, r20, r21, r26, r27
; Volatile: r16, r17
; Chama: div_f16
;-----------------------------------------------------
div_int_f16:
    push r18
    push r20
    push r21
    push r26
    push r27

    ; 1. Chamar divisão float normal A/B
    call div_f16         ; Resultado R em r25:r24

    ; 2. Salvar sinal do resultado R -> r20
    mov r20, r25
    andi r20, 0x80       ; r20 = Sinal de R

    ; 3. Checar se resultado R é Zero
    mov r16, r24         ; Byte baixo de R
    mov r17, r25
    andi r17, 0x7F       ; Byte alto de R sem sinal
    or r16, r17          ; r16 == 0 se R for +/- 0.0
    brne check_inf_nan   ; Pular se R não for zero
    mov r25, r20         ; Restaurar sinal em r25
    ldi r24, 0x00        ; Garantir r24 zero
    rjmp div_int_cleanup ; Resultado é +/- 0.0, fim.

check_inf_nan:
    ; 4. Checar Inf/NaN (Expoente == 31) -> r26
    mov r26, r25         ; Pegar byte alto de R
    andi r26, 0x7C       ; Isolar bits do expoente (posições 6-2)
    cpi r26, 0x7C        ; Comparar com padrão Inf/NaN (11111 << 2)
    breq div_int_cleanup ; Se Inf/NaN, retornar R como está. Fim.

    ; 5. Extrair expoente com bias -> r26 (já isolado, só shiftar)
    lsr r26
    lsr r26              ; r26 = Expoente com bias (0-30)

    ; 6. Calcular E = Exp - Bias -> r18
    mov r18, r26
    subi r18, 15         ; r18 = E = Exp - 15. Flags N,Z,C,V,S atualizados.

    ; 7. Se E < 0 (Exp < 15), |R| < 1.0. Resultado truncado é +/- Zero
    brge E_ge_zero       ; Pular se E >= 0 (com sinal)
    ; E < 0 (|R| < 1.0)
    mov r25, r20         ; Resultado = +/- Zero
    ldi r24, 0x00
    rjmp div_int_cleanup ; Fim.

E_ge_zero:
    ; E é >= 0 aqui.
    ; 8. Se E >= 10 (Exp >= 25), R já é inteiro. Retornar R.
    cpi r18, 10
    brlt E_lt_10         ; Pular se E < 10 (com sinal)
    ; E >= 10. R já é inteiro.
    rjmp div_int_cleanup ; Fim.

E_lt_10:
    ; --- Truncar Parte Fracionária (E está entre 0 e 9) --- 
    ; 9. Calcular k = 10 - E -> r27
    ldi r27, 10
    sub r27, r18         ; r27 = k = 10 - E (k estará entre 1 e 10)

    ; 10. Mascarar r24 (M7-M0) - Zerar os k bits inferiores
    ldi r16, 0xFF        ; Máscara inicial
    mov r17, r27         ; Contador k
mask_r24_loop:
    tst r17              ; Contador k == 0?
    breq mask_r24_done   ; Sim, loop terminou.
    lsl r16              ; Deslocar máscara para esquerda
    dec r17              ; Decrementar contador k
    rjmp mask_r24_loop   ; Repetir o loop
mask_r24_done:
    and r24, r16         ; Aplicar máscara em r24

    ; 11. Mascarar r25 (M9, M8 - bits 1,0)
    cpi r27, 9           ; Comparar k com 9
    brlo mask_r25_done   ; Se k < 9 (E >= 2), M9 e M8 são mantidos.
    ldi r17, 0x02        ; Máscara para MANTER M9 (bit 1) - default para k=9
    cpi r27, 10          ; Comparar k com 10
    brne apply_mask_r25_final ; Pular se k=9
    ; k = 10 (E=0), zerar M9 e M8
    ldi r17, 0x00        ; Máscara para MANTER NADA (M9=0, M8=0)
apply_mask_r25_final:
    mov r16, r25         ; Copiar r25 original para r16 (Volatile)
    andi r16, 0x03       ; Isolar M9, M8 originais em r16
    and r16, r17         ; Aplicar máscara de MANTER -> r16 = M9', M8'
    andi r25, 0xFC       ; Zerar M9, M8 em r25 original (preserva S|Exp)
    or r25, r16          ; Combinar S|Exp com M9', M8' corretos
mask_r25_done:
    ; O resultado truncado está em r25:r24
div_int_cleanup:
    pop r27
    pop r26
    pop r21
    pop r20
    pop r18
    ret
"""
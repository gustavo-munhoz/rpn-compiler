DIV_F16 = """
;-----------------------------------------------------
; div_f16: Divisão em ponto flutuante IEEE 754 de 16 bits
; Entrada:
;   r25:r24 = dividendo
;   r23:r22 = divisor
; Saída:
;   r25:r24 = resultado
; Registradores usados: r0, r1, r2, r3, r16-r21
;-----------------------------------------------------
div_f16:
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
    ; Verificar se divisor é zero
    mov  r16, r22
    or   r16, r23
    brne divisor_not_zero
    ; Divisão por zero - retornar infinito com sinal apropriado
    mov  r16, r25
    andi r16, 0x80
    ori  r16, 0x7C
    mov  r25, r16
    ldi  r24, 0x00
    rjmp div_f16_end
divisor_not_zero:
    ; Extrair sinais
    mov  r16, r25
    andi r16, 0x80
    mov  r17, r23
    andi r17, 0x80
    mov  r18, r16
    eor  r18, r17
    mov  r20, r18
    ; Extrair magnitude (remover bit de sinal)
    mov  r16, r25
    andi r16, 0x7F
    mov  r17, r23
    andi r17, 0x7F
    ; Verificar se dividendo é zero (após remover sinal)
    mov  r18, r16
    or   r18, r24
    brne dividend_not_zero
    ; Dividendo é zero - retornar zero com sinal apropriado
    mov  r25, r20
    ldi  r24, 0x00
    rjmp div_f16_end
dividend_not_zero:
    ; Extrair expoentes
    mov  r18, r16
    andi r18, 0x7C
    lsr  r18
    lsr  r18
    mov  r19, r17
    andi r19, 0x7C
    lsr  r19
    lsr  r19
    ; Calcular expoente do resultado: exp_res = exp_divd - exp_divs + 15
    sub  r18, r19
    subi r18, -15
    ; Extrair mantissas (11 bits com implícito)
    ; Dividendo -> r1:r0
    mov  r19, r16
    andi r19, 0x03
    ori  r19, 0x04
    mov  r1, r19
    mov  r0, r24
    ; Divisor -> r3:r2
    mov  r19, r17
    andi r19, 0x03
    ori  r19, 0x04
    mov  r3, r19
    mov  r2, r22
    clr  r16            ; Limpar registrador baixo do quociente
    clr  r17            ; Limpar registrador alto do quociente
    ldi  r19, 16        ; Contador de iterações (16 para quociente de 16 bits)
division_loop_new:
    ; Comparar Resto (r1:r0) com Divisor (r3:r2)
    cp   r0, r2
    cpc  r1, r3
    brcc sub_ok_new     ; Pular se R >= D (Carry Limpo)
    ; R < D : Bit do quociente é 0
    clc                 ; Garantir Carry = 0 para shift no quociente
    rjmp shift_q_new    ; Pular subtração
sub_ok_new:
    ; R >= D : Bit do quociente é 1
    sub  r0, r2         ; R = R - D
    sbc  r1, r3
    sec                 ; Setar Carry = 1 para shift no quociente
shift_q_new:
    ; Deslocar Quociente (r17:r16) à esquerda e inserir bit (Carry)
    rol  r16
    rol  r17
shift_r_new:
    lsl  r0
    rol  r1
    ; Decrementar contador e loop
    dec  r19
    brne division_loop_new
    ; Normalizar o quociente (r17:r16) e ajustar o expoente (r18)
    mov r19, r16
    or r19, r17
    breq result_is_zero
div_normalize_loop:
    tst r17
    brne msb_in_r17
    mov r17, r16
    clr r16
    subi r18, 8
    tst r17
    breq result_is_zero
    rjmp div_normalize_loop
msb_in_r17:
    mov r19, r17
check_msb_pos:
    sbrc r19, 7        ; Bit 7 de r17 é a posição do bit implícito (1.xxxx)
    rjmp msb_normalized
    tst r19
    breq msb_normalized ; Parar se ficou zero
    lsl  r16
    rol  r17
    lsl  r19
    dec  r18           ; Ajustar (diminuir) expoente para cada LSL
    rjmp check_msb_pos
msb_normalized:
    ; Verificar limites do expoente (Overflow / Underflow)
check_exponent:
    cpi  r18, 31
    brsh exponent_overflow
    cpi  r18, 1
    brlo exponent_underflow
    ; Expoente válido (1 a 30)
    rjmp construct_result
exponent_overflow:
    mov  r25, r20
    ori  r25, 0x7C
    ldi  r24, 0x00
    rjmp div_f16_end
result_is_zero:
exponent_underflow:
    mov  r25, r20
    ldi  r24, 0x00
    rjmp div_f16_end
construct_result:
    ; Construir número normalizado
    ; Expoente ajustado em r18, mantissa normalizada em r17:r16, sinal em r20.
    ; r17 = 1 M9 M8 M7 M6 M5 M4 M3
    ; r16 = M2 M1 M0 X X X X X
    ; Preparar byte alto (r25): Sinal | Expoente | M9 M8
    mov  r25, r18       ; Expoente (1-30)
    lsl  r25
    lsl  r25            ; Posicionar em bits 6-2
    andi r25, 0x7C      ; Isolar bits do expoente
    mov  r19, r17       ; r17 = 1 M9 M8 ...
    andi r19, 0x60      ; Isolar M9 M8 em posições 6,5
    lsr  r19
    lsr  r19
    lsr  r19
    lsr  r19
    lsr  r19            ; Mover M9 M8 para posições 1,0
    or   r25, r19       ; Combinar expoente e M9 M8
    or   r25, r20       ; Adicionar bit de sinal
    ; Preparar byte baixo (r24): M7 M6 M5 M4 M3 M2 M1 M0
    mov  r19, r17       ; r17 = 1 M9 M8 M7 M6 M5 M4 M3
    andi r19, 0x1F     ; Isolar M7..M3
    lsl  r19
    lsl  r19
    lsl  r19           ; r19 = M7M6M5M4M3000
    mov  r24, r19       ; Mover para resultado parcial
    mov  r19, r16       ; r16 = M2 M1 M0 X ...
    andi r19, 0xE0     ; Isolar M2 M1 M0
    lsr  r19
    lsr  r19
    lsr  r19           ; r19 = 000M2M1M000
    or   r24, r19       ; Combinar -> r24 = M7M6M5M4M3M2M1M0
div_f16_end:
    ; Restaurar registradores
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
"""
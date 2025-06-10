MOD_F16 = """
;-----------------------------------------------------
; mod_f16: Resto da divisão de float16
; Entrada A: r25:r24
; Entrada B: r23:r22
; Saida:     r25:r24 = A % B = A - trunc(A/B) * B
; Usa:       Registradores conforme funções chamadas.
; Chama:     div_int_f16, mul_f16, sub_f16
;-----------------------------------------------------
mod_f16:
    ; --- Salvar Registradores ---
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
    push r26
    push r27
    push r28
    push r29
    push r30
    push r31
    ; --- Checar Divisor B Zero --- 
    mov r16, r22         ; B low
    mov r17, r23         ; B high
    andi r17, 0x7F       ; Limpar bit de sinal de B high
    or r16, r17          ; Checar se magnitude é zero
    brne mod_b_not_zero  ; Pular se B != 0
    ldi r25, 0x7E
    ldi r24, 0x00
    rjmp mod_cleanup     ; Pular para restauração e ret
mod_b_not_zero:

    ; Guardar A e B originais na pilha
    push r25 ; Salvar A high
    push r24 ; Salvar A low
    push r23 ; Salvar B high
    push r22 ; Salvar B low
    ; --- Passo 1: Calcular i = trunc(A / B) --- 
    call div_int_f16

    ; Guardar 'i' na pilha
    push r25
    push r24
    ; --- Passo 2: Calcular P = i * B --- 
    pop r22              ; Pop B low original para r22
    pop r23              ; Pop B high original para r23
    pop r24              ; Pop i low para r24
    pop r25              ; Pop i high para r25
    call mul_f16         ; P = i * B fica em r25:r24

    ; Guardar P na pilha
    push r25
    push r24
    ; --- Passo 3: Calcular R = A - P --- 
    pop r24              ; Pop A low original para r24
    pop r25              ; Pop A high original para r25
    pop r22              ; Pop P low para r22
    pop r23              ; Pop P high para r23
    call sub_f16

    ; Checar se R' (r25:r24) tem magnitude zero
    mov r16, r24         ; R' low
    mov r17, r25         ; R' high
    andi r17, 0x7F       ; Ignorar sinal de R'
    or r16, r17          ; r16 == 0 se magnitude zero
    brne mod_flip_sign   ; Pular para inverter se não for zero
    ; Magnitude é zero, não fazer nada
    rjmp mod_sign_done
mod_flip_sign:
    ; Resultado R' não é zero, inverter seu bit de sinal
    ldi r16, 0x80
    eor r25, r16         ; Inverte bit 7 de r25
mod_sign_done:
    ; O resultado final R (com sinal correto) está em r25:r24
mod_cleanup:
    pop r31
    pop r30
    pop r29
    pop r28
    pop r27
    pop r26
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

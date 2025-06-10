RES_OP = """
;-----------------------------------------------------
; res_op: Recupera o resultado da linha N anterior.
; Entrada:
;   r24 = índice N (número de linhas anteriores)
; Saída:
;   r24:r25 = resultado armazenado em 'results' na posição (N*2)
;-----------------------------------------------------

res_op:
    lsl   r24         ; Multiplica N por 2 (offset em bytes)
    ldi   r30, lo8_results
    ldi   r31, hi8_results
    add   r30, r24    ; Adiciona o offset ao endereço base
    ld    r24, Z+     ; Carrega o byte baixo do resultado
    ld    r25, Z      ; Carrega o byte alto do resultado
    ret
"""
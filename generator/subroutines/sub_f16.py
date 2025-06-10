SUB_F16 = """
;-----------------------------------------------------
; sub_f16: Subtração de dois half-precision IEEE-754
; Entradas: Operando A em R25:R24, Operando B em R23:R22
; Saída: Resultado em R25:R24
;-----------------------------------------------------

sub_f16:
    ldi R16, 0x80
    eor R23, R16
    
    rcall add_f16
    ret
"""
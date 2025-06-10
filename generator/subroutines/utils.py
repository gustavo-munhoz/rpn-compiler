USART_CONFIG = """
; Configuração da USART
    store   UBRR0H, 0x01
    store   UBRR0L, 0xA0
    store   UCSR0A, 0b00100000
    store   UCSR0C, 0x06
    store   UCSR0B, 0x18
"""

SERIAL_COMM = """
; Rotina para transmitir um caractere via Serial.
tx_R16:
    push    R16
tx_R16_aguarda:
    lds     R16, UCSR0A
    sbrs    R16, 5
    rjmp    tx_R16_aguarda
    pop     R16
    sts     UDR0, R16
    ret
"""

PRINT_F16 = """
; ---------------------------------------------------------------
; Rotina para imprimir o valor em R25:R24 como HEX (f16 IEEE 754)
; ---------------------------------------------------------------

print_f16:
 push R16
 push R17
 push R18
 push R19
 push R24
 push R25

 ldi R16, '0'
 rcall tx_R16
 ldi R16, 'x'
 rcall tx_R16

 mov R16, R25
 rcall print_hex8

 mov R16, R24
 rcall print_hex8

 ldi R16, 0x0D ; CR
 rcall tx_R16
 ldi R16, 0x0A ; LF
 rcall tx_R16

 pop R25
 pop R24
 pop R19
 pop R18
 pop R17
 pop R16
 ret

print_hex8:
 push R17

 mov R17, R16

 swap R16
 andi R16, 0x0F
 rcall nibble2hex

 mov R16, R17
 andi R16, 0x0F
 rcall nibble2hex

 pop R17
 ret

nibble2hex:
 cpi R16, 10
 brlt nibble_is_dec
 subi R16, 10
 subi R16, -'A'
 rjmp nibble_print

nibble_is_dec:
 subi R16, -'0'
nibble_print:
 rcall tx_R16
 ret
"""

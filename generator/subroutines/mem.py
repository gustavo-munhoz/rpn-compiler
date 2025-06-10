SET_MEM = """
;-----------------------------------------------------
; set_mem: Armazena o valor de r24:r25 em storeVal
;-----------------------------------------------------
set_mem:
    STS storeVal, r24
    STS storeVal+1, r25
    ret
"""

GET_MEM = """
;-----------------------------------------------------
; get_mem: Carrega o valor de storeVal em r24:r25
;-----------------------------------------------------
get_mem:
    LDS r24, storeVal
    LDS r25, storeVal+1
    ret
"""
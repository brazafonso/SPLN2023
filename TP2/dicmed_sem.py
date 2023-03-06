import ply.yacc as yacc
from dicmed_lex import tokens

def p_1(p):
    r'dic : Es'
    print(p[0])

def p_2(p):
    r'Es : E LB Es'

def p_3(p):
    r'Es : E'

def p_4(p):
    r'E : ITENS'

def p_5(p):
    r'E : '

def p_6(p):
    r'ITENS : ITEM "\n" ITENS'

def p_7(p):
    r'ITENS : ITEM'

def p_8(p):
    r'ITEM : AT_CONC'

def p_9(p):
    r'ITEM : LING'

def p_10(p):
    r'AT_CONC : ID ":" VAL'

def p_11(p):
    r'LING : ID_LING ":" "\n" Ts'

def p_12(p):
    r'Ts : T "\n" Ts'

def p_13(p):
    r'Ts : T'

def p_14(p):
    r'T : "-" VAL AT_Ts'

def p_15(p):
    r'AT_Ts : AT_Ts AT_T'

def p_16(p):
    r'AT_Ts : '

def p_17(p):
    r'AT_T : "\n" "+" ID ":" VAL'

def p_error(p):
    print('Syntax error: ', p)
    parser.success = False

parser = yacc.yacc()

parser.parse('''Area: Anatomía
Pt:
-ACA (sg)
En:
-ACA (sg)
Es:
-ACA (sg)
La:
-arteria cerebri anterior
Ga:
-arteria cerebral anterior     
- ACA (sg)
'''
)




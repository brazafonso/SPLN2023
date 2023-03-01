import ply.yacc as yacc
from dicmed_lex import tokens

def p_1(p):
    'dic : Es'

def p_2(p):
    'Es : E LB Es'

def p_3(p):
    'Es : E'

def p_4(p):
    'E : ITENS'

def p_5(p):
    'ITENS : ITEM "\n" ITENS'

def p_6(p):
    'ITENS : ITEM'

def p_7(p):
    'ITEM : AT_CONC'

def p_8(p):
    'ITEM : LING'

def p_9(p):
    'AT_CONC : ID ":" VAL'

def p_10(p):
    'LING : ID_LING ":" "\n" Ts'

def p_11(p):
    'Ts : T "\n" Ts'

def p_12(p):
    'Ts : T'

def p_13(p):
    'T : "-" VAL AT_Ts'

def p_14(p):
    'AT_Ts : AT_Ts AT_T'

def p_15(p):
    'AT_Ts : '

def p_16(p):
    'AT_T : "\n" "+" ID ":" VAL'

def p_error(p):
    print('Syntax error: ', p)
    parser.success = False

parser = yacc.yacc()

parser.parse('''
    Area: ... delim ...
    Ga: ...
    ...
    +var: ...
    En: ...
    ...
    Pt: ...
    +var: ...
    ...
    +var: ...
''')




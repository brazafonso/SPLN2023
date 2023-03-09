import ply.lex as lex


tokens = ('ID','VAL','ID_LING','LB')

literals = [':','-','+','\n']

t_ANY_ignore =" "

def t_ID_LING(t):
    r'(En|Pt|La|Ga|Es)(?=\s*:)'
    return t

def t_ID(t):
    r'\w+(?=\s*:)'
    return t

def t_LB(t):
    r'(?<=\n)\n'
    return t

def t_VAL(t):
    r'[^\+\-\:\n ]+[^\:\n]*'
    return t

def t_error(t):
    print('Ilegal character "%s"' % t.value[0])
    t.lexer.skip(1)


lexer = lex.lex()
# file = open('dicionario_global_medicina.txt','r', encoding='utf-8')
# txt = file.read()
# file.close()
# file = open('lexer_out.txt','w')

# lexer.input(txt)
# while True:
#     tok = lexer.token()
#     if not tok: 
#         break      # No more input
#     file.write(f'{tok}\n')
# file.close()

# lexer.input('''Area: Fisioloxía
# Pt:
# -factores ABO [Pt.]
# En:
# -ABO blood-group system
# Es:
# -factores ABO
# Ga:
# -sistema ABO     
# - sistema do grupo sanguíneo ABO

# Area: Anatomía
# Pt:
# -ACA (sg)
# En:
# -ACA (sg)
# Es:
# -ACA (sg)
# La:
# -arteria cerebri anterior
# Ga:
# -arteria cerebral anterior     
# - ACA (sg)
# '''
# )

# Tokenize
# while True:
#     tok = lexer.token()
#     if not tok: 
#         break      # No more input
#     print(tok)
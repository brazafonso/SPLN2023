import ply.lex as lex


tokens = ('ID','VAL','ID_LING','LB')

literals = [':','-','+','\n']


def t_ID_LING(t):
    r'(En|Pt|La|Ga)(?=\s*:)'
    return t

def t_ID(t):
    r'\w+(?=\s*:)'
    return t

def t_LB(t):
    r'\n\n'
    return t

def t_VAL(t):
    r'[^\+\-\:\n]+'
    return t



def t_error(t):
    print('Ilegal character "%s"' % t.value[0])
    t.lexer.skip(1)


lexer = lex.lex()

lexer.input(
'''
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
'''

)

# Tokenize
while True:
    tok = lexer.token()
    if not tok: 
        break      # No more input
    print(tok)
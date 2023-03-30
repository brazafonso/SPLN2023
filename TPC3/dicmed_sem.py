import ply.yacc as yacc
from dicmed_lex import tokens
import pickle



def create_item_dict(item:tuple):
    """Create a dictionary from an item tuple"""
    result = {}
    if item[0] == 'atributes':
        result['atributes'] = {}
        result['atributes'][item[1]] = {}
        values = item[2].split(';')
        for value in values:
            result['atributes'][item[1]][value] = []
    elif item[0] == 'languages':
        result['languages'] = {}
        result['languages'][item[1]] = {}
        for termo in item[2]:
            result['languages'][item[1]] = {termo[0] : termo[1]}
    return result

def unite_item_dict(item1,item2):
    """Unites a item dictionary (item 1) with the result items dictionary (item2)"""
    result = item2
    for key,value in item1.items():
        if key in result:
            for key2,value2 in item1[key].items():
                if key2 in result[key]:
                    for key3,value3 in value2.items():
                        result[key][key2][key3] = value3
                else:
                    result[key][key2] = value2
        else:
            result[key] = value
    return result

def p_1(p):
    r'dic : Es'
    p[0] = p[1]

def p_2(p):
    r'Es : Es LB E '
    p[0] = p[1] +[p[3]]

def p_3(p):
    r'Es : E'
    p[0] = [p[1]]

def p_4(p):
    r'E : ITENS'
    p[0] = p[1]

def p_5(p):
    r'E : '
    p[0] = []

def p_6(p):
    r'ITENS : ITEM ITENS'
    p[0] = unite_item_dict(create_item_dict(p[1]),p[2])

def p_7(p):
    r'ITENS : ITEM'
    p[0] = create_item_dict(p[1])

def p_8(p):
    r'ITEM : AT_CONC'
    p[0] = p[1]

def p_9(p):
    r'ITEM : LING'
    p[0] = p[1]

def p_10(p):
    r'AT_CONC : ID ":" VAL "\n"'
    p[0] = ('atributes',p[1] , p[3])

def p_11(p):
    r'LING : ID_LING ":" "\n" Ts'
    p[0] = ('languages',p[1],p[4])

def p_12(p):
    r'Ts : T Ts'
    p[0] = [p[1]] + p[2]

def p_13(p):
    r'Ts : T'
    p[0] = [p[1]]

def p_14(p):
    r'T : "-" VAL AT_Ts'
    p[0] = ( p[2] , p[3])

def p_15(p):
    r'AT_Ts : "\n" AT_T AT_Ts'
    p[0] = [p[2]] + p[3]

def p_16(p):
    r'AT_Ts : "\n"'
    p[0] = []

def p_17(p):
    r'AT_T : "+" ID ":" VAL'
    p[0] = [(p[2], p[4])]

def p_error(p):
    print('Syntax error: ', p)
    parser.error += 1

parser = yacc.yacc()




file = open('dicionario_global_medicina.txt','r', encoding='utf-8')
txt = file.read()

# parser.parse('''Area: Fisioloxía
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
# ''')

parser.dic = []
parser.entry = {}
parser.error = 0
result = parser.parse(txt)
if parser.error == 0:
    print('Concluido parse sem erros')
    print(f'Numero de entradas : {len(result)}')
    for i,entrada in enumerate(result):
        if entrada == []:
            result.pop(i)

    print(result[0])
    file = open('entries_dic','wb')
    pickle.dump(result,file)
    file.close()

else:
    print(f'Encontrados {parser.error} erros no ficheiro')


"""
Vocabulário de Medicina


Tipos de entradas:

* Entradas completas
  ** numeros
  ** area tematica == taboa de materias
  ** Galego
    *** areas tematicas
    *** SIN
    *** Var
    *** es
    *** en
    *** pt
    *** la
    *** Nota

* Entradas remisivas (variantes de uma entrada completa)
  



TPC:
criar git e colocar na folha
marcar os elementos de segunda ordem (***)
tirar o xml a mais do resultado
colocar numa estrutura de dados o resultado(por exemplo com split)

"""


import re

def remove_header_footer(texto):
    texto = re.sub(r'<text.* font="1">ocabulario.*</text>', r'###', texto)
    texto = re.sub(r'.*\n###\n.*\n', r'___', texto)
    texto = re.sub(r'<page.*\n|</page>\n', r'', texto)
    return texto


def marcaE(texto):
    """Marca entradas de vocabulario"""
    texto = re.sub(r'<text.* font="3"><b>\s*(\d+.*)</b></text>', r'###C \1', texto)
    texto = re.sub(r'<text.* font="3"><b>\s*(\S.*)</b></text>', r'###R \1', texto)
    return texto



texto = open('medicina.xml', 'r+', encoding="utf8")

    

texto = remove_header_footer(texto)


texto = marcaE(texto)

def marcaLinguas(texto):
    # @
    pass

# dicionario

def marcaEC(texto):
    pass

def marcaER(texto):
    pass


file = open('medicina2.xml', 'w')

file.write(texto)


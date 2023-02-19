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
import json



def remove_header_footer(texto):
    texto = re.sub(r'<text.* font="1">ocabulario.*</text>', r'###', texto)
    texto = re.sub(r'.*\n###\n.*\n', r'___', texto)
    texto = re.sub(r'<page.*\n|</page>\n', r'', texto)
    return texto


def marcaE(texto):
    """Marca entradas de vocabulario"""
    texto = re.sub(r'<text.* font="3"><b>\s*(\d+.*)</b></text>', r'###C\1', texto)
    texto = re.sub(r'<text.* font="3"><b>\s*(\S.*)</b></text>', r'###R\1', texto)
    return texto

def marcaLinguas(texto):
    texto = re.sub(r'<text.* font="0">\s*(\w\w)\s*</text>', r'@\1', texto)
    return texto

def marcaTraducoes(texto):
    texto = re.sub(r'<text.*font="7">\s*<i>\s*(.*)</i>\.*</text>', r'@T\1', texto)
    texto = re.sub(r'\n@T\s*\n(@T)?', r' ', texto)
    return texto

def marcaAreas(texto):
    texto = re.sub(r'<text.*font="5">\s*</text>\n', r'', texto)
    texto = re.sub(r'(###[CR].*\n)<text.*font="6">\s*<i>\s*(.*)</i>\.*</text>', r'\1!\2', texto)
    return texto

def marcaSinVar(texto):
    #limpar fonte 0 5 vazios
    texto = re.sub(r'<text.*font="[05]">\s*</text>', r'', texto)
    #apanhar todos os sinonimos ou variacoes
    texto = re.sub(r'<text.*font="[05]">\s*(SIN\.-(.*?))?(VAR\.-(.*))?</text>', r'$S\2\n$V\4', texto)
    return texto

def marcaVid(texto):
    texto = re.sub(r'<text.*font="[05]">\s*Vid\.-(.*)</text>', r'$I\1', texto)
    #juntar alguns irregulares
    texto = re.sub(r'\$I(.*)\n<text.*font="5">(.*)</text>',r'\1\2',texto)
    return texto

def marcaNota(texto):
    texto = re.sub(r'<text.*font="9">(.*)</text>', r'#N\1', texto)
    texto = re.sub(r'#N\s*Nota\.-', r'#N', texto)
    # texto = re.sub(r'#N\s*\n',r'',texto)
    # texto = re.sub(r'\n#N\s*(?!Nota\.-)(.*)\n',r'\1',texto)
    # texto = re.sub(r'(#N[^<]*)',r'\1\n',texto)
    return texto

def limpaXML(texto):
    texto = re.sub(r'<.*>\n?', r'', texto)
    texto = re.sub(r'\n\s*\n', r'\n', texto)
    return texto

texto = open('medicina.xml', 'r+', encoding="utf8").read()

texto = remove_header_footer(texto)

texto = marcaE(texto)

texto = marcaLinguas(texto)

texto = marcaTraducoes(texto)

texto = marcaAreas(texto)

texto = marcaSinVar(texto)

texto = marcaVid(texto)

texto = marcaNota(texto)

texto = limpaXML(texto)

# dicionario

entradas = texto.split('###')

completas = {}
remissivas = {}
erros = 0
for entrada in entradas:
    try:
        if entrada[0] == 'C':
            linhas = entrada.split('\n')
            assinatura = linhas[0]
            assinatura = re.match(r'C(\d+)\s+(\w*\s*)+\s+(\w)',assinatura)
            if assinatura.groups:
                numero = int(assinatura.group(1))
                nome = assinatura.group(2)
                genero = assinatura.group(3)
                areas = []
                sinonimos = []
                variacoes = []
                traducoes = {
                    'pt' : [],
                    'en' : [],
                    'es' : [],
                    'la' : [],
                }
                nota = ''
                flag = ''
                for linha in linhas:
                    if len(linha) > 0:
                        if linha[0] == '!':
                            areas = linha[1:]
                            areas = re.sub(r'\s\s+',' ',areas)
                            areas = areas.split(' ')
                        elif '$S' in linha:
                            sinonimos = linha[2:]
                            sinonimos = sinonimos.split(';')
                        elif '$V' in linha:
                            variacoes = linha[2:]
                            variacoes = variacoes.split(';')
                        elif linha[0] == '@':
                            if '@es' in linha:
                                flag = 'es'
                            elif '@en' in linha:
                                flag = 'en'
                            elif '@pt' in linha:
                                flag = 'pt'
                            elif '@la' in linha:
                                flag = 'la'
                            else:
                                traducoes[flag].append(linha[2:])
                        elif '#N' in linha:
                            nota += linha[2:]
                completas[numero] = {
                    'numero' : numero,
                    'nome' : nome,
                    'genero' : genero,
                    'areas' : areas,
                    'sinonimos' : sinonimos,
                    'variacoes' : variacoes,
                    'traducoes' : traducoes,
                    'nota' : nota,

                }

        elif entrada[0] == 'R':
            linhas = entrada.split('\n')
            assinatura = linhas[0]
            nome = assinatura[1:]
            vids = []
            for linha in linhas:
                if '$I' in linha:
                    vids.append(linha[2:])
            remissivas[nome] = {
                'nome' : nome,
                'vids' : vids,
            }


    except Exception as e:
        print(e)
        entry = entrada.split('\n')[0]
        print(f"Error on entry : {entry}")
        erros+=1


file = open('medicina_processado.xml', 'w')
file.write(texto)

dados = {
    'completas' : completas,
    'remissivas' : remissivas,
}

json_dump = json.dumps(dados,indent=4)
file = open('medicina_resultado.json','w',encoding='utf-8')
file.write(json_dump)


print(f'Resultados:\n Entradas completas = {len(dados["completas"])}\n Entradas remissivas = {len(dados["remissivas"])}\n Entradas com erros = {erros}')


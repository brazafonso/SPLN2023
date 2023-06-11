'''Ficheiro com parser do ficheiro de configuracao do servidor'''

from lark.visitors import Interpreter
from lark import Lark

import re


grammar = '''
start : servidor
servidor : "*" "Servidor" opcoes_servidor ferramentas visuais?
opcoes_servidor : nome_servidor diretoria_servidor porta_servidor trabalhadores_servidor?
nome_servidor : "-" "Nome" ":" NOME
diretoria_servidor : "-" "Diretoria" ":" TEXTO
porta_servidor : "-" "Porta" ":" PORTA
trabalhadores_servidor : "-" "Trabalhadores" ":" INT

ferramentas : "*" "Ferramentas" ("--" ferramenta)+
ferramenta : familia titulo descricao comando inputs?
familia : "-" "Família" ":" NOME
titulo  : "-" "Título" ":" TEXTO
descricao : "-" "Descrição" ":" TEXTO
comando : "-" "Comando" ":" comando_formato
comando_formato : (NOME (opcoes | arg)*) (comando_operador comando_formato)*
opcoes : INPUT
        | FLAG
comando_operador : PIPE
                | REDIRECIONAMENTO
                | AND
arg : TEXTO
    | PALAVRA

visuais : "*" "Visuais" favicon? colors?
favicon : "-" "Favicon" ":" TEXTO
colors : color+
color : "-" COLOR ":" HEXCODE


inputs : "-" "Inputs" ":" input+
input : "-" INPUT ":" opcoes_input
opcoes_input : input_nome? input_descricao? input_tipo
input_nome : "-" "Nome" ":" NOME 
input_descricao : "-" "Descrição" ":" TEXTO 
input_tipo : "-" "Tipo" ":" TYPE 

IP: /(\d{1,4}\.){3}\d{1,4}/
PORTA: /\d+/
STR: /"[^"]"/
TEXTO: /"[^"]*"/
NOME: /[\w\-]+/
PALAVRA: /[\w\.\-_]+/
INPUT: /INPUT\d+/
FLAG: /-{1,2}\w+/
TYPE: /(STR)|(NUM)|(FILE)/
PIPE: /\|/
REDIRECIONAMENTO: /<|>/
AND: /&/
COLOR: /(PrimaryBgColor)|(SecondaryBgColor)|(PrimaryTextColor)|(SecondaryTextColor)|(LabelColor)|(BorderColor)/
HEXCODE: /#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})/

%import common.WS
%import common.WORD
%import common.NEWLINE
%import common.INT
%ignore WS
'''

class Interpreter(Interpreter):
    '''Interpreter para atravessar ficheiro de configuracao'''

    def __set_server_name(self,nome):
        '''Modifica o nome do servidor'''
        self.server_config['nome'] = nome

    def __set_server_directory(self,diretoria):
        '''Modifica a diretoria do servidor'''
        self.server_config['diretoria'] = diretoria

    def __set_server_ip(self,ip):
        '''Modifica o ip do servidor'''
        self.server_config['ip'] = ip

    def __set_server_port(self,porta):
        '''Modifica a porta do servidor'''
        self.server_config['porta'] = porta

    def __set_server_route(self,rota):
        '''Modifica a rota do servidor'''
        self.server_config['rota'] = rota

    def __set_server_workers(self,trabalhadores):
        '''Modifica o numero de trabalhadores do servidor'''
        self.server_config['workers'] = trabalhadores

    def __set_color(self,tag,color):
        tag = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', tag)
        tag = re.sub('([a-z0-9])([A-Z])', r'\1_\2', tag).lower()
        self.server_config['visuais']['colors'][tag] = color

    def __set_favicon(self,favicon):
        self.server_config['visuais']['favicon'] = favicon

    def __add_tool(self,familia,titulo_ferramenta):
        '''Adiciona uma nova ferramenta no dicionario de ferramentas'''
        self.server_config['ferramentas'][familia][titulo_ferramenta] = {
            'descricao' : '',
            'comando' : '',
            'inputs' : [],
            'n_files' : 0
        }

    def __add_tool_family(self,familia):
        '''Adiciona uma familia de ferramentas'''
        if familia not in self.server_config['ferramentas']:
            self.server_config['ferramentas'][familia] = {}

    def __set_tool_description(self,familia,tool,descricao):
        '''Modifica a descricao de uma ferramenta'''
        self.server_config['ferramentas'][familia][tool]['descricao'] = descricao

    def __set_tool_command(self,familia,tool,comando):
        '''Modifica o comando de uma ferramenta'''
        self.server_config['ferramentas'][familia][tool]['comando'] = comando

    def __add_tool_input(self,familia,tool,input_id, input_opcoes):
        '''Adiciona um input a uma ferramenta'''
        self.server_config['ferramentas'][familia][tool]['inputs'].append({'id':input_id, 'opcoes':dict(input_opcoes)})

    def __add_tool_nfiles(self,familia,tool):
        '''Incrementa o numero de ficheiros que a tool aceita'''
        self.server_config['ferramentas'][familia][tool]['n_files'] += 1


    
    def __init__(self):
        self.server_config = {
            'nome' : '',
            'diretoria' : '',
            'ip' : '127.0.0.1',
            'porta' : '',
            'rota' : '/',
            'workers' : 1,
            'ferramentas' : {},
            'visuais' : {
                'favicon' : '',
                'colors' : {
                    'primary_text_color' : '#000',
                    'secondary_text_color' : '#fff',
                    'primary_bg_color' : '#fff',
                    'secondary_bg_color' : '#3f51b5',
                    'label_color' : '#3f51b5',
                    'border_color' : '#9e9e9e',
                    }
            }
        }
        self.curTool = None
        self.curFamily = None

    def start(self,start):
        '''start : servidor'''
        elems = start.children
        # visitar servidor
        self.visit(elems[0])
        return self.server_config
    
    def servidor(self,servidor):
        '''servidor : "*" "Servidor" opcoes_servidor ferramentas visuais?'''
        elems = servidor.children
        # visitar opcoes_servidor
        self.visit(elems[0])
        # visitar ferramentas
        self.visit(elems[1])
        # visitar visuais?
        if (len(elems) == 3):
            self.visit(elems[2])

    def opcoes_servidor(self,opcoes_servidor):
        '''opcoes_servidor : nome_servidor diretoria_servidor porta_servidor  rota_servidor? trabalhadores_servidor?'''
        elems = opcoes_servidor.children
        # visitar todas as opcoes
        for elem in elems:
            self.visit(elem)

    def nome_servidor(self,nome_servidor):
        '''nome_servidor : "-" "Nome" ":" NOME'''
        elems = nome_servidor.children
        nome = elems[0].value
        self.__set_server_name(nome)

    def diretoria_servidor(self,diretoria_servidor):
        '''diretoria_servidor : "-" "Diretoria" ":" TEXTO'''
        elems = diretoria_servidor.children
        diretoria = elems[0].value[1:-1]
        self.__set_server_directory(diretoria)

    def porta_servidor(self,porta_servidor):
        '''porta_servidor : "-" "Porta" ":" PORTA'''
        elems = porta_servidor.children
        porta = elems[0].value
        self.__set_server_port(porta)

    def rota_servidor(self,rota_servidor):
        '''rota_servidor : "-" "Rota" ":" ROTA'''
        elems = rota_servidor.children
        rota = elems[0].value
        self.__set_server_route(rota)

    def trabalhadores_servidor(self,trabalhadores_servidor):
        '''trabalhadores_servidor : "-" "Trabalhadores" ":" INT'''
        elems = trabalhadores_servidor.children
        workers = elems[0].value
        self.__set_server_workers(workers)

    def ferramentas(self,ferramentas):
        '''ferramentas : "*" "Ferramentas" ("--" ferramenta)+'''
        elems = ferramentas.children
        # visitar todas as ferramentas
        for elem in elems:
            self.visit(elem)

    def ferramenta(self,ferramenta):
        '''ferramenta : familia titulo descricao comando inputs?'''
        elems = ferramenta.children
        # visitar todas as opcoes
        for elem in elems:
            self.visit(elem)

    def familia(self,familia):
        '''familia : "-" "Familia" ":" NOME'''
        elems = familia.children
        familia_ferramenta = elems[0].value
        self.curFamily =familia_ferramenta
        self.__add_tool_family(familia_ferramenta)


    def titulo(self,titulo):
        '''titulo  : "-" "Titulo" ":" TEXTO'''
        elems = titulo.children
        titulo_ferramenta = elems[0].value[1:-1]
        self.curTool = titulo_ferramenta
        self.__add_tool(self.curFamily,titulo_ferramenta)


    def descricao(self,descricao):
        '''descricao : "-" "Descricao" ":" TEXTO'''
        elems = descricao.children
        descricao_ferramenta = elems[0].value[1:-1]
        self.__set_tool_description(self.curFamily,self.curTool, descricao_ferramenta)

    def comando(self,comando):
        '''comando : "-" "Comando" ":" comando_formato'''
        elems = comando.children
        # visitar comando_forma
        comando_formato = self.visit(elems[0])
        self.__set_tool_command(self.curFamily,self.curTool, comando_formato)

    def comando_formato(self,comando_formato):
        '''comando_formato : (NOME (opcoes | arg)*) (comando_operador comando_formato)*'''
        elems = comando_formato.children
        comando = ''
        nome = elems[0].value
        comando += f'{nome} '
        # visitar opcoes
        for elem in elems[1:]:
            opcao = self.visit(elem)
            comando += f'{opcao} '
        return comando
    
    
    def opcoes(self, opcoes):
        '''opcoes : INPUT
                  | FLAG'''
        elems = opcoes.children
        return elems[0].value
    
    def arg(self,arg):
        '''arg: TEXTO
              | PALAVRA'''
        elems = arg.children
        return elems[0].value

    def comando_operador(self,comando_operador):
        '''comando_operador : PIPE
                            | REDIRECIONAMENTO
                            | AND'''
        elems = comando_operador.children
        return elems[0].value

    def inputs(self,inputs):
        '''inputs : "-" "Inputs" ":" input+'''
        elems = inputs.children
        #visitar inputs
        for elem in elems:
            self.visit(elem)


    def input(self,input):
        '''input : "-" INPUT ":" opcoes_input'''
        elems = input.children
        input_id = elems[0].value
        # visitar opcoes
        opcoes = self.visit(elems[1])
        self.__add_tool_input(self.curFamily,self.curTool,input_id,opcoes)

    def opcoes_input(self,opcoes_input):
        '''opcoes_input : input_nome? input_descricao? input_tipo'''
        elems = opcoes_input.children
        opcoes = []
        # visitar opcoes
        for elem in elems:
            opcoes.append(self.visit(elem))
        return opcoes

    def input_nome(self,input_nome):
        '''input_nome : "-" "Nome" ":" NOME'''
        elems = input_nome.children
        input_nome = elems[0].value
        return ('nome',input_nome)

    def input_descricao(self,input_descricao):
        '''input_descricao : "-" "Descrição" ":" TEXTO'''
        elems = input_descricao.children
        input_desc = elems[0].value
        return ('descricao',input_desc)

    def input_tipo(self,input_tipo):
        '''input_tipo : "-" "Tipo" ":" TYPE '''
        elems = input_tipo.children
        input_tipo = elems[0].value
        if input_tipo == 'FILE':
            self.__add_tool_nfiles(self.curFamily,self.curTool)
        return ('tipo',input_tipo)
    
    def visuais(self,visuais):
        '''visuais : "*" "Visuais" favicon? colors?'''
        elems = visuais.children
        for elem in elems:
            self.visit(elem)

    def favicon(self, favicon):
        '''favicon : "-" "Favicon" ":" TEXTO'''
        elems = favicon.children
        texto = elems[0].value[1:-1]
        self.__set_favicon(texto)
    
    def colors(self,colors):
        '''colors : color+'''
        elems = colors.children
        for elem in elems:
            self.visit(elem)

    def color(self,color):
        '''color : "-" COLOR ":" HEXCODE'''
        elems = color.children
        tag = elems[0].value
        hexcode = elems[1].value
        self.__set_color(tag,hexcode)
    



def has_file_input(ferramentas):
    '''Verifica se alguma ferramenta tem ficheiro como input'''
    for _,tools in ferramentas.items():
        for _,config in tools.items():
            if config['n_files'] > 0:
                return True
    return False

def parse_config(config_file):
    '''Parse do ficheiro de configuracao utilizando a classe Interpreter'''
    config_text = config_file.read()
    config_file.close()
    try:
        p = Lark(grammar)
        parse_tree = p.parse(config_text)
        it = Interpreter()
    except Exception as e:
        print(e)
        print('Error : Configuration file not valid.')
    return it.visit(parse_tree)

def config_valid(config):
    '''Validar um dicionario como configuracao do servidor'''
    tool_fields = [('descricao',str),('comando',str)]
    input_fields = [('id',str),('opcoes',dict)]
    config_fields = [('nome',str),('diretoria',str),('porta',int),('ferramentas',dict)]

    colors_default = {
                    'primary_text_color' : '#000',
                    'secondary_text_color' : '#fff',
                    'primary_bg_color' : '#fff',
                    'secondary_bg_color' : '#3f51b5',
                    'label_color' : '#3f51b5',
                    'border_color' : '#9e9e9e',
                    }

    # verificar campos do servidor
    for field,t in config_fields:
        if field not in config or type(config[field]) != t:
            print(f'Error: error on field {field} | expected type "{t}"')
            return False
    # adicionar workers default se nao houver
    if 'workers' not in config or type(config['workers'] != int):
        config['workers'] = 1
    # adicionar rota default se nao houver
    if 'rota' not in config or type(config['rota'] != str):
        config['rota'] = '/'
    # ip default
    config['ip'] = '127.0.0.1'
    
    # verificar todas as familias
    for family,ferramentas in config['ferramentas'].items():
        # dicionario de ferramentas
        if type(ferramentas) != dict:
            print(f'Error: error on tool family {family}')
            return False
        # verificar ferramentas da familia
        for _,ferramenta in ferramentas.items():
            if type(ferramenta) != dict:
                print(f'Error: error on tool {ferramenta}')
                return False
            # verificar campos da ferramenta
            for field,t in tool_fields:
                if field not in ferramenta or type(ferramenta[field]) != t:
                    print(f'Error: error on tool {ferramenta} field "{field}" | expected type "{t}"')
                    return False
            # adicionar n_files default se nao houver
            if 'n_files' not in ferramenta:
                ferramenta['n_files'] = 0
            # adicionar inputs default se nao houver
            if 'inputs' not in ferramenta:
                ferramenta['inputs'] = []
                ferramenta['n_files'] = 0
            # verificar inputs
            else:
                if type(ferramenta['inputs']) != list:
                    print(f'Error: error on tool {ferramenta} input field')
                    return False
                # verificar cada input
                for input in ferramenta['inputs']:
                    if type(input) != dict:
                        print(f'Error: error on tool {ferramenta} input {input}')
                        return False
                    # verificar campos do input
                    for field,t in input_fields:
                        if field not in input or type(input[field]) != t:
                            print(f'Error: error on tool {ferramenta} input {input} field "{field}" | expected type "{t}"')
                            return False
                        
                    input_opcoes = input['opcoes']
                    # campo obrigatorio 'tipo'
                    if 'tipo' not in input_opcoes or type(input_opcoes['tipo']) != str:
                        print(f'Error: error on tool {ferramenta} input {input} field "tipo"')
                        return False
                    # se o tipo for ficheiro contar para o numero de input ficheiros
                    if input_opcoes['tipo'] == 'FILE':
                        ferramenta['n_files'] += 1
                    # campo nao obrigatorio mas que deve ter o tipo certo
                    if 'nome' in input_opcoes and type(input_opcoes['nome']) != str:
                        print(f'Error: error on tool {ferramenta} input {input} field "nome"')
                        return False
                    # campo nao obrigatorio mas que deve ter o tipo certo
                    if 'descricao' in input_opcoes and type(input_opcoes['descricao']) != str:
                        print(f'Error: error on tool {ferramenta} input {input} field "descricao"')
                        return False
    # verificar visuais
    if 'visuais' in config:
        if 'favicon' in config['visuais']:
            if  type(config['visuais']['favicon']) != str :
                return False
        else:
            config['visuais']['favicon'] = ''
        if 'colors' in config['visuais']:
            tags = [('primary_text_color','#000'),
                    ('secondary_text_color','#fff'),
                    ('primary_bg_color','#fff'),
                    ('secondary_bg_color','#3f51b5'),
                    ('label_color','#3f51b5'),
                    ('border_color','#9e9e9e'),]
            
            for (tag,default) in tags:
                if tag in config['visuais']['colors']:
                    if type(config['visuais']['colors'][tag]) != str :
                        return False
                else:
                    config['visuais']['colors'][tag] = default
        else:
            config['visuais']['colors'] = colors_default
    else:
        config['visuais'] = {
                'favicon' : '',
                'colors' : colors_default
            }

    return True
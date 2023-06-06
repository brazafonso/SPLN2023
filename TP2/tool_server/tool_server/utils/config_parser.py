'''Ficheiro com parser do ficheiro de configuracao do servidor'''

from lark.tree import pydot__tree_to_png
from lark.visitors import Interpreter
from lark import Lark,Discard ,Token,Tree


grammar = '''
start : servidor
servidor : "*" "Servidor" opcoes_servidor ferramentas
opcoes_servidor : nome_servidor diretoria_servidor ip_servidor porta_servidor  rota_servidor? trabalhadores_servidor?
nome_servidor : "-" "Nome" ":" NOME
diretoria_servidor : "-" "Diretoria" ":" TEXTO
ip_servidor : "-" "IP" ":" IP
porta_servidor : "-" "Porta" ":" PORTA
rota_servidor : "-" "Rota" ":" ROTA
trabalhadores_servidor : "-" "Trabalhadores" ":" INT

ferramentas : "*" "Ferramentas" ("--" ferramenta)+
ferramenta : familia titulo descricao comando inputs? outputs?
familia : "-" "Família" ":" NOME
titulo  : "-" "Título" ":" TEXTO
descricao : "-" "Descrição" ":" TEXTO
comando : "-" "Comando" ":" comando_formato
comando_formato : NOME opcoes* 
opcoes : INPUT
        | OUTPUT
        | FLAG
inputs : "-" "Inputs" ":" input+
input : "-" INPUT ":" opcoes_input
opcoes_input : input_nome? input_descricao? input_tipo
input_nome : "-" "Nome" ":" NOME 
input_descricao : "-" "Descrição" ":" TEXTO 
input_tipo : "-" "Tipo" ":" TYPE 
outputs : "-" "Outputs" ":" output+
output : "-" OUTPUT ":" opcoes_output
opcoes_output : output_nome? output_descricao? output_tipo
output_nome : "-" "Nome" ":" NOME 
output_descricao : "-" "Descrição" ":" TEXTO 
output_tipo : "-" "Tipo" ":" TYPE 

IP: /(\d{1,4}\.){3}\d{1,4}/
PORTA: /\d+/
ROTA: /[\w\-\/]+/
STR: /"[^"]"/
TEXTO: /"[^"]*"/
NOME: /[\w\-]+/
INPUT: /INPUT\d+/
OUTPUT: /OUTPUT\d+/
FLAG: /-\w+/
TYPE: /(STR)|(NUM)|(FILE)|(FOLDER)/

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

    def __add_tool(self,familia,titulo_ferramenta):
        '''Adiciona uma nova ferramenta no dicionario de ferramentas'''
        self.server_config['ferramentas'][familia][titulo_ferramenta] = {
            'descricao' : '',
            'comando' : '',
            'inputs' : [],
            'outputs' : []
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
        self.server_config['ferramentas'][familia][tool]['inputs'].append((input_id, dict(input_opcoes)))

    def __add_tool_output(self,familia,tool,output_id, output_opcoes):
        '''Adiciona um output a uma ferramenta'''
        self.server_config['ferramentas'][familia][tool]['outputs'].append((output_id, dict(output_opcoes)))


    
    def __init__(self):
        self.server_config = {
            'nome' : '',
            'diretoria' : '',
            'ip' : '',
            'porta' : '',
            'rota' : '',
            'workers' : '',
            'ferramentas' : {}
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
        '''servidor : "*" "Servidor" opcoes_servidor ferramentas'''
        elems = servidor.children
        # visitar opcoes_servidor
        self.visit(elems[0])
        # visitar ferramentas
        self.visit(elems[1])

    def opcoes_servidor(self,opcoes_servidor):
        '''opcoes_servidor : nome_servidor diretoria_servidor ip_servidor porta_servidor  rota_servidor? trabalhadores_servidor?'''
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

    def ip_servidor(self,ip_servidor):
        '''ip_servidor : "-" "IP" ":" IP'''
        elems = ip_servidor.children
        ip = elems[0].value
        self.__set_server_ip(ip)

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
        '''ferramenta : familia titulo descricao comando inputs? outputs?'''
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
        '''comando_formato : NOME opcoes*'''
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
                  | OUTPUT
                  | FLAG'''
        elems = opcoes.children
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
        return ('tipo',input_tipo)

    def outputs(self,outputs):
        '''outputs : "-" "Outputs" ":" output+'''
        elems = outputs.children
        #visitar outputs
        for elem in elems:
            self.visit(elem)

    def output(self,output):
        '''output : "-" OUTPUT ":" opcoes_output'''
        elems = output.children
        output_id = elems[0].value
        # visitar opcoes
        opcoes = self.visit(elems[1])
        self.__add_tool_output(self.curFamily,self.curTool,output_id,opcoes)

    def opcoes_output(self,opcoes_output):
        '''opcoes_output : output_nome? output_descricao? output_tipo'''
        elems = opcoes_output.children
        opcoes = []
        # visitar opcoes
        for elem in elems:
            opcoes.append(self.visit(elem))
        return opcoes

    def output_nome(self,output_nome):
        '''output_nome : "-" "Nome" ":" NOME'''
        elems = output_nome.children
        output_nome = elems[0].value
        return ('nome',output_nome)

    def output_descricao(self,output_descricao):
        '''input_descricao : "-" "Descrição" ":" TEXTO'''
        elems = output_descricao.children
        output_desc = elems[0].value
        return ('descricao',output_desc)

    def output_tipo(self,output_tipo):
        '''input_tipo : "-" "Tipo" ":" TYPE '''
        elems = output_tipo.children
        output_tipo = elems[0].value
        return ('tipo',output_tipo)


    




def parse_config(config_file):
    '''Parse do ficheiro de configuracao utilizando a classe Interpreter'''
    config_text = config_file.read()
    config_file.close()

    p = Lark(grammar)
    parse_tree = p.parse(config_text)
    it = Interpreter()
    return it.visit(parse_tree)



#TODO: 
# verificar porta, ip, inputs e outputs
def config_valid(config):
    return True
'''Ficheiro com funcoes para configuracao do servidor'''

import re
import os

def config_server(server_dir,config_file):
    '''Modificar configuracoes do servidor'''

    # www file (ip and port changed)
    __www_file(f'{server_dir}/bin/www',config_file['ip'],config_file['porta'])

    # layout.pug file (alterar titulo do layout)
    __layout_pug_file(f'{server_dir}/views/layout.pug',config_file['nome'])

    family_names = sorted(config_file['ferramentas'].keys())
    __index_pug_file(f'{server_dir}/views/index.pug',config_file['nome'],family_names, config_file['ferramentas'])


def __www_file(www_path,ip,porta):
    '''Modificar configuracoes do servidor, porta e ip'''
    www_file = open(www_path,'r')
    www = www_file.read()
    www_file.close()
    www = re.sub(r'\$ip',f'\"{ip}\"',www)
    www = re.sub(r'\$port',f'\"{porta}\"',www)
    www_file = open(www_path,'w')
    www_file.write(www)
    www_file.close()

def __layout_pug_file(layout_path,nome):
    '''Modificar configuracoes do layout, titulo'''
    layout_file = open(layout_path,'r')
    layout = layout_file.read()
    layout_file.close()
    layout = re.sub(r'title=(.*)',f'title {nome}',layout)
    layout_file = open(layout_path,'w')
    layout_file.write(layout)
    layout_file.close()

def __index_pug_file(index_path, name, tool_names):
    '''Criar o index do servidor. '''
    index_file = open(index_path,'w+')

    index = f"""
extends layout

block content
    h1 {name}
    p Welcome to #{name}
"""
    
    for tool_name in tool_names:
        index+=f"""
    h2 {tool_name}
"""

    index_file.write(index)
    index_file.close()
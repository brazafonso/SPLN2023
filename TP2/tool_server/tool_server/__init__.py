#! /usr/bin/env python3
"""Module to create tools server
"""

import os
import shutil
import subprocess
import argparse
import sys
from .utils.utils import *
from .utils.config_parser import *
from .utils.config_server import *

__version__ = '0.1'
project_dir = os.path.dirname(os.path.realpath(__file__))
model_server = f'{project_dir}/model'


def start_server(server_dir,config):
    '''Inicia o servidor'''
    server_path = f'{os.getcwd()}/{server_dir}'
    if has_file_input(config['ferramentas']):
        dependencies = ' '.join(['express','http-errors','multer','adm-zip'])
    else:
        dependencies = ' '.join(['express','http-errors','adm-zip'])
    print('Installing server dependencies')
    p = subprocess.call(f'npm i {dependencies} -s', cwd=server_path,shell=True)
    print('Dependencies installed')
    print('Starting server')
    p = subprocess.call(f'npm start', cwd=server_path,shell=True)

def tool_server():
    args = parse_arguments(__version__)
    config_file = args.config_file
    config = parse_config(config_file[0])

    if config_valid(config):
        #Copiar o modelo do servidor para a diretoria desejada
        destino = config['diretoria'] + '/' + config['nome']
        origem = model_server
        try:
            shutil.copytree(origem, destino)
        except FileNotFoundError:
            print("Servidor modelo não encontrado!")
            exit(-1)
        except FileExistsError:
            print("A diretoria de destino já existe.")
            exit(-1)
        except Exception as e:
            print(f"Erro ao copiar o modelo do servidor: {e}")
            exit(-1)
        # alterar configuracoes do servidor
        config_server(destino,config)

        #iniciar servidor
        if args.start_server:
            start_server(destino,config)
    else:
        print('Erro no ficheiro de configuração')
        exit(-1)

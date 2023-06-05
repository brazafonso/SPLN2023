#! /usr/bin/env python3
"""Module to create tools server
"""

import os
import shutil
import argparse
import sys
from .utils.utils import *
from .utils.config_parser import *
from .utils.config_server import *

__version__ = '0.1'
project_dir = os.path.dirname(os.path.realpath(__file__))
model_server = f'{project_dir}/model'


def start_server(server_dir):
    '''Inicia o servidor'''
    print(server_dir)
    os.system(f'cd {server_dir} & npm i -s & npm start')

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
        start_server(destino)
    else:
        print('Erro no ficheiro de configuração')
        exit(-1)

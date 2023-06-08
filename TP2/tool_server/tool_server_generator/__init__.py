#! /usr/bin/env python3
"""Module to create tools server
"""

import os
import shutil
import subprocess
from pyngrok import ngrok
from .utils.utils import *
from .utils.config_parser import *
from .utils.config_server import *

__version__ = '0.3.3'
project_dir = os.path.dirname(os.path.realpath(__file__))
model_server = f'{project_dir}/model'
tunnel = None

def start_ngrok(config):
    '''Tenta expor a porta do servidor utilizando o ngrok'''
    global tunnel
    try:
        print(ngrok.get_tunnels())
        print('Exposing port using ngrok')
        tunnel = ngrok.connect(config['porta'],'http')
        print('Port exposed',tunnel)
        print('Public URL',tunnel.public_url)
    except Exception as e:
        print(e)
        print('Error: Could not expose port using ngrok.')
        tunnel = None


def start_server(server_dir,config):
    '''Inicia o servidor'''
    global tunnel
    server_path = f'{os.getcwd()}/{server_dir}'
    dependencies = ['express','http-errors','adm-zip']

    # multer apenas se ferramentas levarem ficheiros como input
    if has_file_input(config['ferramentas']):
        dependencies += ['multer']
        
    dependencies = ' '.join(dependencies)
    print(f'Installing server dependencies: [{dependencies}]')
    p = subprocess.call(f'npm i {dependencies} -s', cwd=server_path,shell=True)
    print('Dependencies installed')
    print('Starting server')
    p = subprocess.call(f'npm start', cwd=server_path,shell=True)
    print('Server closed')
    # desconectar ngrok
    if tunnel:
        print('Closing ngrok')
        ngrok.disconnect(tunnel.public_url)

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

        # expor porta de ngrok
        if args.ngrok:
            start_ngrok(config)

        #iniciar servidor
        if args.start_server:
            start_server(destino,config)
    else:
        print('Erro no ficheiro de configuração')
        exit(-1)

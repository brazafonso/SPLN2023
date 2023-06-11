#! /usr/bin/env python3
"""Module to create tools server
"""

import os
import shutil
import subprocess
import json
from pyngrok import ngrok
from .utils.utils import *
from .utils.config_parser import *
from .utils.config_server import *

__version__ = '0.4.4'
project_dir = os.path.dirname(os.path.realpath(__file__))
model_server = f'{project_dir}/model'
tunnel = None

def start_ngrok(config):
    '''Tenta expor a porta do servidor utilizando o ngrok'''
    global tunnel
    try:
        print(ngrok.get_tunnels())
        print('LOG: Exposing port using ngrok')
        tunnel = ngrok.connect(config['porta'],'http')
        print('Public URL: ',tunnel.public_url)
    except Exception as e:
        print(e)
        print('Error: Could not expose port using ngrok.')
        tunnel = None

def install_server_dependencies(server_dir,config):
    '''Instala as dependencias do servidor'''
    server_path = f'{os.getcwd()}/{server_dir}'
    dependencies = ['express','http-errors','adm-zip']

    # multer apenas se ferramentas levarem ficheiros como input
    if has_file_input(config['ferramentas']):
        dependencies += ['multer']
        
    dependencies = ' '.join(dependencies)
    print(f'LOG: Installing server dependencies: [{dependencies}]')
    p = subprocess.call(f'npm i {dependencies} -s', cwd=server_path,shell=True)
    print('LOG: Dependencies installed')


def start_server(server_dir):
    '''Inicia o servidor'''
    global tunnel
    server_path = f'{os.getcwd()}/{server_dir}'
    try:
        print('LOG: Starting server')
        p = subprocess.call(f'npm start', cwd=server_path,shell=True)
    except Exception as e:
        print('LOG: Server closed')
        # desconectar ngrok
        if tunnel:
            print('LOG: Closing ngrok')
            ngrok.disconnect(tunnel.public_url)

def tool_server():
    args = parse_arguments(__version__)
    config_file = args.config_file[0]
    file = open(config_file,'r',encoding='utf-8')
    json_config = False
    # ficheiro json
    if config_file.endswith('.json'):
        json_config = True
        config = dict(json.load(file))
        file.close()
    # outro tipo
    else:
        config = parse_config(file)

    if not json_config or config_valid(config):
        #Copiar o modelo do servidor para a diretoria desejada
        destino = config['diretoria'] + '/' + config['nome']
        origem = model_server
        try:
            shutil.copytree(origem, destino)
        except FileNotFoundError:
            print("Error: Model Server not found!")
            exit(-1)
        except FileExistsError:
            print("Error: Directory already exists.")
            exit(-1)
        except Exception as e:
            print(f"Error: Error copying the model server: {e}")
            exit(-1)
        
        # alterar configuracoes do servidor
        config_server(destino,config)

        if config['visuais']['favicon'] != '':
            favicon = config['visuais']['favicon']
            old_favicon = destino + '/public/images/favicon.ico'
            destino_favicon = destino + '/public/images/favicon.ico'

            #remover favicon default que vem do model
            os.remove(old_favicon)
            
            #colocar o dado
            try:
                shutil.copy(favicon,destino_favicon)
            except FileNotFoundError:
                print("Error: Favicon not found!")
                exit(-1)
            except Exception as e:
                print(f"Error: Error copying the favicon: {e}")
                exit(-1)
        # instalar dependencias do servidor
        install_server_dependencies(destino,config)

        #iniciar servidor
        if args.start_server:
            # expor porta de ngrok
            if args.ngrok:
                start_ngrok(config)

            start_server(destino)
    else:
        print('Error: Error on the configuration file.')
        exit(-1)

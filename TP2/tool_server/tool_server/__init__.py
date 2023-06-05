#! /usr/bin/env python3
"""Module to create tools server
"""

import os
import shutil
import argparse
import sys
from .utils import parse_config, config_valid

__version__ = '0.1'
project_dir = os.getcwd()
model_server = f'{project_dir}/model'

def parse_arguments(version)->argparse.Namespace:
    """Process arguments from stdin"""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description=f'''
    --------------------------------------------------------------------
                        **Tool Server**
    --------------------------------------------------------------------'''
    )
    parser.add_argument('config_file',metavar='filename',type=argparse.FileType('r'),nargs=1,help='configure file')
    return parser.parse_args()


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
        except FileExistsError:
            print("A diretoria de destino já existe.")
        except Exception as e:
            print(f"Erro ao copiar o modelo do servidor: {e}")
    else:
        print('Erro no ficheiro de configuração')

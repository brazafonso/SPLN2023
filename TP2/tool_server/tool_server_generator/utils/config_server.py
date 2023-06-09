'''Ficheiro com funcoes para configuracao do servidor'''

import re
import os
from .config_parser import *

html_types = {
    'STR' : 'text',
    'NUM' : 'number',
    'FILE' : 'file'
}

def config_server(server_dir,config_file):
    '''Modificar configuracoes do servidor'''

    # www file (ip and port changed)
    __www_file(f'{server_dir}/bin/www',config_file['ip'],config_file['porta'])


    #nome das ferramentas organizado por familias
    ferramentas = config_file['ferramentas']
    families = {family:list(tools.keys()) for family,tools in ferramentas.items()}

    # layout.pug file (alterar titulo do layout)
    __layout_pug_file(f'{server_dir}/views/layout.pug',config_file['nome'],families)

    # index.pug file (criar a view inicial do servidor com botoes para as ferramentas)
    #__index_pug_file(f'{server_dir}/views/index.pug',config_file['nome'],families)

    # {family}_{tool}.pug file (criar uma view para cada conjunto de ferramentas)
    __tool_pug_file(f'{server_dir}/views', config_file)

    # criar rota para cada familia e ferramenta
    __server_create_routes(f'{server_dir}/routes/index.js',config_file)

    # alterar cores do css
    __css_color_file(f'{server_dir}/public/stylesheets/color.css',config_file['visuais']['colors'])


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


def __sidebar_tools(families):
    sidebar = ""
    for family,tools in families.items():
        sidebar += f"""
      button.w3-button.w3-block.w3-left-align(onclick="open_tools('{family}')") {family} 
            i.fa.fa-caret-down
      .w3-hide(id="{family}")"""
        for tool in tools:
            tool_re = tool.replace(' ','_')
            sidebar += f"""
        a.w3-bar-item.w3-button(href="/{family}/{tool_re}") {tool}"""
    return sidebar

def __layout_pug_file(layout_path,nome,families):
    '''Modificar configuracoes do layout, titulo'''
    layout_file = open(layout_path,'r')
    layout = layout_file.read()
    layout_file.close()
    layout = re.sub(r'\$title',f'{nome}',layout)
    layout = re.sub(r'\$tools',__sidebar_tools(families),layout)
    layout_file = open(layout_path,'w')
    layout_file.write(layout)
    layout_file.close()


def __pug_input_field(type,id):
    return f'''input.w3-input.w3-round.w3-border.border_color.primary_bg_color.primary_text_color(type="{html_types[type]}" name="{id}")'''


def __tool_pug_file_desc(descricao):
    '''Retorna o pug da descricao de uma ferramenta'''
    pug = ''
    for line in descricao.splitlines():
                pug += f'''
        p {line}'''
    return pug

def __tool_pug_file_form(config):
    '''Retorna o pug do form de uma ferramenta'''
    inputs = config['inputs']
    pug =''
    pug +='''
            form.w3-container.w3-border.border_color(method="post"'''
    # permite upload de ficheiros se for o caso
    if config['n_files'] > 0:
        pug += ',enctype="multipart/form-data",style="overflow: hidden;"'
    pug+=''')'''

    if len(inputs)>0:
        pug+='''
                h3 Inputs'''
    # botao para cada input
    for input in inputs:
        id = input['id']
        input_dict = input['opcoes']
        nome = input_dict['nome'] if input_dict['nome'] else id
        input_type = input_dict['tipo']
        pug += '''
                label.w3-left.label_color'''
        if ('descricao' in input_dict):
            descricao = input_dict['descricao']
            pug += f'''
                    p.w3-tooltip
                        b {nome} 
                        span.w3-text {descricao}'''
        else:
            pug += f'''
                    b {nome}'''
        pug += f'''
                {__pug_input_field(input_type,id)}
                br'''
    pug += f'''
                input(type="hidden" name="command" value="{config['comando']}")
                br
                button.w3-button.secondary_bg_color.secondary_text_color.w3-mb-2(type="submit") Submit
                br
                br
'''
    return pug


def __tool_pug_file(path, server_config):
    ferramentas = server_config['ferramentas']
    base_route = server_config['rota']
    '''Criar a view de cada ferramenta'''
    for family,tools in ferramentas.items():
        for tool,config in tools.items():
            tool_re = tool.replace(' ','_')
            descricao = config['descricao']
            # header
            pug = f'''
extends layout
block content
    .w3-container
        h3 Description
'''         
            # descricao
            pug += __tool_pug_file_desc(descricao)

            pug += """
    .w3-container.secondary_bg_color.secondary_text_color
        p
    .w3-container
        br
        .w3-container(style="width:40%;margin:auto;")
"""
            # form
            pug += __tool_pug_file_form(config)
            
            pug += f'''
    br
'''
            
            tool_file = open(f'{path}/{family}_{tool_re}.pug','w+')
            tool_file.write(pug)
            tool_file.close()


def __server_create_routes_multer():
    '''Retorna o js necessario para a preparacao do multer'''
    index = ''
    index += '''
const multer = require("multer")
// criar pasta de uploads se nao houver
if(!fs.existsSync(path.join('uploads')))
    fs.mkdirSync(path.join('uploads'))
const storageEngine = multer.diskStorage({
  destination: (req, file, cb) => { cb(null, './uploads') },
  filename: (req, file, cb) => { cb(null, Date.now() + '_' + file.originalname) }, })
        '''
    return index


def __server_create_routes_tool_post_multer(family,tool,config,base_route):
    '''Retorna o js da rota de post para uma ferramenta que receba ficheiros de input'''
    tool_re = tool.replace(' ','_')
    index = ''
    # middleware para processamento dos inputs ficheiros
    index += f'''
const upload_{family}_{tool_re} = multer({'{'} storage: storageEngine {'}'}).fields(['''
    # adicioanr field para cada input ficheiro
    for input in config['inputs']:
        id = input['id']
        opcoes = input['opcoes']
        if opcoes['tipo'] == 'FILE':
            index +=f'''
    {'{'} name: '{id}', maxCount: 1 {'}'},
                '''
    index = index[:-1] # retirar ultima ','
    index += '''
    ]);
    '''
    # rota com middleware
    index += f'''
router.post('{base_route}{family}/{tool_re}', function(req, res) {'{'}
    upload_{family}_{tool_re}(req, res, (err) => {'{'}
        if (err) {'{'}
        console.error(err);
        return res.status(500).json({'{'} error: 'Erro no upload dos arquivos' {'}'});
        {'}'}
    process_command(req);
    res.render('{family}_{tool_re}', {'{'} title: '{family}' {'}'});
{'}'});{'}'});
''' 
    return index


def __server_create_routes_tool(family,tool,config,base_route):
    '''Retorna o js das rotas para uma ferramenta'''
    tool_re = tool.replace(' ','_')
    index =''
    # rota get da ferramenta
    index += f'''
router.get('{base_route}{family}/{tool_re}', function(req, res, next) {'{'}
    res.render('{family}_{tool_re}', {'{'} title: '{family}' {'}'});
{'}'});
''' 
    # rota post da ferramenta
    n_files = config['n_files']
    if n_files:
        # multer
        index += __server_create_routes_tool_post_multer(family,tool,config,base_route)
    else:
        # simples
        index += f'''
router.post('{base_route}{family}/{tool_re}', function(req, res) {'{'}
    process_command(req);
    res.render('{family}_{tool_re}', {'{'} title: '{family}' {'}'});
{'}'});
'''
    return index

def __server_create_routes(index_path,server_config):
    '''Cria as rotas para cada uma das ferramentas e familias'''
    ferramentas = server_config['ferramentas']
    workers = server_config['workers']
    base_route = server_config['rota']

    file = open(index_path,'r')
    index = file.read()
    file.close()
    # alterar numero de threads base
    index = index.replace('$threads',f'{workers}')
    index = index.splitlines()
    # guardar e retirar ultima linha (module.exports = router;)
    export_router = index[-1]
    index = "\n".join(index[:-1])

    # multer para o upload de ficheiros para o servidor
    if has_file_input(ferramentas):
        index += __server_create_routes_multer()

    # criar rota das ferramentas
    for family,tools in ferramentas.items():
        for tool,config in tools.items():
            index += __server_create_routes_tool(family,tool,config,base_route)
             

    # adicionar ultima linha (module.exports = router;)
    index += f'''
{export_router}'''
    file = open(index_path,'w')
    file.write(index)
    file.close()


def __change_color(css, tag, color):
    return css.replace(tag,color)

def __css_color_file(css_path,colors):
    file = open(css_path, 'r')
    css = file.read()
    file.close()

    for tag in colors:
        css = __change_color(css,f'${tag}',colors[tag])

    file = open(css_path,'w')
    file.write(css)
    file.close()
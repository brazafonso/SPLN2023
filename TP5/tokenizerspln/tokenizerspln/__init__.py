#! /usr/bin/env python3
"""Module to tokenize books
"""

__version__ = '0.4'

import re
from .utils import *

list_poemas = []


def remove_empty(l):
    new_list = [x.strip() for x in l if x.strip()]
    return new_list
    

def load_abrev():
    file = open('conf/abrev.txt','r')
    txt = file.read()
    ln_list = txt.split('#')
    ln_list = remove_empty(ln_list)
    abrev_dic = {}
    for lan in ln_list:
        ln,*abrevs = remove_empty(lan.split('\n'))
        abrev_dic[ln] = abrevs
    return abrev_dic

def treat_page_break(args,text):
    """If flagged or default removes page breaks"""
    regex_nl = r'([a-z.0-9,;\-–?!\(\)])(\n\n)+([a-zA-Z.0-9,;\-–?!\(\)])'
    return re.sub(regex_nl,r'\1\n\3',text)

def treat_punctuation(args,text):
    """If flagged or default separates punctuation from words"""
    regex_punc = r'([.!,?;:' + r'\"\-\”\–\`()\[\]])?(\w+)([.!,?;:' + r'\"\-\”\–\`()\[\]])'
    return re.sub(regex_punc,r'\1 \2 \3',text)


def treat_chapters(args,text):
    """If flagged or default tags chapters with the '#' delimeter\n
       Further subtitles or descriptions of the chapter will be delimeted between '[' and ']'
    """
    regex_cap = r'.*(CAPÍTULO +(\w+|\d+)).*\n((.+\n)*)'
    return re.sub(regex_cap,r'#\1\n[\3]\n',text)

def treat_paragraphs(args,text):
    """If flagged or default separates paragraphs from simple sentences with the '/PAR/' delimiter"""
    regex_par = r'([.!?;])\n(([^.!?;]|[\u00C0-\u017F]))'
    return re.sub(regex_par,r'\1\n/PAR/ \2',text)

def treat_sentences_single_line(args,text):
    """If flagged or default unifies sentences into a single line"""
    regex_sen = r'([^.!?])\n+([^.!?])'
    return re.sub(regex_sen,r'\1 \2',text)

def treat_sentences_per_line(args,text):
    """If flagged or default seperates every sentence in differente lines"""
    regex_sen = r'([^.!?][.?!])(\s|[^.])'
    text = re.sub(regex_sen,r'\1\2\n',text)
    regex_abrv = r'((Sr)|(Sra))\.(\s*)\n'
    # utilizar dicionario das abreviaturas para completar a expressao regular
    # permitir opção de linguas para usar apenas um conjunto de abreviaturas
    return re.sub(regex_abrv,r'\1.\4',text)


def save_poems(poema):
    """Saves a poem in a data structure"""
    list_poemas.append(poema[1])
    return f">>{len(list_poemas)}<<"

def treat_poems(args,text):
    """If flagged removes poems from text and saves it on data structure\n
       Poems need to be marked between <poem> and </poem>
    """
    if args.poem:
        regex_poema = r'<poem>(.*?)</poem>'
        text = re.sub(regex_poema,save_poems,text,flags=re.S)
        print(list_poemas)
    return text

def tokenizer():
    args = process_arguments(__version__)
    #print(args)
    #procedure_dic = process_arguments()
    text = get_input(args)
    
    # 0. Quebra de pagina
    # 1. Separar pontuação das palavras
    # 2. Marcar capitulos
        #* titulo do capitulo na linha seguinte 
        #* keywords para procurar por capitulo (ex.: multilingua)
    # 3. Separar paragrafos de linhas pequenas
    # 4. Juntar linhas da mesma frase
    # 5. Uma frase por linha
    # 6. Tratar Poemas (tagged)


    # 6. Tratar Poemas (tagged)
    text = treat_poems(args,text)

    # 2. Marcar capitulos
    text = treat_chapters(args,text)

    # 0. Quebra de pagina
    text = treat_page_break(args,text)
    
    # 3. Separar paragrafos de linhas pequenas
    text = treat_paragraphs(args,text)

    # 4. Juntar linhas da mesma frase
    text = treat_sentences_single_line(args,text)

    # 5. Uma frase por linha
    text = treat_sentences_per_line(args,text)

    # 1. Separar pontuação das palavras
    text = treat_punctuation(args,text)

    write_output(args,text)


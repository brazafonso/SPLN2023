#! /usr/bin/env python3
"""Module to tokenize books
"""

__version__ = '0.4'

import re
import os
from .utils import *

list_poemas = []
path = os.path.dirname(os.path.realpath(__file__))

def remove_empty(l):
    new_list = [x.strip() for x in l if x.strip()]
    return new_list
    



def treat_page_break(args,text):
    """If flagged or default removes page breaks"""
    regex_nl = r'([a-z.0-9,;\-–?!\(\)])(\n\n)+([a-zA-Z.0-9,;\-–?!\(\)])'
    return re.sub(regex_nl,r'\1\n\3',text)

def treat_punctuation(args,text):
    """If flagged or default separates punctuation from words"""
    regex_punc = r'([.!,?;:' + r'\"\-\”\–\`()\[\]])?(\w+)([.!,?;:' + r'\"\”\–\`()\[\]])'
    text = re.sub(regex_punc,r'\1 \2 \3',text)

    """Fixes abreviatures, default recognizes english"""
    abrevs = load_abrev()
    regex_abrv,groups = make_regex_abrevs(args,abrevs)
    if regex_abrv:
        regex_abrv += r'\s*\.'
        text = re.sub(regex_abrv,r'\1.',text)
    return text 


def treat_chapters(args,text):
    """If flagged or default tags chapters with the '#' delimeter\n
       Further subtitles or descriptions of the chapter will be delimeted between '[' and ']'
    """
    regex_cap = r'.*(CAPÍTULO +(\w+|\d+)).*\n(.*)(\n\n)+'
    return re.sub(regex_cap,r'#\1\n[\3]\n/PAR/',text)

def treat_paragraphs(args,text):
    """If flagged or default separates paragraphs from simple sentences with the '/PAR/' delimiter"""
    regex_par = r'([.!?;])\n(([^.!?;]|[\u00C0-\u017F]))'
    return re.sub(regex_par,r'\1\n/PAR/ \2',text)

def treat_sentences_single_line(args,text):
    """If flagged or default unifies sentences into a single line"""
    regex_sen = r'([^.!?])\n+([^.!?])'
    text = re.sub(regex_sen,r'\1 \2',text)
    """Fix Chapters"""
    regex_chap = r'(#CAPÍTULO +(\w+|\d+) \[.*\])'
    text = re.sub(regex_chap,r'\1\n',text)
    return text


def load_abrev():
    """Loads abreviatures from the config file"""
    file = open(f'{path}/conf/abrev.txt','r')
    txt = file.read()
    file.close()
    ln_list = txt.split('#')
    ln_list = remove_empty(ln_list)
    abrev_dic = {}
    for lan in ln_list:
        ln,*abrevs = remove_empty(lan.split('\n'))
        abrev_dic[ln] = abrevs
    return abrev_dic

def make_regex_abrevs(args,abrevs):
    """Creates regex expression to catch abreviatures from the given dict in the same group'
    By default will only use the english abreviatures
    """
    regex = r'('
    one_abrev = False
    groups = 1
    for lan in abrevs:
        for i,abr in enumerate(abrevs[lan]):
            one_abrev = True
            regex += r'(' + abr + r')'
            groups += 1
            if i != len(abrevs[lan])-1:
                regex += r'|'
    
    regex += r')'
    return (regex,groups) if one_abrev else (None,groups)

def treat_sentence_per_line(args,text):
    """If flagged or default seperates every sentence in differente lines"""
    regex_sen = r'([^.!?][.?!])( |[^.\n])'
    text = re.sub(regex_sen,r'\1\2\n',text)
    
    """Fixes abreviatures, default recognizes english"""
    abrevs = load_abrev()
    regex_abrv,groups = make_regex_abrevs(args,abrevs)
    #FIXME utilizar dicionario das abreviaturas para completar a expressao regular
    #FIXME permitir opção de linguas para usar apenas um conjunto de abreviaturas
    if regex_abrv:
        regex_abrv += r'\.(\s*)\n'
        text = re.sub(regex_abrv,rf'\1.\{groups+1}',text)
    return text


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
    text = get_input(args)
    
    # 0. Quebra de pagina
    # 1. Separar pontuação das palavras
    # 2. Marcar capitulos
        #*FIXME titulo do capitulo na linha seguinte 
        #*FIXME keywords para procurar por capitulo (ex.: multilingua)
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
    text = treat_sentence_per_line(args,text)

    # 1. Separar pontuação das palavras
    text = treat_punctuation(args,text)
    write_output(args,text)


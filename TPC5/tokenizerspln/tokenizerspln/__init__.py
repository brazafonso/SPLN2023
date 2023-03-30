#! /usr/bin/env python3
"""Module to tokenize books
"""

__version__ = '0.5'

import re
import os
from .utils import *

list_poemas = []
path = os.path.dirname(os.path.realpath(__file__))

def remove_empty(l):
    new_list = [x.strip() for x in l if x.strip()]
    return new_list
    
def make_regex_lan(args,dict):
    """
    Creates regex expression to catch elments from the given languages dict in the same group\n
    """
    regex = r'('
    one_abrev = False
    groups = 1
    for lan in dict:
        for i,abr in enumerate(dict[lan]):
            one_abrev = True
            regex += r'(' + abr + r')'
            groups += 1
            if i != len(dict[lan])-1:
                regex += r'|'
    
    regex += r')'
    return (regex,groups) if one_abrev else (None,groups)

def load_translations(args,file_path):
    """
    Loads translations from the config file, only gathers the translations of the defined language\n
    English by default
    """
    file = open(f'{path}{file_path}','r')
    txt = file.read()
    file.close()
    ln_list = txt.split('#')
    ln_list = remove_empty(ln_list)
    dic = {}
    for elem in ln_list:
        ln,*translations = remove_empty(elem.split('\n'))
        if args.language[0] in ln:
            dic[ln] = translations
            break
    return dic

def treat_page_break(args,text):
    """If flagged or default removes page breaks"""
    if is_default() or '-pb' in args.options:
        regex_nl = r'([a-z.0-9,;\-–?!\(\)])(\n\n)+([a-zA-Z.0-9,;\-–?!\(\)])'
        text = re.sub(regex_nl,r'\1\n\3',text)
    return text

def treat_punctuation(args,text):
    """If flagged or default separates punctuation from words"""
    if is_default() or '-pu' in args.options:
        regex_punc = r'([.!,?;:' + r'\"\-\”\–\`()\[\]])?(\w+)([.!,?;:' + r'\"\”\–\`()\[\]])'
        text = re.sub(regex_punc,r'\1 \2 \3',text)

        """Fixes abreviatures, default recognizes english"""
        abrevs = load_translations(args,'/conf/abrev.txt')
        regex_abrv,groups = make_regex_lan(args,abrevs)
        if regex_abrv:
            regex_abrv += r'\s*\.'
            text = re.sub(regex_abrv,r'\1.',text)
    return text 



def treat_chapters(args,text):
    """If flagged or default tags chapters with the '#' delimeter\n
       Further subtitles or descriptions of the chapter will be delimeted between '[' and ']'
    """
    if is_default() or '-c' in args.options:
        chapter_delims = load_translations(args,'/conf/chapter_delim.txt')
        regex_caps,groups = make_regex_lan(args,chapter_delims)
        regex_cap = r'.*'
        regex_cap += regex_caps + r' +(\w+|\d+).*\n((.*)\n)?(\n)+'
        print(regex_cap)
        text = re.sub(regex_cap,rf'#\1 \{groups+1}[\{groups+3}]\n/PAR/',text)
    return text



def treat_paragraphs(args,text):
    """If flagged or default separates paragraphs from simple sentences with the '/PAR/' delimiter"""
    if is_default() or '-par' in args.options:
        regex_par = r'([.!?;])\n(([^.!?;]|[\u00C0-\u017F]))'
        text = re.sub(regex_par,r'\1\n/PAR/ \2',text)
    return text




def treat_sentences_single_line(args,text):
    """If flagged or default unifies sentences into a single line"""
    if is_default() or '-js' in args.options:
        regex_sen = r'([^.!?])\n+([^.!?])'
        text = re.sub(regex_sen,r'\1 \2',text)
        """Fix Chapters"""
        regex_chap = r'(#CAPÍTULO +(\w+|\d+) \[.*\])'
        text = re.sub(regex_chap,r'\1\n',text)
    return text





def treat_sentence_per_line(args,text):
    """If flagged or default seperates every sentence in differente lines"""
    if is_default() or '-spl' in args.options:
        regex_sen = r'([^.!?][.?!])( |[^.\n])'
        text = re.sub(regex_sen,r'\1\2\n',text)
        
        """Fixes abreviatures, default recognizes english"""
        abrevs = load_translations(args,'/conf/abrev.txt')
        regex_abrv,groups = make_regex_lan(args,abrevs)
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


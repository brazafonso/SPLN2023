#!/usr/bin/env python3


from glob import glob
import argparse
import sys
import os
from gensim.models import Word2Vec
from gensim.utils import tokenize
from bs4 import BeautifulSoup


def parse_arguments()->argparse.Namespace:
    """Process arguments from stdin"""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description=f'''
    --------------------------------------------------------------------
                                **W2V model**
    --------------------------------------------------------------------'''
    )
    parser.add_argument('-d','--directory'       ,type=str                                                   ,help='folder with the corpus files')
    parser.add_argument('-e','--epochs'          ,type=int,default=50                                        ,help='number of epochs to train the model')
    parser.add_argument('-dim','--dimension'     ,type=int,default=300                                       ,help='dimension of the word vectors to create')
    parser.add_argument('-s','--save'            ,type=str,default=None                                      ,help='file to save the model')
    parser.add_argument('-lm','--load_model'     ,type=str,default=None                                      ,help='file from where to load model')
    parser.add_argument('-t','--train'                    ,default=False,action='store_true'                 ,help='option to chose whether to continue training model')
    parser.add_argument('-q','--queries'         ,type=str,default=None                                      ,help='file with queries to test')
    
    return parser.parse_args()


def treat_file_txt(filename):
    '''Treat a txt file using tokenizer'''
    file = open(filename,'r',encoding='utf-8')
    text = file.read()
    file.close()
    corpus = []
    for line in text.splitlines():
        corpus.append(list(tokenize(line,lowercase=True)))
    return corpus

def treat_file_html(filename):
    '''Treat a html file using tokenizer, grabing only text within text tags'''
    file = open(filename,'r',encoding='utf-8')
    html = file.read()
    file.close()
    soup = BeautifulSoup(html,features='lxml')
    corpus = []
    for elem in soup.find_all('text'):
        text = elem.get_text()
        for line in text.splitlines():
            corpus.append(list(tokenize(line,lowercase=True)))
    return corpus

def save_model(model,out):
    '''Saves the model on a given file'''
    print('Saving model')
    model.save(out)
    print('Model saved')

def load_model(file):
    '''Load model from file'''
    print('Loading model')
    model = Word2Vec.load(file)
    print('Model loaded')
    return model

def train_model(model,corpus,epochs=50):
    '''Train a model'''
    print('Training model')
    model.train(corpus, total_examples=len(corpus),epochs=epochs)
    print('Training finished')

def create_model(corpus,epochs=50,vector_size=300):
    '''Cria e devolve o modelo'''
    print('Creating model')
    model = Word2Vec(sentences=corpus,epochs=epochs,vector_size=vector_size)
    print('Model ready')
    return model


def get_queries(a):
    '''Read queries from file'''
    analogies = []
    similarities = []
    file = open(a, 'r',encoding='utf-8')
    text = file.read()
    file.close()
    for analogy in text.splitlines():
        words = analogy.split(' ')
        if len(words) == 3:
            words = [(w.lower()).strip() for w in words]
            analogies.append(words)
        elif len(words) == 1:
            words = [(w.lower()).strip() for w in words]
            similarities.append(words)
        else:
            words = analogy.split(' ')
            if len(words) == 2:
                similar = words[1].split('|')
                if len(similar) == 2:
                    words.pop(1)
                    words += similar
                    words = [(w.lower()).strip() for w in words]
                    similarities.append(words)
        
    return analogies,similarities
    

def treat_analogy(model,analogy):
    '''Checks and prints an analogy'''
    most_similar = model.wv.most_similar(positive=[analogy[0],analogy[2]],negative=[analogy[1]])
    print(f'{analogy[0]}  + {analogy[1]} = {analogy[2]} + x')
    print('x = ',most_similar)



def treat_similarity(model,similarity):
    '''Checks and prints a similarity'''
    if len(similarity) == 3:
        s1 = model.wv.similarity(similarity[0],similarity[1])
        s2 = model.wv.similarity(similarity[0],similarity[2])
        print(f'{similarity[0]}  = {similarity[1]} | {similarity[2]} -> ' + (f'{similarity[1]} ({s1})' if s1 > s2 else f'{similarity[2]} ({s2})'))
    elif len(similarity) == 1:
        print(f'Most similar to {similarity[0]} : ',model.wv.most_similar(similarity[0]))




# Main
if __name__ == '__main__':
    args = parse_arguments()
    dir = args.directory
    files_html = glob(f'{dir}/**/*.html',recursive=True)
    files_txt = glob(f'{dir}/**/*.txt',recursive=True)

    if args.directory:
        if args.load_model:
            model = load_model(args.load_model)
            if args.train:
                corpus = []
                for file in files_txt:
                    print('Geting text from file: ',file)
                    corpus += treat_file_txt(file)
                for file in files_html:
                    print('Geting text from file: ',file)
                    corpus += treat_file_html(file)
                print('Number of sentences on corpus: ',len(corpus))
                train_model(model,corpus,epochs=args.epochs)

        else:
            corpus = []
            for file in files_txt:
                print('Geting text from file: ',file)
                corpus += treat_file_txt(file)
            for file in files_html:
                print('Geting text from file: ',file)
                corpus += treat_file_html(file)
            print('Number of sentences on corpus: ',len(corpus))
            model = create_model(corpus,epochs=args.epochs,vector_size=args.dimension)
            
    if model and args.save:
        save_model(model,args.save)

    if model and args.queries:
        analogies,similarities = get_queries(args.queries)
        for analogy in analogies:
            try:
                treat_analogy(model,analogy)
                print('----------------------------\n----------------------------')
            except Exception as e:
                print(e)
                print('----------------------------\n----------------------------')
        for similarity in similarities:
            try:
                treat_similarity(model,similarity)
                print('----------------------------\n----------------------------')
            except Exception as e:
                print(e)
                print('----------------------------\n----------------------------')
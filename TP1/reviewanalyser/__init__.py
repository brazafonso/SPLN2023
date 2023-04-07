#! /usr/bin/env python3
"""Test of concept, dl model to categorize a review, trained from datasets creted by goodreadsscraper
"""

__version__ = '0.1'

import os
import sys
import re
import pandas as pd
import pickle
import tensorflow as tf
from tensorflow import keras
from keras import models, layers,optimizers
from keras.preprocessing import sequence
from keras.layers import Flatten,LSTM, Dense, Embedding
#from sklearn.utils import class_weight
#from sklearn.preprocessing import LabelEncoder


path = os.path.dirname(os.path.realpath(__file__))
model_path = 'model/review_analyser.h5'
text_vec_path = 'model/tv_layer.pkl'


def treat_text(text:str)->str:
    """Treat text, turning it to lower and removing all non alphabetical(english only) or numerical characters"""
    return str.lower(re.sub(r'([^a-zA-Z0-9]+)',' ',text))



def load_model():
    """Loads the neural network model"""
    return models.load_model(f'{path}/{model_path}',compile=True)


def predict_review(text:str)->str:
    """Receives a review and predicts if it represents a good or bad review"""
    # Loading vectorizer and model 
    vec = open(f'{path}/{text_vec_path}','rb')
    saved_text_vectorizer = pickle.load(vec)
    text_vectorizer = layers.TextVectorization.from_config(saved_text_vectorizer['config'])
    text_vectorizer.set_weights(saved_text_vectorizer['weights'])
    model = load_model()
    # Treating text
    text = [treat_text(text)]
    print(text)
    vec_text = text_vectorizer(text)

    # Making prediction
    prediction = model.predict(vec_text)
    return 'bad' if prediction > 0.5 else 'good'




def reviewanalyser():
    """Main function of the program"""
    print('Insert your review:')
    review = ''
    for line in sys.stdin.read():
        review += line
    if len(review) > 0:
        prediction = predict_review(review)
        print(prediction)
    else:
        print('Please insert some text')
    

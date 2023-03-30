#! /usr/bin/env python3
"""Module to scrap book information from goodreads
"""

__version__ = '0.0.1'

import os
import requests
import re
#from BeautifulSoup import BeautifulSoup
from bs4 import BeautifulSoup
from .utils import *
path = os.path.dirname(os.path.realpath(__file__))



def get_book_page(args)->requests.Response:
	"""Performs a get request to goodreads for a book with a give isbn or work id"""
	r= None
	if args.isbn:
		r = requests.get(f"https://www.goodreads.com/search?q={args.isbn}")
	elif args.id:
		r = requests.get(f"https://www.goodreads.com/book/show/{args.id}")
	return r


def get_book_reviews(id:str=None)->requests.Response:
	"""Performs a get request to goodreads for a book's reviews with a give isbn or wrok id"""
	r= None
	if id:
		r = requests.get(f"https://www.goodreads.com/book/show/{id}/reviews")
	return r

def bookscraper():
	"""Main function of the program"""
	print("Teste")
	args = utils.process_arguments(__version__)

	args.isbn = "9781846144769" #teste

	r = get_book_page(args)

	file = open(f'{path}/test/teste.html','w')
	file.write(r.content.decode(r.encoding))
	file.close()

	book_id = re.sub(r'[^0-9]+(\d+).*',r'\1',r.url)
	print(book_id)

	r = get_book_reviews(book_id)

	file = open(f'{path}/test/teste2.html','w')
	file.write(r.content.decode(r.encoding))
	file.close()
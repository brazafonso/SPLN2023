#! /usr/bin/env python3
"""Module to scrap book information from goodreads
"""

__version__ = '0.0.2'

import os
import requests
import re
import json
from bs4 import BeautifulSoup
import lxml.html as lh
from .utils import *
from .book import Book
path = os.path.dirname(os.path.realpath(__file__))


"""
TODO:
	- Permitir encontrar um livro atraves do nome (pesquisa no goodreads, encontrar primeiro url e assumir que esse e o livro)
	- Permitir pesquisar por autor
	- Apanhar reviews
		* Apanhar todas as reviews de uma pagina (manipulando o javascript inerente)
	- Criar dataset com as reviews conseguidas
	- Criar/permitir uso de modelo de aprendizagem profunda para analisar reviews

"""


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


def scrape_book_page(html_page)->Book:
	"""Scrapes a book's page for info such as title, score, number of reviews and others"""
	page = BeautifulSoup(html_page,features='lxml')

	book_details = page.find('script',{'type':'application/ld+json'}).get_text()
	book_details = json.loads(book_details)
	book_name = book_details['name']
	book_score = book_details['aggregateRating']['ratingValue']
	book_nratings = book_details['aggregateRating']['ratingCount']
	book_nreviews = book_details['aggregateRating']['reviewCount']
	book_npages = book_details['numberOfPages']
	book_author = book_details['author'][0]['name']
	book_language = book_details['inLanguage']
	book_isbn = book_details['isbn']
	book_description = page.find('div',{'class':'DetailsLayoutRightParagraph__widthConstrained'}).find('span',{'class':'Formatted'}).get_text()
	book_genres_divs = page.find_all('span',{'class':'BookPageMetadataSection__genreButton'})
	
	book_genres = []
	for genre in book_genres_divs:
		book_genres.append(genre.find('span',{'class':'Button__labelItem'}).get_text().strip())

	book_publishing_date = re.sub(r'.*(\b\w+\b\s*\d+\s*,\s*\d+)',r'\1',page.find('p',{'data-testid':'publicationInfo'}).get_text()).strip()

	return Book(book_name,book_isbn,book_author,book_description,book_publishing_date,book_score,book_nratings,book_nreviews,book_npages,book_language,book_genres)

def bookscraper():
	"""Main function of the program"""
	args = utils.process_arguments(__version__)

	if not args.isbn:
		args.isbn = "9781846144769" #teste

	# r = get_book_page(args)

	# soup = BeautifulSoup(r.content.decode(r.encoding),features='lxml')
	# prettyHTML1 = soup.prettify()

	# file = open(f'{path}/test/teste.html','w')
	# file.write(prettyHTML1)
	# file.close()
	
	# book_id = re.sub(r'[^0-9]+(\d+).*',r'\1',r.url)
	# print(book_id)

	# r = get_book_reviews(book_id)

	# soup = BeautifulSoup(r.content.decode(r.encoding),features='lxml')
	# prettyHTML2 = soup.prettify()

	# file = open(f'{path}/test/teste2.html','w')
	# file.write(prettyHTML2)
	# file.close()

	# book = scrape_book_page(prettyHTML1)

	file = open(f'{path}/test/teste.html','r')
	r = file.read()
	file.close()
	book = scrape_book_page(r)
	print(book)
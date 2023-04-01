#! /usr/bin/env python3
"""Module to scrap book information from goodreads
"""

__version__ = '0.0.2'

import os
import requests
import re
import json
from bs4 import BeautifulSoup
import jellyfish
import lxml.html as lh
from .utils import *
from .book import Book

path = os.path.dirname(os.path.realpath(__file__))
errors = []


"""
TODO:
	- Permitir encontrar um livro atraves do nome (pesquisa no goodreads, encontrar primeiro url e assumir que esse e o livro)
	- Permitir pesquisar por autor
	- Apanhar reviews
		* Apanhar todas as reviews de uma pagina (manipulando o javascript inerente)
	- Criar dataset com as reviews conseguidas
	- Criar/permitir uso de modelo de aprendizagem profunda para analisar reviews

"""


def add_error(msg):
	errors.append(f'Error: {msg}\n')


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


def get_author_page(args)->requests.Response:
	"""Performs a get request to goodreads for a author with a give name or id\n
	   If a name is given an indirect search is made by finding a work of the author and proceeding from there
	"""
	r= None
	# Check flag
	if args.author:
		a = args.author.lower().replace(' ','')
		match = re.match(r'\d+$',a)
		# Search by author id
		if match:
			search = requests.get(f"https://www.goodreads.com/author/show/{args.author}")
			soup = BeautifulSoup(search.content.decode(search.encoding),features='lxml')
			if re.search(r'Page not found',soup.find('title').get_text()):
				add_error(f'Could not find author id {args.author}')
			else:
				r = search

		# Search by author name
		else:
			search = requests.get(f"https://www.goodreads.com/search?q={args.author}")
			soup = BeautifulSoup(search.content.decode(search.encoding),features='lxml')
			authors = soup.find_all('a',{'class':'authorName'})
			url = None
			similarityDic = []
			# Search through every listed book for an author match
			for author in authors:
				name = author.find('span',{'itemprop':'name'}).get_text().lower().replace(' ','')
				auxurl = author['href']
				difference = jellyfish.levenshtein_distance(a,name)
				similarityDic.append((name,auxurl,difference))
				if difference == 0:
					break
			if len(similarityDic)>0:
				similarityDic = sorted(similarityDic,key=lambda x: x[2])
				r = requests.get(similarityDic[0][1])
			else:
				add_error(f'Could not find author name {args.author}')
	return r


def bookscraper():
	"""Main function of the program"""
	args = utils.process_arguments(__version__)

	if not args.isbn:
		args.isbn = "9781846144769" #teste

	r = get_author_page(args)
	if r:
		soup = BeautifulSoup(r.content.decode(r.encoding),features='lxml')
		prettyHTML3 = soup.prettify()

		file = open(f'{path}/test/teste3.html','w')
		file.write(prettyHTML3)
		file.close()

	# r = get_book_page(args)
	# if r
		# soup = BeautifulSoup(r.content.decode(r.encoding),features='lxml')
		# prettyHTML1 = soup.prettify()

		# file = open(f'{path}/test/teste.html','w')
		# file.write(prettyHTML1)
		# file.close()
	
	# book_id = re.sub(r'[^0-9]+(\d+).*',r'\1',r.url)
	# print(book_id)

	# r = get_book_reviews(book_id)

	# if r
		# soup = BeautifulSoup(r.content.decode(r.encoding),features='lxml')
		# prettyHTML2 = soup.prettify()

		# file = open(f'{path}/test/teste2.html','w')
		# file.write(prettyHTML2)
		# file.close()

	# book = scrape_book_page(prettyHTML1)

	# file = open(f'{path}/test/teste.html','r')
	# r = file.read()
	# file.close()
	# book = scrape_book_page(r)
	# utils.write_output(args,book.__str__())

	utils.write_errors(args,errors)
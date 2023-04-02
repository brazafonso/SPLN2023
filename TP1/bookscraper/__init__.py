#! /usr/bin/env python3
"""Module to scrap book information from goodreads
"""

__version__ = '0.0.2'

import os
from typing import Set
import requests
import re
import json
from bs4 import BeautifulSoup
import jellyfish
import lxml.html as lh
from .utils import *
from .book import Book
from .author import Author
path = os.path.dirname(os.path.realpath(__file__))
errors = []


"""
TODO:
	- Apanhar reviews
		* Apanhar todas as reviews de uma pagina (manipulando o javascript inerente)
	- Criar dataset com as reviews conseguidas
	- Criar/permitir uso de modelo de aprendizagem profunda para analisar reviews
	- Permitir uma opção em que é indicado um ficheiro estilo json para fazer um conjunto de pesquisas de uma só vez
"""


def add_error(msg):
	errors.append(f'Error: {msg}\n')


def search_book_option(args):
	return args.isbn or args.id or args.btitle

def get_book_page(args)->requests.Response:
	"""Performs a get request to goodreads for a book with a give isbn, work id or search name"""
	r= None
	# Search with book's isbn
	if args.isbn:
		r = requests.get(f"https://www.goodreads.com/search?q={args.isbn}")
	# Search with book's work id'
	elif args.id:
		r = requests.get(f"https://www.goodreads.com/book/show/{args.id}")
	# Search with search name (less precise)
	elif args.btitle:
		btitle = args.btitle.lower().replace(' ','')
		search = requests.get(f"https://www.goodreads.com/search?q={args.btitle}")
		soup = BeautifulSoup(search.content.decode(search.encoding),features='lxml')
		books = soup.find_all('a',{'class':'bookTitle'})
		authors = soup.find_all('a',{'class':'authorName'})
		similarityDic = []
		if args.author:
			a = args.author.lower().replace(' ','')
		# Search through every listed book for a book match
		for i,book in enumerate(books):
			bname = book.find('span',{'itemprop':'name'}).get_text().lower().replace(' ','')
			bname = re.sub(r'([^(]+)\s*(\(.+\))?',r'\1',bname)
			url = book['href']
			difference = jellyfish.levenshtein_distance(btitle,bname)
			# Use given author to increase book search precision
			if args.author:
				author = authors[i]
				aname = author.find('span',{'itemprop':'name'}).get_text().lower().replace(' ','')
				differenceA = jellyfish.levenshtein_distance(a,aname)
				# print(btitle,bname,utils.similitarity_percent(btitle,difference))
				# print(a,aname,utils.similitarity_percent(aname,differenceA))
				if utils.similitarity_percent(aname,differenceA) < 0.6:
					if utils.similitarity_percent(btitle,difference) < 0.6: 
						similarityDic.append((bname,url,difference))
					# Stops with perfect match
					if difference == 0:
						break
			# Default search
			else:
				if utils.similitarity_percent(btitle,difference) < 0.5: 
					similarityDic.append((bname,url,difference))
				# Stops with perfect match
				if difference == 0:
					break
		if len(similarityDic)>0:
			similarityDic = sorted(similarityDic,key=lambda x: x[2])
			r = requests.get(f'https://www.goodreads.com/{similarityDic[0][1]}')
		else:
			add_error(f'Could not find book name {args.btitle}')
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

	return Book(book_name,book_isbn,book_author,
	     book_description,book_publishing_date,book_score,
		 book_nratings,book_nreviews,book_npages,
		 book_language,book_genres)






def get_author_page(args)->requests.Response:
	"""Performs a get request to goodreads for a author with a give name or id\n
	   If a name is given an indirect search is made by finding a work of the author and proceeding from there
	"""
	r= None
	# Check flag
	if args.author and not search_book_option(args):
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
			similarityDic = []
			# Search through every listed book for an author match
			for author in authors:
				name = author.find('span',{'itemprop':'name'}).get_text().lower().replace(' ','')
				url = author['href']
				difference = jellyfish.levenshtein_distance(a,name)
				if utils.similitarity_percent(a,difference) < 0.5: 
					similarityDic.append((name,url,difference))
				if difference == 0:
					break

			if len(similarityDic)>0:
				similarityDic = sorted(similarityDic,key=lambda x: x[2])
				r = requests.get(similarityDic[0][1])
			else:
				add_error(f'Could not find author name {args.author}')
	return r


def scrape_author_page(html_page:str)->Author:
	"""Scrapes an author's page for info such as name, birthday, average score, number of reviews and others"""
	page = BeautifulSoup(html_page,features='lxml')

	author_name = page.find('h1',{'class':'authorName'}).get_text().strip()
	author_birthdate = page.find('div',{'class':'dataItem','itemprop':"birthDate"}).get_text().strip()
	author_birthplace = page.find('div',{'class':'dataTitle'}).next_sibling.get_text().strip()
	author_deathdate = page.find('div',{'class':'dataItem','itemprop':"deathDate"}).get_text().strip()
	author_website = page.find('a',{'itemprop':"url"}).get_text().strip()
	author_description = page.find('div',{'class':'aboutAuthorInfo'}).find('span',{'style':'display:none'}).get_text().strip()
	author_averageRating = page.find('span',{'class':'average','itemprop':'ratingValue'}).get_text().strip()
	author_nratings = page.find('span',{'class':'value-title','itemprop':'ratingCount'}).get_text().strip()
	author_nreviews = page.find('span',{'class':'value-title','itemprop':'reviewCount'}).get_text().strip()
	author_nUniqueWorks = None

	# Catch author's genres and influences
	dataItems = page.find_all('div',{'class':'dataItem'})
	author_genres = []
	author_influences = []
	works_url = None
	for item in dataItems:
		items = item.find_all('a')
		for item in items:
			if item['href']:
				if re.search('genres',item['href']):
					author_genres.append(item.get_text().strip())
				elif re.search('/author/show/',item['href']):
					author_influences.append(item.get_text().strip())

	author_stats = page.find('div',{'class':'hreview-aggregate'})
	items = author_stats.find_all('a')
	for item in items:
		if re.search('/author/list/',item['href']):
			print(item)
			author_nUniqueWorks = item.get_text().strip()
			works_url = item['href']

	author_works = get_author_works(works_url)

	return Author(author_name,author_birthdate,author_birthplace,
	       author_deathdate,author_website,author_genres,
		   author_influences,author_description,author_averageRating,
		   author_nratings,author_nreviews,author_nUniqueWorks,author_works)

def get_author_works(works_url:str)->Set[str]:
	"""Get the list of unique works of an author"""
	# FIXME : needs to search through all the pages of works (only searching the first currently)
	works = set()
	print('found0',works_url)
	if works_url:
		r = requests.get(f'https://www.goodreads.com/{works_url}')
		print('found1')
		if r.status_code == 200:
			print('found2')
			page = BeautifulSoup(r.content.decode(r.encoding),features='lxml')
			books = page.find_all('a',{'class':'bookTitle'})
			for book in books:
				print('found3')
				works.add(book.find('span',{'itemprop':'name'}).get_text().strip())
	
	if works:
		return works
	else:
		return None



def work_in_progress(args):
	"""Testing new implementations"""

	if not args.isbn:
		args.isbn = "9781846144769" #teste

	# r = get_author_page(args)
	# if r:
	# 	soup = BeautifulSoup(r.content.decode(r.encoding),features='lxml')
	# 	prettyHTML3 = soup.prettify()

	# 	file = open(f'{path}/test/teste3.html','w')
	# 	file.write(prettyHTML3)
	# 	file.close()

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

	file = open(f'{path}/test/teste3.html','r')
	r = file.read()
	file.close()
	author = scrape_author_page(r)
	utils.write_output(args,author.__str__(True))

def bookscraper():
	"""Main function of the program"""
	# FIXME: Decidir resultados do programa (html ou resultados de scrape, no ultimo caso flags para informacao extra tipo descricao)
	args = utils.process_arguments(__version__)
	work_in_progress(args)

	# results = []

	# # Get the page of a book
	# r = get_book_page(args)
	# if r:
	# 	book = scrape_book_page(utils.prettify_html(r))
	# 	results.append(book.__str__())
	
	# # Get the page of an author
	# r = get_author_page(args)
	# if r:
	# 	author = scrape_author_page(utils.prettify_html(r))
	# 	results.append(author.__str__())

	# utils.write_output(args,results)
	# utils.write_errors(args,errors)
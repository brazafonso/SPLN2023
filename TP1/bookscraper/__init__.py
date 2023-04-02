#! /usr/bin/env python3
"""Module to scrap book information from goodreads
"""

__version__ = '0.0.3'

import os
from typing import List, Set
import requests
import re
import json
from bs4 import BeautifulSoup
import jellyfish
import lxml.html as lh
from .utils import *
from .book import Book
from .author import Author
from .review import Review
path = os.path.dirname(os.path.realpath(__file__))
errors = []


"""
TODO:
	- Apanhar reviews
		* Apanhar todas as reviews de uma pagina (manipulando o javascript inerente)
	- Criar dataset com as reviews conseguidas
	- Criar/permitir uso de modelo de aprendizagem profunda para analisar reviews
	- Permitir uma opção em que é indicado um ficheiro estilo json para fazer um conjunto de pesquisas de uma só vez
	- Acrescentar verificacao de procedimento default ou com flag
"""


def add_error(msg:str):
	"""Adds an error message to the error stack"""
	errors.append(f'Error: {msg}\n')


def search_book_option(args):
	"""Verify if a book search option was given"""
	return args.isbn or args.id or args.btitle


def search_btitle(args,btitle,page):
	"""Searches for a book page using its name and author if given"""
	r = None
	soup = BeautifulSoup(page.content.decode(page.encoding),features='lxml')
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
	# Choose the best match
	if len(similarityDic)>0:
		similarityDic = sorted(similarityDic,key=lambda x: x[2])
		r = requests.get(f'https://www.goodreads.com{similarityDic[0][1]}')
	else:
		add_error(f'Could not find book name {args.btitle}')
	return r

def is_book_page(r:requests.Response)->bool:
	"""Checks if response is relative to a book page"""
	return re.search('www.goodreads.com/book/show/',r.url)

def get_book_page(args)->requests.Response:
	"""Performs a get request to goodreads for a book with a give isbn, work id or search name"""
	r= None
	# Search with book's isbn
	if args.isbn:
		utils.log(args,f"Searching for book with isbn - {args.isbn}...")
		r = requests.get(f"https://www.goodreads.com/search?q={args.isbn}")

	# Search with book's work id'
	elif args.id:
		utils.log(args,f"Searching for book with id - {args.id}...")
		r = requests.get(f"https://www.goodreads.com/book/show/{args.id}")

	# Search with search name (less precise)
	elif args.btitle:
		utils.log(args,f"Searching for book with name - {args.btitle}...")
		btitle = args.btitle.lower().replace(' ','')
		search = requests.get(f"https://www.goodreads.com/search?q={args.btitle}")
		if search.status_code == 200:
			r = search_btitle(args,btitle,search)

	utils.log(args,f"Search finished")
	if r and r.status_code==200 and is_book_page(r):
		return r
	else:
		add_error(f'Could not find book')
		return None




def get_book_id(r:requests.Response)->str:
	"""Return a book's id using a responses url"""
	id = re.search(r'www.goodreads.com/book/show/(\d+)',r.url).group(1)
	return id 



def scrape_book_page(args,html_page:str)->Book:
	"""Scrapes a book's page for info such as title, score, number of reviews and others"""
	utils.log(args,f"Scraping book info...")
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

	utils.log(args,f"Scrape finished")
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
			utils.log(args,f"Searching for author with id - {args.author}...")
			search = requests.get(f"https://www.goodreads.com/author/show/{args.author}")
			soup = BeautifulSoup(search.content.decode(search.encoding),features='lxml')
			if re.search(r'Page not found',soup.find('title').get_text()):
				add_error(f'Could not find author id {args.author}')
			else:
				r = search

		# Search by author name
		else:
			utils.log(args,f"Searching for author with name - {args.author}...")
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
			
			# Choose the best match
			if len(similarityDic)>0:
				similarityDic = sorted(similarityDic,key=lambda x: x[2])
				r = requests.get(similarityDic[0][1])
			else:
				add_error(f'Could not find author name {args.author}')
		utils.log(args,f"Search finished")
	return r


def get_page_works(page:BeautifulSoup)->List[str]:
	"""Get all the books from a page that lists them"""
	works = []
	books = page.find_all('a',{'class':'bookTitle'})
	for book in books:
		works.append(book.find('span',{'itemprop':'name'}).get_text().strip())
	return works




def get_author_works(args,works_url:str,max:int=None)->List[str]:
	"""Get the list of unique works of an author\n
	Max represents the maximum number of works to obtain (by default gathers all going from page to page)"""
	works = []
	if works_url:
		utils.log(args,f"Scraping author's books")
		page_number = 1
		count = 0
		r = requests.get(f'https://www.goodreads.com/{works_url}?page=1&per_page=30')
		if r.status_code == 200:
			page = BeautifulSoup(r.content.decode(r.encoding),features='lxml')
			max_pages_element = page.find('div',{'style':'float: right'}).find_all('a')
			if max_pages_element:
				max_pages = int(max_pages_element[-2].get_text().strip())
			else:
				max_pages = 1
			page_works = get_page_works(page)
			if max and count + len(page_works) > max:
				works += page_works[:max-count]
			else:
				works += page_works
				count += len(page_works)
				# Search through all the pages of books, until limit reached (max to collect or all collected)
				for i in range(2,max_pages+1):
					r = requests.get(f'https://www.goodreads.com/{works_url}?page={i}&per_page=30')
					if r.status_code == 200:
						page = BeautifulSoup(r.content.decode(r.encoding),features='lxml')
						page_works = get_page_works(page)
						if max and count + len(page_works) > max:
							works += page_works[:max-count]
							break
						else:
							works += page_works
							count += len(page_works)
		utils.log(args,f"Scraping finished")
	if works:
		return works
	else:
		return None


def scrape_author_page(args,html_page:str)->Author:
	"""Scrapes an author's page for info such as name, birthday, average score, number of reviews and others"""
	# FIXME: if elses para tudo pq pode n ter nada - ex. Sir kazzio
	utils.log(args,f"Scraping author's page for info")
	page = BeautifulSoup(html_page,features='lxml')

	author_name = page.find('h1',{'class':'authorName'}).get_text().strip()
	author_birthdate = page.find('div',{'class':'dataItem','itemprop':"birthDate"}).get_text().strip()
	author_birthplace = page.find('div',{'class':'dataTitle'}).next_sibling.get_text().strip()
	author_deathdate = None
	# Death date
	element_deathdate = page.find('div',{'class':'dataItem','itemprop':"deathDate"})
	if element_deathdate:
		author_deathdate = element_deathdate.get_text().strip()
	author_website = page.find('a',{'itemprop':"url"}).get_text().strip()
	# Description
	element_description = page.find('div',{'class':'aboutAuthorInfo'}).find('span').find_next_sibling('span')
	author_description = element_description.get_text().strip()

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
			author_nUniqueWorks = item.get_text().strip()
			works_url = item['href']

	max = args.maxworks 
	author_works = get_author_works(args,works_url,max)
	utils.log(args,f"Scraping finished")
	return Author(author_name,author_birthdate,author_birthplace,
	       author_deathdate,author_website,author_genres,
		   author_influences,author_description,author_averageRating,
		   author_nratings,author_nreviews,author_nUniqueWorks,author_works)


def get_book_reviews_page(args):
	r = None
	utils.log(args,f"Searching for book reviews's page")
	if args.id:
		r = requests.get(f'https://www.goodreads.com/book/show/{args.id}/reviews')
	elif args.isbn:
		r = requests.get(f"https://www.goodreads.com/search?q={args.isbn}")
		if r.status_code == 200 and is_book_page(r):
			id = get_book_id(r)
			if id:
				r = requests.get(f'https://www.goodreads.com/book/show/{id}/reviews')
	utils.log(args,f"Search finished")
	return r


def scrape_reviews_page(args,html_page:str)->List[Review]:
	reviews_list = []
	utils.log(args,f"Scraping reviews's page for info")
	page = BeautifulSoup(html_page,features='lxml')
	div_reviews_list = page.find('div',{'class':'ReviewsList'})
	reviews = div_reviews_list.find_all('article',{'class':'ReviewCard'})
	# Get info from all the reviews
	for review in reviews:
		reviewer_info = review.find('div',{'class':'ReviewerProfile__name'})
		reviewer_main = reviewer_info.find('a')
		reviewer_name = reviewer_main.get_text().strip()
		reviewer_id = re.search(r'/user/show/(\d+)',reviewer_main['href']).group(1)
		review_score = review.find('div',{'class':'ShelfStatus'}).find('span')['aria-label']
		review_score = re.search(r'Rating (\d+) out of \d+',review_score).group(1)
		review_description_card = review.find('section',{'class','ReviewText__content'})
		review_description = review_description_card.find('span').get_text().strip()
		rev = Review(reviewer_id,reviewer_name,review_score,review_description)
		#print(reviewer_name,reviewer_id,review_score,review_description)
		reviews_list.append(rev)
	utils.log(args,f"Scraping finished")
	return reviews_list



def work_in_progress(args):
	"""Testing new implementations"""

	# if not args.isbn:
	# 	args.isbn = "9781846144769" #teste

	# if not args.id:
	# 	args.id = "46262177"

	r = get_book_reviews_page(args)
	if r:
		soup = BeautifulSoup(r.content.decode(r.encoding),features='lxml')
		prettyHTML3 = soup.prettify()

		file = open(f'{path}/test/teste5.html','w')
		file.write(prettyHTML3)
		file.close()
		reviews = scrape_reviews_page(args,r.content.decode(r.encoding))
		for review in reviews:
			print(review.__str__(True))
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

	# book = scrape_book_page(args,prettyHTML1)

	# file = open(f'{path}/test/teste3.html','r')
	# r = file.read()
	# file.close()
	# author = scrape_author_page(args,r)
	# utils.write_output(args,author.__str__(True))

def bookscraper():
	"""Main function of the program"""
	# FIXME: Decidir resultados do programa (html ou resultados de scrape, no ultimo caso flags para informacao extra tipo descricao)
	args = utils.process_arguments(__version__)
	work_in_progress(args)

	#results = []

	# Get the page of a book
	# r = get_book_page(args)
	# if r:
	# 	book = scrape_book_page(args,utils.prettify_html(r))
	# 	results.append(book.__str__(True))
	
	# # Get the page of an author
	# r = get_author_page(args)
	# if r:
	# 	author = scrape_author_page(args,utils.prettify_html(r))
	# 	results.append(author.__str__(True))


	# utils.write_output(args,results)
	# utils.write_errors(args,errors)
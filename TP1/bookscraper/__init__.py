#! /usr/bin/env python3
"""Module to scrap book information from goodreads
"""

__version__ = '0.0.5'

import os
import time
import re
import json
import jellyfish
import lxml.html as lh
import pandas as pd
import threading as th
from typing import List, Union
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .utils import *
from .book import Book
from .author import Author
from .review import Review

path = os.path.dirname(os.path.realpath(__file__))


"""
TODO:
	- Criar/permitir uso de modelo de aprendizagem profunda para analisar reviews
"""




def create_driver(args)->webdriver:
	"""Create driver to make requests from pages\nNeeded because of the great use of js"""
	driver = None
	log(args,f'Creating driver')
	try:
		log(args,f'Chrome')
		opf = webdriver.ChromeOptions()
		opf.add_argument('--window-size=1920,1080')
		opf.add_argument('--headless')
		driver = webdriver.Chrome(options=opf)
		
	except:
		error(args,f'Could not create Chrome driver')
		try:
			log(args,f'Firefox')
			opf = webdriver.FirefoxOptions()
			opf.add_argument('--window-size=1920,1080')
			opf.add_argument('--headless')
			driver = webdriver.Firefox(options=opf)
		except:
			error(args,f'Could not create Firefox driver')
			driver = None
	if driver:
		log(args,f'Driver created')
	else:
		log(args,f'Could not create driver. Please read documentation to install proper dependencies.')
	return driver

def driver_wait_element_to_be_clickable(driver:webdriver,xpath:str,timeout:int=1):
	'''Waits until timeout for element in XPATH to become clickable'''
	WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH,xpath)))

def driver_wait_element(driver,xpath:str,timeout:int=1,exist:bool=True):
	'''Waits until timeout for element in XPATH to either exist or not'''
	if exist:
		WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
	else:
		WebDriverWait(driver, timeout).until(EC.none_of(EC.presence_of_element_located((By.XPATH, xpath))))



def create_dataset(header,list)->pd.DataFrame:
	"""Creates a dataset from a list of already processed into strings of dataset lines"""
	return pd.DataFrame(list,columns=header)


def search_book_option(args):
	"""Verify if a book search option was given"""
	return args.isbn or args.id or args.btitle


def search_btitle(args,driver:webdriver,btitle:str,page:str)->str:
	"""Searches for a book page using its name and author if given"""
	r = None
	soup = BeautifulSoup(page,features='lxml')
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
			if similitarity_percent(aname,differenceA) < 0.6:
				if similitarity_percent(btitle,difference) < 0.6:
					similarityDic.append((bname,url,difference))
				# Stops with perfect match
				if difference == 0:
					break
		# Default search
		else:
			if similitarity_percent(btitle,difference) < 0.5:
				similarityDic.append((bname,url,difference))
			# Stops with perfect match
			if difference == 0:
				break
	# Choose the best match
	if len(similarityDic)>0:
		similarityDic = sorted(similarityDic,key=lambda x: x[2])
		driver.get(f'https://www.goodreads.com{similarityDic[0][1]}')
		r = driver.page_source
	else:
		error(args,f'Could not find book name {args.btitle}')
	return r

def is_book_page(url:requests.Response)->bool:
	"""Checks if response is relative to a book page"""
	return re.search('www.goodreads.com/book/show/',url)

def get_book_page(args,driver:webdriver)->str:
	"""Performs a get request to goodreads for a book with a give isbn, work id or search name"""
	r= None
	# Search with book's isbn
	if args.isbn:
		log(args,f"Searching for book with isbn - {args.isbn}...")
		driver.get(f"https://www.goodreads.com/search?q={args.isbn}")
		args.id = get_book_id(driver.current_url)
		driver_wait_element(driver,'//script[@type="application/ld+json"]',10000)
		r = driver.page_source

	# Search with book's work id'
	elif args.id:
		log(args,f"Searching for book with id - {args.id}...")
		driver.get(f"https://www.goodreads.com/book/show/{args.id}")
		driver_wait_element(driver,'//script[@type="application/ld+json"]',10000)
		r = driver.page_source

	# Search with search name (less precise)
	elif args.btitle:
		log(args,f"Searching for book with name - {args.btitle}...")
		btitle = args.btitle.lower().replace(' ','')
		driver.get(f"https://www.goodreads.com/search?q={args.btitle}")
		page = driver.page_source
		r = search_btitle(args,driver,btitle,page)
		if r:
			args.id = get_book_id(driver.current_url)
			driver_wait_element(driver,'//script[@type="application/ld+json"]',10000)


	log(args,f"Search finished")
	if r  and is_book_page(driver.current_url):
		return r
	else:
		error(args,f'Could not find book')
		return None




def get_book_id(url:str)->str:
	"""Return a book's id using a url"""
	id = re.search(r'www.goodreads.com/book/show/(\d+)',url).group(1)
	return id



def scrape_book_page(args,html_page:str)->Book:
	"""Scrapes a book's page for info such as title, score, number of reviews and others"""
	log(args,f"Scraping book info...")
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

	log(args,f"Scrape finished")
	return Book(book_name,book_isbn,book_author,
	     book_description,book_publishing_date,book_score,
		 book_nratings,book_nreviews,book_npages,
		 book_language,book_genres)






def get_author_page(args,driver:webdriver)->str:
	"""Performs a get request to goodreads for a author with a give name or id\n
	   If a name is given an indirect search is made by finding a work of the author and proceeding from there
	"""
	r= None
	# Check flag
	#if args.author and not search_book_option(args):
	if args.author:
		a = args.author.lower().replace(' ','')
		match = re.match(r'\d+$',a)
		# Search by author id
		if match:
			log(args,f"Searching for author with id - {args.author}...")
			driver.get(f"https://www.goodreads.com/author/show/{args.author}")
			search = driver.page_source
			soup = BeautifulSoup(search,features='lxml')
			if re.search(r'Page not found',soup.find('title').get_text()):
				error(args,f'Could not find author id {args.author}')
			else:
				r = search

		# Search by author name
		else:
			log(args,f"Searching for author with name - {args.author}...")
			driver.get(f"https://www.goodreads.com/search?q={args.author}")
			search = driver.page_source
			soup = BeautifulSoup(search,features='lxml')
			authors = soup.find_all('a',{'class':'authorName'})
			similarityDic = []
			# Search through every listed book for an author match
			for author in authors:
				name = author.find('span',{'itemprop':'name'}).get_text().lower().replace(' ','')
				url = author['href']
				difference = jellyfish.levenshtein_distance(a,name)
				if similitarity_percent(a,difference) < 0.5:
					similarityDic.append((name,url,difference))
				if difference == 0:
					break

			# Choose the best match
			if len(similarityDic)>0:
				similarityDic = sorted(similarityDic,key=lambda x: x[2])
				driver.get(similarityDic[0][1])
				r = driver.page_source
			else:
				error(args,f'Could not find author name {args.author}')
		log(args,f"Search finished")
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
		log(args,f"Scraping author's books")
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
		log(args,f"Scraping finished")
	if works:
		return works
	else:
		return None


def scrape_author_page(args,html_page:str)->Author:
	"""Scrapes an author's page for info such as name, birthday, average score, number of reviews and others"""
	# FIXME: if elses para tudo pq pode n ter nada - ex. Sir kazzio
	log(args,f"Scraping author's page for info")
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
	element_description = page.find('div',{'class':'aboutAuthorInfo'}).find('span')
	if(element_description.find_next_sibling('span')):
		author_description = element_description.get_text().strip()
	else: author_description = element_description.get_text().strip()

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
	log(args,f"Scraping finished")
	return Author(author_name,author_birthdate,author_birthplace,
	       author_deathdate,author_website,author_genres,
		   author_influences,author_description,author_averageRating,
		   author_nratings,author_nreviews,author_nUniqueWorks,author_works)


def loaded_reviews_page(html:str)->bool:
	"""Checks if the reviews page is loaded"""
	#FIXME
	return True

def get_book_reviews_page(args,driver)->str:
	"""Return the book reviews page (if book flags active)"""
	r = None

	if search_book_option(args):
		log(args,f"Searching for book reviews's page")
		id = None
		if args.id:
			id = args.id

		elif args.isbn or args.btitle:
			get_book_page(args,driver)
			url = driver.current_url
			id = get_book_id(url)
		
		if id:		
			log(args,f"Trying to get reviews page")
			driver.get(f'https://www.goodreads.com/book/show/{id}/reviews')
			# Wait for reviews to appear
			driver_wait_element(driver,"//div[@class='ReviewsList']",100000)
			# Check if something is still loading
			driver_wait_element(driver,"//div[@class='LoadingCard']",100000,False)
			if not loaded_reviews_page(driver.page_source):
				error(args,'Could not get proper reviews page')
			else:
				r = driver.page_source

		log(args,f"Search finished")
	return r


def scrape_reviews_page(args,html_page:str,lower_limit:int=None,higher_limit:int=None)->List[Review]:
	"""Scrape reviews from page, if range is given only grab reviews in that range"""
	reviews_list = []
	log(args,f"Scraping reviews's page for info")

	page = BeautifulSoup(html_page,features='lxml')
	div_reviews_list = page.find('div',{'class':'ReviewsList'})
	reviews = div_reviews_list.find_all('article',{'class':'ReviewCard'})
	# Change range of reviews to gather
	reviews = list_range(reviews,lower_limit,higher_limit)

	# Get info from all the reviews
	for review in reviews:
		reviewer_info = review.find('div',{'class':'ReviewerProfile__name'})
		reviewer_main = reviewer_info.find('a')
		reviewer_name = reviewer_main.get_text().strip()
		reviewer_id = re.search(r'/user/show/(\d+)',reviewer_main['href']).group(1)
		review_score = None
		review_score_elem = review.find('div',{'class':'ShelfStatus'}).find('span')
		if review_score_elem:
			review_score = re.search(r'Rating (\d+) out of \d+',review_score_elem['aria-label']).group(1)
		review_description_card = review.find('section',{'class','ReviewText__content'})
		review_description = review_description_card.find('span').get_text().strip()
		rev = Review(reviewer_id,reviewer_name,review_score,review_description)
		reviews_list.append(rev)
	log(args,f"Scraping finished")
	return reviews_list



def get_review_page_stats(page:str)->List[int]:
	"""Recovers simple stats about review page, such as number of reviews and range shown"""
	soup = BeautifulSoup(page,features='lxml')
	number_reviews_elem = soup.find('div',{'class':'ReviewsList__listContext'}).find('span')
	number_reviews_info = re.search(r'(\d+)\s*-\s*(\d+)[^\d]*(\d+((,|\.)\d+)?)',number_reviews_elem.get_text().strip())
	n_reviews = int(re.sub(r'(.*),|\.(.*)',r'\1\2',number_reviews_info.group(3)))
	lower_review = int(number_reviews_info.group(1))
	higher_review = int(number_reviews_info.group(2))
	return [n_reviews,lower_review,higher_review]


def review_page_show_more(args,driver):
	"""Activates show more reviews javascript on review page"""
	log(args,f'Showing more reviews...')
	elem = driver.find_element(By.XPATH,"//button[@class='Button Button--secondary Button--small']")
	if elem:
		driver.execute_script("arguments[0].scrollIntoView();", elem)
		driver_wait_element_to_be_clickable(driver,"//button[@class='Button Button--secondary Button--small']",1000000)
		time.sleep(0.5)
		elem.click()
		driver_wait_element(driver,"//button[@class='Button Button--secondary Button--small Button--disabled']",1000000,False)
		log(args,f'Got more reviews.')
	else:
		log(args,f'No more reviews.')


def scrape_reviews(args,driver)->List[Review]:
	"""Gets reviews from book page"""
	reviews = []
	if args.reviews or args.reviews_full:
		log(args,f'Scraping book reviews...')
		page = get_book_reviews_page(args,driver)
		if page:
			range = [None,None]
			if args.reviews_range:
				range = [args.reviews_range[0],args.reviews_range[1]]

			# Only get the minimum number of reviews
			if args.reviews:
				log(args,f'Simple review scraping')
				reviews = scrape_reviews_page(args,page,range[0],range[1])

			# Get more reviews (slower as it uses a driver to interact with buttons that make js requests)
			# FIXME: Bug after 1000 reviews reviews (~30 button activations)
			elif args.reviews_full:
				log(args,f'Full review scraping')

				reviews += scrape_reviews_page(args,page,range[0],range[1])
				review_page_show_more(args,driver)
				count = len(reviews)
				n_reviews,lower_review,higher_review = get_review_page_stats(page)
				# Get reviews in range
				if args.reviews_range:
					max_reviews = range[1]-range[0]
					range[0] = range[0] + len(reviews)
					while(count < n_reviews and count < max_reviews):
						log(args,f'Current reviews : {count} of {n_reviews}')
						page = driver.page_source
						thread = th.Thread(target=review_page_show_more,args=[args,driver])
						thread.start()
						n_reviews,lower_review,higher_review = get_review_page_stats(page)
						reviews += scrape_reviews_page(args,page,range[0],range[1])
						range[0] = range[0] + len(reviews)
						count = len(reviews)
						thread.join()
				# Get all reviews
				else:
					range[0] = len(reviews)		
					while(count < n_reviews):
						log(args,f'Current reviews : {count} of {n_reviews}')
						page = driver.page_source
						thread = th.Thread(target=review_page_show_more,args=[args,driver])
						thread.start()
						n_reviews,lower_review,higher_review = get_review_page_stats(page)
						reviews += scrape_reviews_page(args,page,range[0],range[1])
						range[0] = len(reviews)
						count = len(reviews)
						thread.join()
				
		log(args,f'Finished Scraping')
	return reviews


def work_in_progress(args):
	"""Testing new implementations"""

	# if not args.isbn:
	# 	args.isbn = "9781846144769" #teste

	# if not args.id:
	# 	args.id = "46262177"

	# soup = BeautifulSoup(r.content.decode(r.encoding),features='lxml')
	# prettyHTML3 = soup.prettify()

	# file = open(f'{path}/test/teste5.html','w')
	# file.write(prettyHTML3)
	# file.close()
	driver = create_driver(args)
	reviews = scrape_reviews(args,driver)
	if reviews:
		df = create_dataset(reviews[0].header(),[r.dataset_line() for r in reviews])
		print(df.head(),df.info())
		file = open(f'{path}/test/teste.txt','w')
		file.write(df.to_string())
	driver.quit()
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
	# write_output(args,author.__str__(True))

def bookscraper():
	"""Main function of the program"""
	args = parse_arguments(__version__)
	#work_in_progress(args)

	driver = create_driver(args)
	if driver:
		results = []
		results_reviews = []

		books,authors = process_arguments(args)

		for book in books:
			# Get the page of a book
			res = get_book_page(book,driver)
			if res:
				b = scrape_book_page(book,prettify_html(res))
				results.append({'out':book.output,'result':b.__str__(True if args.verbose else False)})
			
			if(book.reviews or book.reviews_full):
				reviews = scrape_reviews(book,driver)
				if reviews:
					df = create_dataset(reviews[0].header(),[r.dataset_line() for r in reviews])
					results_reviews.append({'out' : book.review_output, 'result':df.to_json(indent=4)})

			

		for author in authors:
			# Get the page of an author
			res = get_author_page(author,driver)
			if res:
				a = scrape_author_page(author,prettify_html(res))
				results.append({'out':author.output,'result':a.__str__(True if args.verbose else False)})

		driver.quit()
		for result in results:
			write_output(result['out'],result['result'])
		
		for result in results_reviews:
			write_output(result['out'],result['result'])



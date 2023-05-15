#! /usr/env/bin python3

from bs4 import BeautifulSoup as bs
import requests

import sys

url = sys.argv[1]

conteudo = requests.get(url).text

dt = bs(conteudo,'lxml')

tables = dt.find_all('table')


for i,table in enumerate(tables):
    print('-----------------------','Table',i,'-----------------------')
    lines = table.find_all('tr')
    for line in lines:
        elements = [x.text for x in line.find_all('td')]
        line_txt = "::".join(elements)
        print(line_txt)

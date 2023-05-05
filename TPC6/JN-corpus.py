#!/usr/bin/env python3

import os, sys
import datetime
import traceback

os.chdir(sys.path[0]) 
path = os.getcwd()

def create_news_symlink():
    """Checks if newspaper_scraper dir already exists, if not creates symlink to current dir"""
    # creating symlink
    if not os.path.exists('/tmp/.newspaper_scraper'):
        origem = f'{path}/newspaper_scraper'
        os.symlink(origem,'/tmp/.newspaper_scraper')


def create_date_dirs(p:str)->str:
    """Creates the year and month folder to save the news"""
    today = datetime.date.today()
    year = today.year
    month = today.month
    day = today.day

    # year and month folder
    os.makedirs(f'{p}/{year}/{month}',exist_ok=True)
    return f'{p}/{year}/{month}/{day}.html'
    


def main():
    """Main of the program"""
    create_news_symlink()
    import newspaper

    url = 'https://www.jn.pt'

    logs = open(f'{path}/logs.txt','w')
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logs.write(f'Geting articles [{now}]\n')

    jn = newspaper.build(url,memoized_articles=False)
    
    n_articles = jn.size()
    print('number of articles :',n_articles)

    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logs.write(f'{n_articles} articles [{now}]\n')

    out_path = create_date_dirs(f'{path}/news')

    out = open(out_path,'a')

    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logs.write(f'Starting to write to file [{now}]\n')

    out.write('<news>\n')
    i = 0
    for article in jn.articles:
        print(f'Article {i} of {n_articles}')
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logs.write(f'Article {i} of {n_articles} [{now}]\n')
        i +=1
        try:
            #print(article.url,article.title)
            ar = newspaper.Article(article.url)
            ar.download()
            ar.parse()
            out.write(f'''  <article>
        <title>
            {ar.title}
        </title>
        <url>
            {ar.url}
        </url>
        <autor>
            {ar.authors}
        </autor>
        <date>
            {ar.publish_date}
        </date>
        <tags>
            {ar.tags}
        </tags>
        <text>
            {ar.text}
        </text>
    </article>
''')
        except Exception:
            print(traceback.format_exc())
    out.write('</news>')
    out.close()

    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logs.write(f'Finished writing [{now}]\n')
    logs.close()


if __name__ == "__main__":
    main()


import sys
import argparse
import requests
from bs4 import BeautifulSoup

default = True

def prettify_html(r:requests.Response)->str:
    soup = BeautifulSoup(r.content.decode(r.encoding),features='lxml')
    return soup.prettify()

def similitarity_percent(string:str,difference:int)->float:
    """Returns the relative difference between the string and the actions number of actions to replicate it"""
    return difference/len(string)


def is_default():
    return default

def get_input(args):
    """Gets the input text according with the register in args"""
    text = ''
    if not args.input:
        for line in sys.stdin:
            text+=line
    else:
        input = args.input
        text = input.read()
    return text

def write_output(args,output):
    """Writes the ouput on the location registered in args"""
    if not args.output:
        for o in output:
            sys.stdout.write(o)
    else:
        for o in output:
            file = args.output[0]
            file.write(o)

def write_errors(args,errors):
    """Writes the errors on the location registered in args"""
    if not args.errors:
        for e in errors:
            sys.stdout.write(e)
    else:
        file = args.errors[0]
        for e in errors:
            file.write(e)






def process_arguments(__version__)->argparse.Namespace:
    """Process arguments from stdin"""
    parser = argparse.ArgumentParser(
        prog='tok',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=f'''
    --------------------------------------------------------------------
                    **BookScraper version {__version__}**
    --------------------------------------------------------------------
                Module to scrap book information from goodreads'''
    )
    parser.add_argument('-isbn',type=str,nargs='?',help='isbn of the book to scrape',default=None)
    parser.add_argument('-id',type=str,nargs='?',help='book id of the book to scrape',default=None)
    parser.add_argument('-btitle',type=str,nargs='?',help='name of the book to scrape (not precise)',default=None)
    parser.add_argument('-a','--author',type=str,nargs='?',help='author name or id to scrape',default=None)
    parser.add_argument('-o','--output',help='defines an output file',type=argparse.FileType('w'), nargs=1,default=None)
    parser.add_argument('-e','--errors',help='defines an output file for the errors',type=argparse.FileType('w'), nargs=1,default=None)
    parser.add_argument('--version','-V', action='version', version='%(prog)s '+__version__)

    return parser.parse_args()
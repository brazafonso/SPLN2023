import sys
import argparse


default = True

def is_default():
    return default

def get_input(args):
    """Gets the input text according with the register in procedure_dic"""
    text = ''
    if not args.input:
        for line in sys.stdin:
            text+=line
    else:
        input = args.input
        text = input.read()
    return text

def write_output(args,output):
    """Writes the ouput on the location registered in procedure_dic"""
    if not args.output:
        sys.stdout.write(output)
    else:
        file = args.output[0]
        file.write(output)


class defaultAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        global default
        default = False
        if namespace.options:
            namespace.options.append(option_string)
        else:
            namespace.options = [option_string]
       



def process_arguments(__version__):
    parser = argparse.ArgumentParser(
        prog='tok',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=f'''
    --------------------------------------------------------------------
                    **Tokenizer SPLN version {__version__}**
    --------------------------------------------------------------------
                Module to tokenize books (English by default)'''
    )
    parser.add_argument('input',metavar='filename',type=argparse.FileType('r'),nargs='?',help='input file of the text to tokenize',default=None)
    parser.add_argument('-o','--output',help='defines an output file',type=argparse.FileType('w'), nargs=1,default=None)
    parser.add_argument('-lan','--language',help='''
    defines a language to recognize, accordingly will use the languages settings (abreviatures, delimiters)
        (default to english)                    
                        ''',type=str, nargs=1,default='en')
    parser.add_argument('-p','--poem',help='saves poems delimited inside <poem></poem> in the text',action='store_true',default=False)
    parser.add_argument('-c','--chapter',help='treat chapters using the language delimiters (default english)',dest='options',action=defaultAction,nargs=0)
    parser.add_argument('-pu','--punctuation',help='treat punctuation using the language abreviations (default english)',dest='options',action=defaultAction,nargs=0)
    parser.add_argument('-pb','--pagebreak',help='treat pagebreak',dest='options',action=defaultAction,nargs=0)
    parser.add_argument('-js','--JoinSentence',help='treat sentences broken between lines, bringing them to the same line',dest='options',action=defaultAction,nargs=0)
    parser.add_argument('-spl','--SentencePerLine',help='each sentence is seperated to an individual line',dest='options',action=defaultAction,nargs=0)
    parser.add_argument('-par','--paragraphs',help='treat paragraphs, delimiting them with /PAR/',dest='options',action=defaultAction,nargs=0)
    parser.add_argument('--version','-V', action='version', version='%(prog)s '+__version__)

    return parser.parse_args()
import sys
import argparse

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


def process_arguments(__version__):
    parser = argparse.ArgumentParser(
        prog='tok',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=f'''
    --------------------------------------------------------------------
                    **Tokenizer SPLN version {__version__}**
    --------------------------------------------------------------------
                        Module to tokenize books'''
    )
    parser.add_argument('input',metavar='filename',type=argparse.FileType('r'),nargs='?',help='input file of the text to tokenize',default=None)
    parser.add_argument('-o','--output',help='defines an output file',type=argparse.FileType('w'), nargs=1,default=None)
    parser.add_argument('-p','--poem',help='saves poems delimited inside <poem></poem> in the text',action='store_true',default=False)
    parser.add_argument('--version','-V', action='version', version='%(prog)s '+__version__)
    return parser.parse_args()
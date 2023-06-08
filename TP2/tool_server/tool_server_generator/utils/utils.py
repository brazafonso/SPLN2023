import argparse


def parse_arguments(version)->argparse.Namespace:
    """Process arguments from stdin"""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description=f'''
    --------------------------------------------------------------------
                        **Tool Server**
    --------------------------------------------------------------------'''
    )
    parser.add_argument('config_file',metavar='filename',type=str,nargs=1,help='configure file')
    parser.add_argument('-s','--start_server'   ,action='store_true'      ,help='starts server automatically')
    parser.add_argument('-ng','--ngrok'   ,action='store_true'      ,help='uses ngrok to expose port. Please make sure to have ngrok installed and authenticated.')
    return parser.parse_args()


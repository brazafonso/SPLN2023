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
    parser.add_argument('config_file',metavar='filename',type=argparse.FileType('r'),nargs=1,help='configure file')
    parser.add_argument('-s','--start_server'   ,action='store_true'      ,help='starts server automatically')
    return parser.parse_args()

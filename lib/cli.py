from argparse import ArgumentParser
from optparse import OptionParser

args_parser = ArgumentParser()   
args_parser.add_argument('pr_number', type=int, help='pr number')
args_parser.add_argument('--no-dry-run', action='store_true')

def get_pr_number():
    return args_parser.parse_args().pr_number
def is_dry_run():
    return not args_parser.parse_args().no_dry_run

    



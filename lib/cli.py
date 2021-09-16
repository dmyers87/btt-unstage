from argparse import ArgumentParser
from optparse import OptionParser

args_parser = ArgumentParser()   
args_parser.add_argument('pr_number', type=int, help='pr number')
args_parser.add_argument('environment', type=bool, help='cluster | local')

def get_args():
    return args_parser.parse_args()

def get_moniker_and_pr_number():
    cli_parser = OptionParser()
    cli_parser.add_option("--moniker")
    cli_parser.add_option("--pr-number")
    cli_options, cli_args = cli_parser.parse_args()

    if cli_options.moniker is None or cli_options.pr_number is None:
        raise Exception("--moniker and --pr-number are required")    

    return (cli_options.moniker, cli_options.pr_number)
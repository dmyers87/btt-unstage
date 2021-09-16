from lib.cli import get_args

def in_cluster():
    return get_args().environment == "cluster"

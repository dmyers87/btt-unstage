from argparse import ArgumentParser
from lib.db import DBHelper, NoDatabaseException
from lib.redis import RedisHelper
from lib.env import EnvReader
from lib.k8s import K8sHelper, ClusterResourceNotFoundException


def main():

    env_reader = EnvReader(
        'DB_HOST',
        'DB_USER',
        'DB_PASSWORD',
    )

    args_parser = ArgumentParser()
    args_parser.add_argument('c5_monikers', type=str,
                             help='comma separated list of c5 monikers')
    args_parser.add_argument(
        '--load-kube-config-from-cluster', action='store_true')
    args_parser.add_argument('--no-dry-run', action='store_true')
    args = args_parser.parse_args()

    c5_monikers = [cm.strip().lower()
                   for cm in args.c5_monikers.strip().split(',')]

    for c5_moniker in c5_monikers:
        if c5_moniker[0] != 'c':
            raise Exception(
                f'C5 monikers start with c, {c5_moniker} does not')
        if len(c5_moniker) != 4:
            raise Exception(
                f'C5 monikers should have 4 characters, {c5_moniker} does not')

    load_kube_config_from_cluster = args.load_kube_config_from_cluster

    is_dry_run = not args.no_dry_run

    print(f'DRY RUN: {is_dry_run}')

    db = DBHelper(
        host=env_reader.get_var('DB_HOST'),
        user=env_reader.get_var('DB_USER'),
        pw=env_reader.get_var('DB_PASSWORD'),
        dry_run=is_dry_run
    )

    for c5_moniker in c5_monikers:

        print(f'=== {c5_moniker.upper()} ===')

        namespace = f'{c5_moniker}-dev'

        k8s_resources = K8sHelper(namespace, dry_run=is_dry_run)

        if load_kube_config_from_cluster:
            k8s_resources.load_config_from_cluster()
        else:
            k8s_resources.load_config_from_system()

        print(f'- deployment')
        try:
            deployment = f'{c5_moniker}-dev-c5'
            print(f'attempting to delete deployment {deployment}')
            k8s_resources.delete_deployment(deployment)
            print(f'deleted deployment {deployment}')
        except ClusterResourceNotFoundException as error:
            print(f'deployment does not exist, cannot delete')

        print(f'- namespace')
        try:
            print(f'attempting to delete {namespace}')
            k8s_resources.delete_namespace()
            print(f'deleted namespace {namespace}, terminating')
        except ClusterResourceNotFoundException as error:
            print(f'namespace does not exist, cannot delete')

        print('- databases')

        for c5_db_suffix in ['_dev', '_dev_tac']:

            c5_db = f'{c5_moniker}{c5_db_suffix}'

            try:
                print(f'attempting to delete database {c5_db}')
                db.delete_db(name=c5_db)
                print(f'deleted database {c5_db}')
            except NoDatabaseException:
                print(f'database {c5_db} does not exist, cannot delete')

    db.connection.close()


main()

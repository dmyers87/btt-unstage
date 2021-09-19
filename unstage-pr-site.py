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
        'REDIS_HOST'
    )

    args_parser = ArgumentParser()
    args_parser.add_argument('pr_monikers', type=str,
                             help='comma separated list of monikers')
    args_parser.add_argument('pr_number', type=int,
                             help='the pr number to tear down')
    args_parser.add_argument('site_type', type=str,
                             help='is site CLOUD or PRO', choices=['CLOUD', 'PRO'])
    args_parser.add_argument(
        '--load-kube-config-from-cluster', action='store_true')
    args_parser.add_argument('--no-dry-run', action='store_true')
    args = args_parser.parse_args()

    pr_monikers = [prm.strip().lower()
                   for prm in args.pr_monikers.strip().split(',')]
    site_type = args.site_type

    if site_type == "PRO":
        if len(pr_monikers) > 1:
            raise Exception(
                f'PRO sites only have 1 moniker, specified {len(pr_monikers)}')
        if len(pr_monikers[0]) != 3:
            raise Exception(
                f'PRO monikers should have 3 characters, not {len(pr_monikers[0])}')

    if site_type == "CLOUD":
        for pr_moniker in pr_monikers:
            if pr_moniker[0] != 'n':
                raise Exception(
                    f'CLOUD monikers start with n, {pr_moniker} does not')
            if len(pr_moniker) != 4:
                raise Exception(
                    f'CLOUD monikers should have 4 characters, {pr_moniker} does not')

    pr_number = args.pr_number

    load_kube_config_from_cluster = args.load_kube_config_from_cluster

    namespace = f'{"ngt" if site_type == "CLOUD" else pr_monikers[0] }-pr{pr_number}'

    is_dry_run = not args.no_dry_run

    print(f'DRY RUN: {is_dry_run}')

    db = DBHelper(
        host=env_reader.get_var('DB_HOST'),
        user=env_reader.get_var('DB_USER'),
        pw=env_reader.get_var('DB_PASSWORD'),
        dry_run=is_dry_run
    )

    redis = RedisHelper(host=env_reader.get_var('REDIS_HOST'))

    k8s_solr = K8sHelper('solr', dry_run=is_dry_run)
    if load_kube_config_from_cluster:
        k8s_solr.load_config_from_cluster()
    else:
        k8s_solr.load_config_from_system()

    for moniker in pr_monikers:
        print(f'=== {moniker.upper()} ===')

        build_id = f'{moniker}_pr{pr_number}'

        print('- solr')
        core_name = f'{moniker}-pr{pr_number}'
        print(f'deleting solr core {core_name}')
        solr_cmd_response = k8s_solr.execute_command_in_pod(
            pod_name='solr-0',
            command=['solr', 'delete', '-c', core_name]
        )
        print(solr_cmd_response.strip())

        try:
            print('- database')
            print(f'attempting to delete database {build_id}')
            db.delete_db(name=build_id)
            print(f'deleted database {build_id}')
        except NoDatabaseException:
            print(f'database {build_id} does not exist, cannot delete')

        try:
            print('- redis')
            pr_key_pattern = f'{build_id}:*'
            pr_keys = redis.get_keys(pr_key_pattern)
            if pr_keys:
                print(
                    f'attempting to delete {len(pr_keys)} keys with pattern "{pr_key_pattern}"')
                redis.delete_keys(pr_keys)
                print(
                    f'deleted {len(pr_keys)} keys with pattern "{pr_key_pattern}"')
            else:
                print(f'found 0 keys with pattern "{pr_key_pattern}"')
        except Exception as error:
            print('Error', error)

    print(f'=== deleting pr namespace & deployment ===')
    k8s_resources = K8sHelper(namespace, dry_run=is_dry_run)
    if load_kube_config_from_cluster:
        k8s_resources.load_config_from_cluster()
    else:
        k8s_resources.load_config_from_system()

    try:
        deployment = f'pr{pr_number}-cloud'
        print(f'attempting to delete deployment {deployment}')
        k8s_resources.delete_deployment(deployment)
        print(f'deleted deployment {deployment}')
    except ClusterResourceNotFoundException as error:
        print(f'deployment does not exist, cannot delete')

    try:
        print(f'attempting to delete {namespace}')
        k8s_resources.delete_namespace()
        print(f'deleted namespace {namespace}, terminating')
    except ClusterResourceNotFoundException as error:
        print(f'namespace does not exist, cannot delete')

    db.connection.close()


main()

#

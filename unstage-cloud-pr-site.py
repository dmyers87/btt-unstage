from argparse import ArgumentParser
from lib.github import GithubHelper
from lib.db import DBHelper, NoDatabaseException
from lib.redis import RedisHelper
from lib.env import EnvReader
from lib.k8s import K8sHelper, ClusterResourceNotFoundException


def main():

    env_reader = EnvReader(
        'GITHUB_ACCESS_TOKEN',
        'DB_HOST',
        'DB_USER',
        'DB_PASSWORD',
        'REDIS_HOST'
    )

    args_parser = ArgumentParser()
    args_parser.add_argument('pr_number', type=int, help='pr number')
    args_parser.add_argument('--no-dry-run', action='store_true')
    args = args_parser.parse_args()

    pr_number = args.pr_number
    is_dry_run = not args.no_dry_run

    print(f'DRY RUN: {is_dry_run}')

    namespace = f'ngt-pr{pr_number}'

    github = GithubHelper(
        repo_name='PropertyBrands/btt-ngt-d7',
        token=env_reader.get_var('GITHUB_ACCESS_TOKEN')
    )

    pr = github.get_pr(pr_number)
    pr_monikers = github.extract_monikers_from_cloud_pr(pr)

    if pr_monikers:

        db = DBHelper(
            host=env_reader.get_var('DB_HOST'),
            user=env_reader.get_var('DB_USER'),
            pw=env_reader.get_var('DB_PASSWORD'),
            dry_run=is_dry_run
        )

        redis = RedisHelper(host=env_reader.get_var('REDIS_HOST'))

        k8s_solr = K8sHelper('solr', dry_run=is_dry_run)

    for moniker in pr_monikers:
        print(f'=== {moniker.upper()} ===')

        build_id = f'{moniker}_pr{pr_number}'

        # print('- solr')
        # core_name = f'{moniker}-pr{pr_number}'
        # print(f'deleting solr core {core_name}')
        # solr_cmd_response = k8s_solr.execute_command_in_pod(
        #     pod_name='solr-0',
        #     command=['solr', 'delete', '-c', core_name]
        # )
        # print(solr_cmd_response.strip())

        try:
            print('- database')
            print(f'attempting to delete database {build_id}')
            db.delete_db(name=build_id)
            print(f'deleted database {build_id}')
        except NoDatabaseException:
            print(f'database {build_id} does not exist, cannot delete')

        try:
            print('- redis')
            pr_key_pattern = '{build_id}:*'
            pr_keys = redis.get_keys(pr_key_pattern)
            if pr_keys:
                print(
                    f'deleting {len(pr_keys)} keys with pattern "{pr_key_pattern}"')
                redis.delete_keys(*pr_keys)
            else:
                print(f'found 0 keys with pattern "{pr_key_pattern}"')
        except Exception as error:
            print('Error', error)

    print(f'=== deleting pr namespace & deployment ===')
    k8s_ngt = K8sHelper(namespace, dry_run=is_dry_run)

    try:
        deployment = f'pr{pr_number}-cloud'
        print(f'deleting deployment {deployment}')
        k8s_ngt.delete_deployment(deployment)
        print(f'deleted deployment {deployment}')
    except ClusterResourceNotFoundException as error:
        print(f'deployment does not exist, cannot delete')

    try:
        print(f'deleting namespace {namespace}')
        k8s_ngt.delete_namespace()
        print(f'namespace {namespace} terminating')
    except ClusterResourceNotFoundException as error:
        print(f'namespace does not exist, cannot delete')

    db.connection.close()


main()

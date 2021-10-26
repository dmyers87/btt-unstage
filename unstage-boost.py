from argparse import ArgumentParser
from lib.redis import RedisHelper
from lib.env import EnvReader
from lib.k8s import K8sHelper, ClusterResourceNotFoundException


def main():

    env_reader = EnvReader('REDIS_HOST')

    args_parser = ArgumentParser()
    args_parser.add_argument('pr_number', type=int,
                             help='the pr number to tear down')
    args_parser.add_argument(
        '--load-kube-config-from-cluster', action='store_true')
    args_parser.add_argument('--no-dry-run', action='store_true')
    args = args_parser.parse_args()

    pr_number = args.pr_number
    load_kube_config_from_cluster = args.load_kube_config_from_cluster

    is_dry_run = not args.no_dry_run

    print(f'DRY RUN: {is_dry_run}')

    namespace = f'api-pr{pr_number}'

    print(f'=== {namespace.upper()} ===')

    redis = RedisHelper(host=env_reader.get_var('REDIS_HOST'))

    print('- redis')
    pr_key_pattern = f'api_pr{pr_number}:*'

    try:
        pr_keys = redis.get_keys(pr_key_pattern)
        if pr_keys:
            print(
                f'attempting to delete {len(pr_keys)} keys with pattern "{pr_key_pattern}"')
            if not is_dry_run:
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

    deployments = k8s_resources.get_deployments()

    for deployment in deployments.items:
        try:
            print(
                f'attempting to delete deployment {deployment.metadata.name}')
            k8s_resources.delete_deployment(deployment.metadata.name)
            print(f'deleted deployment {deployment.metadata.name}')
        except ClusterResourceNotFoundException as error:
            print(f'deployment does not exist, cannot delete')

    try:
        print(f'attempting to delete {namespace}')
        k8s_resources.delete_namespace()
        print(f'deleted namespace {namespace}, terminating')
    except ClusterResourceNotFoundException as error:
        print(f'namespace does not exist, cannot delete')


main()

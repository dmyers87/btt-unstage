from lib.cli import is_dry_run
from os import getenv
from redis import Redis
from kubernetes import client as k8s_client, config as k8s_config, stream as k8s_stream
 
REDIS_HOST = getenv('REDIS_HOST') 
if not REDIS_HOST:
    raise Exception("REDIS_HOST required")

k8s_config.load_kube_config()

k8s_core_v1_api = k8s_client.CoreV1Api()
k8s_apps_v1_api = k8s_client.AppsV1Api()

def delete_solr_core(core_name: str):
    if is_dry_run():
        print(f'dry run: would be deleting core {core_name}, only retrieving status')
        solr_core_deletion_command = ['solr', 'status'] 
    else:
        solr_core_deletion_command = ['solr', 'delete', '-c', core_name]
    solr_core_deletion_response = k8s_stream.stream(
        k8s_core_v1_api.connect_get_namespaced_pod_exec,
        namespace='solr', 
        name='solr-0',
        command=solr_core_deletion_command,
        stderr=True, 
        stdin=False,
        stdout=True, 
        tty=False
    )

    return solr_core_deletion_response

def delete_redis_keys(pr_database: str):

    redis = Redis(host=REDIS_HOST)
    
    print(f'the following keys for {pr_database} exist:')

    staging_site_keys = redis.keys(f'{pr_database}:*')
    print(staging_site_keys)

    if is_dry_run():
        print('dry run: redis connection valid')
    else:
        if staging_site_keys:
            print(f'deleting keys')
            redis.delete(*staging_site_keys)
        else:
            print(f'no keys to delete!')
        
    redis.close()

def delete_deployment(namespace: str, deployment: str):
    if is_dry_run():
        print(f'dry run: would delete deployment {deployment}')
    else:
        k8s_apps_v1_api.delete_namespaced_deployment(
            namespace=namespace,
            name=deployment
        )
  
def delete_namespace(namespace: str):
    if is_dry_run():
        print(f'dry run: would delete namespace {namespace}')
    else:
        k8s_core_v1_api.delete_namespace(namespace)
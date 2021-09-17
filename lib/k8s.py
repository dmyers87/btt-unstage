from lib.cli import is_dry_run
from lib.env import get_env_var
from os import getenv
from redis import Redis
from kubernetes import client as k8s_client, config as k8s_config, stream as k8s_stream
 
REDIS_HOST = get_env_var('REDIS_HOST') 

k8s_config.load_kube_config()
k8s_core_v1_api = k8s_client.CoreV1Api()
k8s_apps_v1_api = k8s_client.AppsV1Api()

class SolrCoreNotFoundException(Exception):
    pass

def delete_solr_core(core: str):
    
    if is_dry_run():
        print(f'dry run: would be deleting core {core}, only retrieving status')
        solr_core_deletion_command = ['solr', 'status'] 
    else:
        solr_core_deletion_command = ['solr', 'delete', '-c', core]

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

    if f'ERROR: Collection {core} not found!' in solr_core_deletion_response:
        raise SolrCoreNotFoundException

    return solr_core_deletion_response

def create_redis_connection() -> Redis:
    return Redis(host=REDIS_HOST)

def get_redis_keys(redis_connection: Redis, redis_keys: str):
    return redis_connection.keys(redis_keys)

def delete_redis_keys(redis_connection: Redis, **redis_keys: str):
    return redis_connection.delete(**redis_keys)

class ClusterResourceNotFoundException(Exception):
    pass

def delete_deployment(namespace: str, deployment: str):
    if is_dry_run():
        print(f'dry run: would delete name {deployment}')
    else:
        try:
            k8s_apps_v1_api.delete_namespaced_deployment(
                namespace=namespace,
                name=deployment
            )
        except k8s_client.ApiException as error:
            if (error.status == 404):
                raise ClusterResourceNotFoundException()

  
def delete_namespace(namespace: str):
    if is_dry_run():
        print(f'dry run: would delete namespace {namespace}')
    else:
        try:
            k8s_core_v1_api.delete_namespace(namespace)
        except k8s_client.ApiException as error:
            if (error.status == 404):
                raise ClusterResourceNotFoundException()
        
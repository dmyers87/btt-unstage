from lib.env import in_cluster

from redis import Redis
from kubernetes import client as k8s_client, config as k8s_config, stream as k8s_stream
 
REDIS_HOST = "redis-master.redis.svc.cluster.local" if in_cluster() else "34.69.97.112"

k8s_config.load_incluster_config() if in_cluster() else k8s_config.load_kube_config()

k8s_core_v1_api = k8s_client.CoreV1Api()
k8s_apps_v1_api = k8s_client.AppsV1Api()

def delete_solr_core(core_name: str):
    if in_cluster():
        solr_core_deletion_command = ['solr', 'delete', '-c', core_name]
    else:
        print(f'test, would be deleting core {core_name}, only retrieving status')
        solr_core_deletion_command = ['solr', 'status'] 
    
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
    
    if in_cluster():
        print(f'deleting keys')
        redis.delete(staging_site_keys)
    else:
        print('test so not deleting keys')

    redis.close()


def delete_deployment(namespace: str, deployment: str):
    if in_cluster():
        k8s_apps_v1_api.delete_namespaced_deployment(
            namespace=namespace,
            name=deployment
        )
    else:
        print(f'test, would delete deployment {deployment}')


def delete_namespace(namespace: str):
    if in_cluster():
        k8s_core_v1_api.delete_namespace(namespace)
    else:
        print(f'test, would delete namespace {namespace}')
from kubernetes import client as k8s_client, config as k8s_config, stream as k8s_stream
 
REDIS_HOST = get_env_var('REDIS_HOST') 

k8s_config.load_kube_config()
k8s_core_v1_api = k8s_client.CoreV1Api()
k8s_apps_v1_api = k8s_client.AppsV1Api()

class SolrCoreNotFoundException(Exception):
    pass


class K8sHelper():

    def __init__(self, namespace: str):

        self.namespace = namespace
    
    def execute_command_in_pod(self, pod_name: str, command: list, is_dry_run=True, stderr=True, stdout=True) -> str:
        
        if is_dry_run:
            command = ['/bin/bash', 'echo', command.join(' ')]


        return k8s_stream.stream(
            k8s_core_v1_api.connect_get_namespaced_pod_exec,
            namespace='solr', 
            name='solr-0',
            command=command,
            stderr=stderr, 
            stdin=False,
            stdout=stdout, 
            tty=False
        )
        # if f'ERROR: Collection {core} not found!' in solr_core_deletion_response:
        #     raise SolrCoreNotFoundException

    def delete_deployment(self, deployment: str):
        if not is_dry_run:
            try:
                k8s_apps_v1_api.delete_namespaced_deployment(
                    namespace=self.namespace,
                    name=deployment
                )
            except k8s_client.ApiException as error:
                if (error.status == 404):
                    raise ClusterResourceNotFoundException()

            return True

        return False


    def delete_namespace(self):
        if not is_dry_run:
            try:
                k8s_core_v1_api.delete_namespace(self.namespace)
            except k8s_client.ApiException as error:
                if (error.status == 404):
                    raise ClusterResourceNotFoundException()
            return True
        return False

# redis


class ClusterResourceNotFoundException(Exception):
    pass
# /redis




# k8s



  

# /k8s        
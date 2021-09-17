from kubernetes import client as k8s_client, config as k8s_config, stream as k8s_stream

k8s_config.load_kube_config()
k8s_core_v1_api = k8s_client.CoreV1Api()
k8s_apps_v1_api = k8s_client.AppsV1Api()


class K8sHelper():

    def __init__(self, namespace: str, dry_run: bool = True):

        self.namespace = namespace
        self.dry_run = dry_run

    def execute_command_in_pod(self, pod_name: str, command: list, stderr=True, stdout=True) -> str:

        if self.dry_run:
            command_str = ' '.join(command)
            command = ['echo', f'echoing "{command_str}"']

        return k8s_stream.stream(
            k8s_core_v1_api.connect_get_namespaced_pod_exec,
            namespace=self.namespace,
            name=pod_name,
            command=command,
            stderr=stderr,
            stdin=False,
            stdout=stdout,
            tty=False
        )
        # if f'ERROR: Collection {core} not found!' in solr_core_deletion_response:
        #     raise SolrCoreNotFoundException

    def delete_deployment(self, deployment: str):
        if not self.dry_run:
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
        if not self.dry_run:
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

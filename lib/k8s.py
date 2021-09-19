from kubernetes import client as k8s_client, config as k8s_config, stream as k8s_stream


class K8sHelper():

    def __init__(self, namespace: str, dry_run: bool = True):

        self.namespace = namespace
        self.dry_run = dry_run

    def load_config_from_cluster(self):
        self.k8s_config = k8s_config.load_incluster_config()
        self._generate_api_clients()

    def load_config_from_system(self):
        self.k8s_config = k8s_config.load_kube_config()
        self._generate_api_clients()

    def _generate_api_clients(self):
        self.k8s_core_v1_api = k8s_client.CoreV1Api()
        self.k8s_apps_v1_api = k8s_client.AppsV1Api()

    def execute_command_in_pod(self, pod_name: str, command: list, stderr=True, stdout=True) -> str:

        if self.dry_run:
            command_str = ' '.join(command)
            command = ['echo', f'echoing "{command_str}"']

        return k8s_stream.stream(
            self.k8s_core_v1_api.connect_get_namespaced_pod_exec,
            namespace=self.namespace,
            name=pod_name,
            command=command,
            stderr=stderr,
            stdin=False,
            stdout=stdout,
            tty=False
        )

    def delete_deployment(self, deployment: str):
        if not self.dry_run:
            try:
                self.k8s_apps_v1_api.delete_namespaced_deployment(
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
                self.k8s_core_v1_api.delete_namespace(self.namespace)
            except k8s_client.ApiException as error:
                if (error.status == 404):
                    raise ClusterResourceNotFoundException()
            return True
        return False


class ClusterResourceNotFoundException(Exception):
    pass

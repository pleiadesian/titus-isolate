from threading import Thread

from kubernetes import client, config, watch

from titus_isolate import log
from titus_isolate.utils import get_config_manager

config_file_path = '/run/kubernetes/config'


class PodManager:
    def __init__(self, config_path=config_file_path):
        config.load_kube_config(config_file=config_file_path)

    def start(self):
        Thread(target=self.__watch).start()

    def __watch(self):
        v1 = client.CoreV1Api()
        w = watch.Watch()

        instance_id = get_config_manager().get_str("EC2_INSTANCE_ID")
        field_selector = "metadata.name={}".format(instance_id)

        for event in w.stream(v1.list_pod_for_all_namespaces, field_selector=field_selector, _request_timeout=60):
            log.info("Received event: {}".format(event))

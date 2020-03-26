
# https://container.forecast.{us-east-1/us-west-2/eu-west-1}.streaming{test/prod}.titus.netflix.net:7004/v1/containersForecast
import json
from typing import Union, Dict, List

import requests
from kubernetes.client import V1Pod

from titus_isolate import log
from titus_isolate.allocate.constants import CPU_USAGE, MEM_USAGE, NET_RECV_USAGE, NET_TRANS_USAGE, DISK_USAGE
from titus_isolate.config.config_manager import ConfigManager
from titus_isolate.model.utils import get_job_descriptor, get_start_time, get_main_container_status, CPU
from titus_isolate.monitor.resource_usage import GlobalResourceUsage
from titus_isolate.monitor.workload_monitor_manager import WorkloadMonitorManager
from titus_isolate.predict.resource_usage_prediction import ResourceUsagePredictions, ResourceUsagePrediction
from titus_isolate.utils import get_config_manager, get_pod_manager, get_workload_monitor_manager, \
    managers_are_initialized

# https://container.forecast.{us-east-1/us-west-2/eu-west-1}.streaming{test/prod}.titus.netflix.net:7004/v1/containersForecast
URL_FORMAT = 'https://container.forecast.{}.streaming{}.titus.netflix.net:7004/v1/containersForecast'

RESOURCE_HEADING_MAPPINGS = {
    CPU_USAGE: CPU,
    MEM_USAGE: "mem",
    NET_RECV_USAGE: "net_recv",
    NET_TRANS_USAGE: "net_trans",
    DISK_USAGE: "disk"
}


def get_url(config_manager: ConfigManager) -> str:
    return URL_FORMAT.format(config_manager.get_region(), config_manager.get_environment())


def get_predictions(client_cert_path: str, client_key_path: str, url: str, body: dict) -> Union[dict, None]:
    log.debug("url: %s, body: %s", url, body)
    response = requests.get(
        url,
        json=body,
        cert=(client_cert_path, client_key_path),
        verify=False)
    if response.status_code != 200:
        log.error("Failed to query resource prediction service: %s", response.content)
        return None

    resp_bytes = response.content
    resp_str = resp_bytes.decode('utf8')
    resp_json = json.loads(resp_str.strip())
    return resp_json


def get_first_window_cpu_prediction(prediction: ResourceUsagePrediction):
    cpu_predictions = prediction.resource_type_predictions[CPU]
    p95_cpu_predictions = cpu_predictions.predictions['p95']
    return p95_cpu_predictions[0]


def get_first_window_cpu_predictions(predictions: ResourceUsagePredictions):
    simple_predictions = {}
    for w_id, prediction in predictions.predictions.items():
        simple_predictions[w_id] = get_first_window_cpu_prediction(prediction)


class ResourceUsagePredictor:

    @staticmethod
    def __translate_usage(usages: Dict[str, List[float]]) -> dict:
        out_usage = {}
        for resource_name, values in usages.items():
            out_usage[RESOURCE_HEADING_MAPPINGS[resource_name]] = values[:60]

        return out_usage

    def __get_job_body(self, pod: V1Pod, resource_usage: GlobalResourceUsage):
        return {
            "job_id": pod.metadata.name,
            "job_descriptor": get_job_descriptor(pod),
            "task_data": {
                "started_ts_ms": str(get_start_time(pod)),
                "past_usage": self.__translate_usage(
                    resource_usage.get_all_usage_for_workload(pod.metadata.name))
            }
        }

    def __get_body(self, pods: List[V1Pod], resource_usage: GlobalResourceUsage) -> Union[dict, None]:
        return {
            "jobs": [self.__get_job_body(p, resource_usage) for p in pods]
        }

    @staticmethod
    def is_running(pod: V1Pod) -> bool:
        if pod.status.phase != "Running":
            log.info("Pod phase is %s, not Running", pod.status.phase)
            return False

        status = get_main_container_status(pod)
        if status is None:
            log.info("Couldn't find the main container's status")
            return False

        running = status.state.running
        if running is None:
            log.info("Container status state is not running")
            return False

        return True

    def get_predictions(self,
                        pods: List[V1Pod],
                        resource_usage: GlobalResourceUsage) -> Union[ResourceUsagePredictions, None]:

        running_pods = []
        for p in pods:
            if p.metadata.name in resource_usage.get_workload_ids():
                running_pods.append(p)
            else:
                log.info("Pod is not yet running: %s", p.metadata.name)

        client_crt = '/run/metatron/certificates/client.crt'
        client_key = '/run/metatron/certificates/client.key'
        url = get_url(get_config_manager())
        body = self.__get_body(running_pods, resource_usage)
        if body is None:
            log.info("Unable to generate a prediction request body")
            return None

        predictions = get_predictions(client_crt, client_key, url, body)
        if predictions is None:
            return None

        return ResourceUsagePredictions(predictions)

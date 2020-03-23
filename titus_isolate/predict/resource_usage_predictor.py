
# https://container.forecast.{us-east-1/us-west-2/eu-west-1}.streaming{test/prod}.titus.netflix.net:7004/v1/containersForecast
import json
from typing import Union

import requests
from kubernetes.client import V1Pod

from titus_isolate import log
from titus_isolate.allocate.constants import CPU_USAGE, MEM_USAGE, NET_RECV_USAGE, NET_TRANS_USAGE, DISK_USAGE
from titus_isolate.config.config_manager import ConfigManager
from titus_isolate.model.utils import get_job_descriptor, get_start_time, get_main_container_status, CPU
from titus_isolate.monitor.workload_monitor_manager import WorkloadMonitorManager
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


class ResourceUsagePredictor:

    def __translate_usage(self, pcp_usage: dict, workload_id: str) -> dict:
        # {
        #     'cpu_usage': {
        #         'daf6f318-a270-432d-b27e-4c7fe559755a': ['0.0', ..., '0.0]
        #     },
        #     'mem_usage': {
        #         'daf6f318-a270-432d-b27e-4c7fe559755a': ['3186688.0', ..., '3186688.0']
        #     },
        #     'net_recv_usage': {
        #         'daf6f318-a270-432d-b27e-4c7fe559755a': ['178.867', ..., '181.767']
        #     },
        #     'net_trans_usage': {
        #         'daf6f318-a270-432d-b27e-4c7fe559755a': ['317.05', ..., '317.067']
        #     },
        #     'disk_usage': {
        #         'daf6f318-a270-432d-b27e-4c7fe559755a': ['36864.0', ..., '36864.0']
        #     }
        # }
        out_usage = {}

        for k in RESOURCE_HEADING_MAPPINGS.keys():
            res_usage = pcp_usage.get(k, None)
            if res_usage is None:
                continue

            workload_res_usage = res_usage.get(workload_id, None)
            if workload_res_usage is None:
                continue

            out_usage[RESOURCE_HEADING_MAPPINGS[k]] = workload_res_usage[:60]

        return out_usage

    def __get_body(self, pod: V1Pod, wmm: WorkloadMonitorManager) -> Union[dict, None]:
        return {
            "jobs": [
                {
                    "job_id": pod.metadata.name,
                    "job_descriptor": get_job_descriptor(pod),
                    "task_data": {
                        "started_ts_ms": str(get_start_time(pod)),
                        "past_usage": self.__translate_usage(wmm.get_pcp_usage(), pod.metadata.name)
                    }
                }
            ]
        }

    def is_running(self, pod: V1Pod) -> bool:
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

    def get_predictions(self, workload_id: str) -> Union[dict, None]:
        if not managers_are_initialized():
            log.warning("Managers are not yet initialized")
            return None

        pod = get_pod_manager().get_pod(workload_id)
        if pod is None:
            log.warning("Pod not found")
            return None

        if not self.is_running(pod):
            log.info("Pod is not yet running")
            return None

        client_crt = '/run/metatron/certificates/client.crt'
        client_key = '/run/metatron/certificates/client.key'
        url = get_url(get_config_manager())
        body = self.__get_body(pod, get_workload_monitor_manager())
        if body is None:
            log.info("Unable to generate a prediction request body")
            return None

        return get_predictions(client_crt, client_key, url, body)

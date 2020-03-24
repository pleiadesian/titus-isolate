import base64
import gzip
import json
from datetime import datetime

from typing import Dict, List, Union

from kubernetes.client import V1Container, V1Pod, V1ContainerStatus
from kubernetes.utils import parse_quantity

from titus_isolate import log
from titus_isolate.allocate.constants import FREE_THREAD_IDS
from titus_isolate.event.constants import BURST, STATIC
from titus_isolate.metrics.constants import RUNNING
from titus_isolate.model.constants import *
from titus_isolate.model.duration_prediction import DurationPrediction
from titus_isolate.model.processor.cpu import Cpu
from titus_isolate.model.workload import Workload
from titus_isolate.monitor.free_thread_provider import FreeThreadProvider
from titus_isolate.utils import get_pod_manager
from titus_isolate.watcher.pod_manager import PodManager


def get_duration_predictions(input: str) -> List[DurationPrediction]:
    try:
        # "0.05=0.29953;0.1=0.29953;0.15=0.29953;0.2=0.29953;0.25=0.29953;0.3=0.29953;0.35=0.29953;0.4=0.29953;0.45=0.29953;0.5=0.29953;0.55=0.29953;0.6=0.29953;0.65=0.29953;0.7=0.29953;0.75=0.29953;0.8=0.29953;0.85=0.29953;0.9=0.29953;0.95=0.29953"
        duration_predictions = []
        pairs = input.split(';')
        for p in pairs:
            k, v = p.split('=')
            duration_predictions.append(DurationPrediction(float(k), float(v)))

        return duration_predictions
    except:
        log.exception("Failed to parse duration predictions: '{}'".format(input))
        return []


def get_start_time(pod: V1Pod) -> Union[int, None]:
    """
    Returns the start time of the main container in ms from UTC epoch
    """
    if pod.status.phase != "Running":
        return None

    main_container_status = get_main_container_status(pod)
    if main_container_status is None:
        return None

    state = main_container_status.state
    if state is None:
        return None

    running = state.running
    if running is None:
        return None

    return int(running.started_at.timestamp() * 1000)


def get_main_container_status(pod: V1Pod) -> Union[V1ContainerStatus, None]:
    statuses = [s for s in pod.status.container_statuses if s.name == pod.metadata.name]
    if len(statuses) != 1:
        return None

    return statuses[0]


def get_main_container(pod: V1Pod) -> Union[V1Container, None]:
    pod_name = pod.metadata.name
    containers = [c for c in pod.spec.containers if c.name == pod_name]

    if len(containers) == 1:
        return containers[0]

    log.info("Failed to find main container for: %s", pod_name)
    return None


def get_job_descriptor(pod: V1Pod) -> Union[object, None]:
    metadata = pod.metadata
    annotations = metadata.annotations

    if JOB_DESCRIPTOR not in annotations.keys():
        return None

    return decode_job_descriptor(annotations.get(JOB_DESCRIPTOR))


def decode_job_descriptor(encoded_job_descriptor: str) -> object:
    jd_bytes = base64.b64decode(encoded_job_descriptor, validate=True)
    jd_bytes = gzip.decompress(jd_bytes)
    return json.loads(jd_bytes.decode("utf-8"))


def get_app_name(job_descriptor: object) -> str:
    return job_descriptor[APP_NAME]


def get_image(job_descriptor: object) -> str:
    return job_descriptor[CONTAINER][IMAGE][NAME]


def get_cmd(job_descriptor: object) -> str:
    return ' '.join(job_descriptor[CONTAINER][COMMAND])


def get_entrypoint(job_descriptor: object) -> str:
    return ' '.join(job_descriptor[CONTAINER][ENTRYPOINT])


def get_job_type(job_descriptor: object) -> str:
    return job_descriptor[CONTAINER][IMAGE][NAME]


def parse_kubernetes_value(val: str) -> float:
    return str(parse_quantity(val))


def get_workload_from_pod(pod: V1Pod) -> Workload:
    metadata = pod.metadata
    main_container = get_main_container(pod)
    resource_requests = main_container.resources.requests

    launch_time = metadata.creation_timestamp.timestamp()
    identifier = metadata.name

    # Resources
    cpus = parse_kubernetes_value(resource_requests[CPU])
    mem = parse_kubernetes_value(resource_requests[MEMORY])
    network = parse_kubernetes_value(resource_requests[TITUS_NETWORK])

    if EPHEMERAL_STORAGE in resource_requests.keys():
        disk = resource_requests[EPHEMERAL_STORAGE]
    else:
        disk = resource_requests[TITUS_DISK]
    disk = parse_kubernetes_value(disk)

    # Job metadata
    job_descriptor = get_job_descriptor(pod)
    log.debug("job_descriptor: %s", job_descriptor)
    app_name = get_app_name(job_descriptor)
    owner_email = metadata.annotations[OWNER_EMAIL]
    image = get_image(job_descriptor)
    command = get_cmd(job_descriptor)
    entrypoint = get_entrypoint(job_descriptor)
    job_type = metadata.annotations[WORKLOAD_JSON_JOB_TYPE_KEY]

    workload_type_str = metadata.annotations.get(CPU_BURSTING)
    workload_type = STATIC
    if workload_type_str is not None and str(workload_type_str).lower() == "true":
        workload_type = BURST

    opportunistic_cpus = 0
    if WORKLOAD_JSON_OPPORTUNISTIC_CPU_KEY in metadata.annotations.keys():
        opportunistic_cpus = metadata.annotations.get(WORKLOAD_JSON_OPPORTUNISTIC_CPU_KEY)

    duration_predictions = []
    if WORKLOAD_JSON_RUNTIME_PREDICTIONS_KEY in metadata.annotations.keys():
        duration_predictions = \
            get_duration_predictions(metadata.annotations.get(WORKLOAD_JSON_RUNTIME_PREDICTIONS_KEY))

    return Workload(
        launch_time=launch_time,
        identifier=identifier,
        thread_count=cpus,
        mem=mem,
        disk=disk,
        network=network,
        app_name=app_name,
        owner_email=owner_email,
        image=image,
        command=command,
        entrypoint=entrypoint,
        job_type=job_type,
        workload_type=workload_type,
        opportunistic_thread_count=opportunistic_cpus,
        duration_predictions=duration_predictions)


def get_workload_from_kubernetes(identifier: str) -> Union[Workload, None]:

    def __get_typed_pod_manager() -> PodManager:
        return get_pod_manager()

    pod_manager = __get_typed_pod_manager()
    if pod_manager is None:
        return None

    pod = pod_manager.get_pod(identifier)
    if pod is None:
        return None

    return get_workload_from_pod(pod)


def get_burst_workloads(workloads):
    return get_workloads_by_type(workloads, BURST)


def get_static_workloads(workloads):
    return get_workloads_by_type(workloads, STATIC)


def get_workloads_by_type(workloads, workload_type):
    return [w for w in workloads if w.get_type() == workload_type]


def get_sorted_workloads(workloads: List[Workload]):
    return sorted(workloads, key=lambda w: w.get_creation_time())


def release_all_threads(cpu, workloads):
    for w in workloads:
        release_threads(cpu, w.get_id())


def release_threads(cpu, workload_id):
    for t in cpu.get_threads():
        t.free(workload_id)


def update_burst_workloads(
        cpu: Cpu,
        workload_map: Dict[str, Workload],
        free_thread_provider: FreeThreadProvider,
        metadata: dict):

    free_threads = free_thread_provider.get_free_threads(cpu, workload_map)
    metadata[FREE_THREAD_IDS] = [t.get_id() for t in free_threads]

    burst_workloads = get_burst_workloads(workload_map.values())
    if len(burst_workloads) == 0:
        return

    for t in free_threads:
        for w in burst_workloads:
            t.claim(w.get_id())


def rebalance(cpu: Cpu, workloads: dict, free_thread_provider: FreeThreadProvider, metadata: dict) -> Cpu:
    burst_workloads = get_burst_workloads(workloads.values())
    release_all_threads(cpu, burst_workloads)
    update_burst_workloads(cpu, workloads, free_thread_provider, metadata)

    return cpu

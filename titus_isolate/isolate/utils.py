from titus_isolate.docker.constants import BURST, STATIC


def get_burst_workloads(workloads):
    return get_workloads_by_type(workloads, BURST)


def get_static_workloads(workloads):
    return get_workloads_by_type(workloads, STATIC)


def get_workloads_by_type(workloads, workload_type):
    return [w for w in workloads if w.get_type() == workload_type]


def get_thread_ids(workload_id, threads):
    return [t.get_id() for t in threads if t.get_workload_id() == workload_id]

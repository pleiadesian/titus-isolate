import copy

from titus_isolate.allocate.allocate_request import AllocateRequest, deserialize_allocate_request
from titus_isolate.allocate.constants import WORKLOAD_ID
from titus_isolate.model.processor.cpu import Cpu


class AllocateThreadsRequest(AllocateRequest):

    def __init__(self,
                 cpu: Cpu,
                 workload_id: str,
                 workloads: dict,
                 cpu_usage: dict,
                 mem_usage: dict,
                 net_recv_usage: dict,
                 net_trans_usage: dict,
                 disk_usage: dict,
                 metadata: dict):
        """
        A threads request encapsulates all information needed to assign threads to workloads when a workload is being
        added or removed.

        :param cpu: An object indicating the state of the CPU before workload assignment
        :param workload_id: The id of the workload being added or removed
        :param workloads: A map of all relevant workloads including the workload to be assigned
                          The keys are workload ids, the objects are Workload objects
        """
        super().__init__(
            cpu=cpu,
            workloads=workloads,
            cpu_usage=cpu_usage,
            mem_usage=mem_usage,
            net_recv_usage=net_recv_usage,
            net_trans_usage=net_trans_usage,
            disk_usage=disk_usage,
            metadata=metadata)
        self.__workload_id = copy.deepcopy(workload_id)

    def get_workload_id(self):
        return self.__workload_id

    def to_dict(self):
        d = super().to_dict()
        d[WORKLOAD_ID] = self.get_workload_id()
        return d


def deserialize_allocate_threads_request(serialized_request: dict) -> AllocateThreadsRequest:
    allocate_request = deserialize_allocate_request(serialized_request)
    workload_id = serialized_request[WORKLOAD_ID]
    return AllocateThreadsRequest(
        cpu=allocate_request.get_cpu(),
        workload_id=workload_id,
        workloads=allocate_request.get_workloads(),
        cpu_usage=allocate_request.get_cpu_usage(),
        mem_usage=allocate_request.get_mem_usage(),
        net_recv_usage=allocate_request.get_net_recv_usage(),
        net_trans_usage=allocate_request.get_net_trans_usage(),
        disk_usage=allocate_request.get_disk_usage(),
        metadata=allocate_request.get_metadata())

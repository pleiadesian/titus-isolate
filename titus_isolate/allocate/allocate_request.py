from typing import Dict

from titus_isolate.allocate.constants import CPU, CPU_USAGE, WORKLOADS, METADATA, HISTORY, SNAPSHOT
from titus_isolate.allocate.utils import parse_cpu, parse_workloads, parse_cpu_usage
from titus_isolate.model.processor.cpu import Cpu
from titus_isolate.model.workload import Workload
from titus_isolate.monitor.cpu_usage import WorkloadCpuUsage


class AllocateRequest:

    def __init__(
            self,
            cpu: Cpu,
            workloads: Dict[str, Workload],
            cpu_usage: Dict[str, WorkloadCpuUsage],
            metadata: dict):
        """
        A rebalance request encapsulates all information needed to rebalance the assignment of threads to workloads.

        :param cpu: An object indicating the state of the CPU before workload assignment
        :param workloads: A map of all relevant workloads including the workload to be assigned
                          The keys are workload ids, the objects are Workload objects
        :param cpu_usage: A map of cpu usage per workload
        """
        self.__cpu = cpu
        self.__workloads = workloads
        self.__cpu_usage = cpu_usage
        self.__metadata = metadata

    def get_cpu(self) -> Cpu:
        return self.__cpu

    def get_cpu_usage(self) -> Dict[str, WorkloadCpuUsage]:
        return self.__cpu_usage

    def get_workloads(self) -> Dict[str, Workload]:
        return self.__workloads

    def get_metadata(self) -> dict:
        return self.__metadata

    def to_dict(self):
        return {
            CPU: self.get_cpu().to_dict(),
            CPU_USAGE: self.__get_serializable_usage(self.get_cpu_usage()),
            WORKLOADS: self.__get_serializable_workloads(list(self.get_workloads().values())),
            METADATA: self.get_metadata()
        }

    @staticmethod
    def __get_serializable_usage(cpu_usage: Dict[str, WorkloadCpuUsage]):
        serializable_history = []
        serializable_snapshot = []

        for w_id, usage in cpu_usage.items():
            for value in usage.history:
                serializable_history.append(str(value))
            for value in usage.snapshot:
                serializable_snapshot.append(str(value))

        return {
            HISTORY: serializable_history,
            SNAPSHOT: serializable_snapshot
        }

    @staticmethod
    def __get_serializable_workloads(workloads: list):
        serializable_workloads = {}
        for w in workloads:
            serializable_workloads[w.get_id()] = w.to_dict()

        return serializable_workloads


def deserialize_allocate_request(serialized_request: dict) -> AllocateRequest:
    cpu = parse_cpu(serialized_request[CPU])
    workloads = parse_workloads(serialized_request[WORKLOADS])
    cpu_usage = parse_cpu_usage(serialized_request[CPU_USAGE])
    metadata = serialized_request[METADATA]
    return AllocateRequest(cpu, workloads, cpu_usage, metadata)

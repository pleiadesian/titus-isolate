from abc import abstractmethod
from typing import Dict

from titus_isolate.monitor.cpu_usage import WorkloadCpuUsage


class CpuUsageProvider:

    @abstractmethod
    def get_cpu_usage(self, seconds: int, agg_granularity_secs: int) -> Dict[str, WorkloadCpuUsage]:
        """
        Returns CPU usage per workload over the last `seconds` seconds, aggregated at `agg_granularity_secs`.
        """
        pass

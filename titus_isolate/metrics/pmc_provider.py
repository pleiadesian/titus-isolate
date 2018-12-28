import time

from titus_isolate.isolate.utils import get_thread_ids
from titus_isolate.metrics.titus_pmc import TitusPmc
from titus_isolate.utils import get_logger

MISS_COUNT_TABLE_NAME = 'llc_miss_count'
REF_COUNT_TABLE_NAME = 'llc_ref_count'

log = get_logger()


class PmcProvider:
    def __init__(self, bpf, context_provider, cpu):
        self.__bpf = bpf
        self.__tables = [MISS_COUNT_TABLE_NAME, REF_COUNT_TABLE_NAME]
        self.__context_provider = context_provider
        self.__cpu = cpu

    def get_metrics(self, duration):
        metrics = []
        for table_name in self.__tables:
            table = self.__bpf.get_table(table_name)
            timestamp = time.time()
            metrics += self.__get_table_metrics(table, table_name, timestamp, duration)
            table.clear()

        return metrics

    def __get_table_metrics(self, table, metric_name, timestamp, duration):
        metrics = []
        try:
            log.info("Processing metric table: {}, with {} items".format(metric_name, len(table.items())))
            for (k, v) in table.items():
                if k.pid == 0:
                    continue
                task_id = self.__context_provider.get_task_id(k.pid)
                job_id = self.__context_provider.get_job_id(k.pid)

                if task_id is not None:
                    metric = TitusPmc(
                        timestamp=timestamp,
                        duration=duration,
                        name=metric_name,
                        value=int(v.value),
                        pid=k.pid,
                        cpu_id=k.cpu,
                        job_id=job_id,
                        task_id=task_id,
                        thread_ids=get_thread_ids(task_id, self.__cpu.get_threads()))
                    log.info("metric: {}".format(metric))
                    metrics.append(metric)
        except:
            log.exception("Failed to process the metric table: {}".format(metric_name))

        return metrics

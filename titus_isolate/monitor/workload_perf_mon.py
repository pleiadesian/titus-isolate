import calendar
import collections
from datetime import datetime as dt
from math import ceil
from threading import Lock

import numpy as np

from titus_isolate import log
from titus_isolate.monitor.cpu_usage import CpuUsageHistory, CpuUsageSnapshot, WorkloadCpuUsage


class WorkloadPerformanceMonitor:

    def __init__(self, metrics_provider, sample_frequency_sec):
        self.__metrics_provider = metrics_provider
        self.__sample_frequency_sec = sample_frequency_sec

        # Maintain buffers for the last hour
        self.__max_buffer_size = ceil(60 * 60 / sample_frequency_sec)
        self.__buffer_lock = Lock()
        self.__timestamps = collections.deque([], self.__max_buffer_size)
        self.__buffers = []

    def get_workload(self):
        return self.__metrics_provider.get_workload()

    def get_buffers(self):
        with self.__buffer_lock:
            return calendar.timegm(dt.utcnow().timetuple()), \
                   [calendar.timegm(t.timetuple()) for t in self.__timestamps], \
                   [list(e) for e in self.__buffers]

    def get_cpu_usage(self, seconds, agg_granularity_secs=60) -> WorkloadCpuUsage:
        with self.__buffer_lock:
            history = self.get_usage_history(seconds, agg_granularity_secs)
            snapshot = self.get_usage_snapshot()
            return WorkloadCpuUsage(history, snapshot)

    def get_usage_history(self, seconds, agg_granularity_secs=60) -> CpuUsageHistory:
        num_buckets = ceil(seconds / agg_granularity_secs)
        if num_buckets > self.__max_buffer_size:
            raise Exception("Aggregation buffer too small to satisfy query.")

        ts_snapshot, timestamps, buffers = self.get_buffers()
        values = WorkloadPerformanceMonitor.normalize_data(
            ts_snapshot,
            timestamps,
            buffers,
            num_buckets,
            agg_granularity_secs).tolist()

        return CpuUsageHistory(seconds, agg_granularity_secs, list(values))

    def get_usage_snapshot(self) -> CpuUsageSnapshot:
        if len(self.__timestamps) < 2:
            return None

        with self.__buffer_lock:
            snapshot = []
            for buffer in self.__buffers:
                snapshot.append(buffer[-1] - buffer[-2])

            return CpuUsageSnapshot(self.__sample_frequency_sec, snapshot)

    def sample(self):
        cpu_usage_snapshot = self.__metrics_provider.get_cpu_usage()
        if cpu_usage_snapshot is None:
            log.debug("No cpu usage snapshot available for workload: '{}'".format(self.get_workload().get_id()))
            return

        with self.__buffer_lock:
            if len(self.__buffers) == 0:
                self.__buffers = [collections.deque([], self.__max_buffer_size) for _ in range(len(cpu_usage_snapshot.rows))]

            self.__timestamps.append(cpu_usage_snapshot.timestamp)
            for row in cpu_usage_snapshot.rows:
                self.__buffers[row.pu_id].append(int(row.user) + int(row.system))

            log.debug("Took snapshot of metrics for workload: '{}'".format(self.get_workload().get_id()))

    @staticmethod
    def normalize_data(ts_snapshot, timestamps, buffers, num_buckets=60, bucket_size_secs=60):
        proc_time = np.full((num_buckets,), np.nan, dtype=np.float32)

        if len(timestamps) == 0:
            return proc_time

        ts_max = ts_snapshot
        for i in range(num_buckets):
            ts_min = ts_max - bucket_size_secs

            # get slice:
            slice_ts_min = np.searchsorted(timestamps, ts_min)
            slice_ts_max = np.searchsorted(timestamps, ts_max, 'right')
            if slice_ts_max == len(timestamps):
                slice_ts_max -= 1

            ts_max = ts_min

            if slice_ts_min == slice_ts_max:
                continue

            if slice_ts_min < 0 or slice_ts_min >= len(timestamps):
                continue

            if slice_ts_max < 0 or slice_ts_max >= len(timestamps):
                continue

            if timestamps[slice_ts_max] < ts_min - bucket_size_secs:
                continue
            # this should be matching Atlas:
            time_diff_ns = (timestamps[slice_ts_max] - timestamps[slice_ts_min]) * 1000000000
            s = 0.0
            for b in buffers: # sum across all cpus
                s += b[slice_ts_max] - b[slice_ts_min]
            if time_diff_ns > 0:
                s /= time_diff_ns
            proc_time[num_buckets - 1 - i] = s

        return proc_time

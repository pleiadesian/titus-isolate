from titus_isolate.allocate.constants import HISTORY, SNAPSHOT


class RawCpuUsageSnapshot:

    def __init__(self, timestamp, rows):
        self.timestamp = timestamp
        self.rows = rows


class RawCpuUsage:

    def __init__(self, pu_id, user, system):
        self.pu_id = pu_id
        self.user = user
        self.system = system


class CpuUsageHistory:
    def __init__(self, duration_sec: int, granularity_sec: int, values: list):
        self.duration_sec = duration_sec
        self.granularity_sec = granularity_sec
        self.values = values

    def to_dict(self):
        return self.__dict__


class CpuUsageSnapshot:
    def __init__(self, sample_sec: int, values: list):
        self.sample_sec = sample_sec
        self.values = values

    def to_dict(self):
        return self.__dict__


class WorkloadCpuUsage:
    def __init__(self, history: CpuUsageHistory, snapshot: CpuUsageSnapshot):
        self.history = history
        self.snapshot = snapshot

    def to_dict(self):
        return {
            HISTORY: self.history.to_dict(),
            SNAPSHOT: self.snapshot.to_dict()
        }

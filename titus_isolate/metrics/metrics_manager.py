import os
from threading import Thread

import schedule
from spectator import GlobalRegistry

from titus_isolate.utils import get_logger

registry = GlobalRegistry
log = get_logger()


def override_registry(reg):
    global registry
    registry = reg


class MetricsManager:

    def __init__(self, reporters, reg=registry, report_interval=30, sleep_interval=1):
        self.__reporters = reporters
        self.__reg = reg
        self.__sleep_interval = sleep_interval

        for reporter in self.__reporters:
            reporter.set_registry(self.__reg)

        schedule.every(report_interval).seconds.do(self.__report_metrics)

        self.__worker_thread = Thread(target=self.__schedule_loop)
        self.__worker_thread.daemon = True
        self.__worker_thread.start()

    def __report_metrics(self):
        try:
            tags = self.__get_tags()

            for reporter in self.__reporters:
                reporter.report_metrics(tags)
        except:
            log.exception("Failed to report metrics.")

    @staticmethod
    def __get_tags():
        ec2_instance_id = 'EC2_INSTANCE_ID'

        tags = {}
        if ec2_instance_id in os.environ:
            tags["node"] = os.environ[ec2_instance_id]

        return tags
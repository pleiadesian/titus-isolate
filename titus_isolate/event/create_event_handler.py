from time import sleep

from titus_isolate.config.constants import GET_WORKLOAD_RETRY_INTERVAL_SEC, DEFAULT_GET_WORKLOAD_RETRY_INTERVAL_SEC, \
    GET_WORKLOAD_RETRY_COUNT, DEFAULT_GET_WORKLOAD_RETRY_COUNT
from titus_isolate.event.constants import ACTION, ACTOR, ATTRIBUTES, REQUIRED_LABELS, START
from titus_isolate.event.event_handler import EventHandler
from titus_isolate.event.utils import get_container_name
from titus_isolate.model.utils import get_workload_from_kubernetes
from titus_isolate.utils import get_config_manager


class CreateEventHandler(EventHandler):
    def __init__(self, workload_manager):
        super().__init__(workload_manager)

    def handle(self, event):
        if not self.__relevant(event):
            return

        workload = self.__get_workload(event)

        if workload is None:
            self.handled_event(event, "failed to get workload from kubernetes for event: '{}'".format(event))

        self.handling_event(event, "adding workload: '{}'".format(workload.get_id()))
        self.workload_manager.add_workload(workload)
        self.handled_event(event, "added workload: '{}'".format(workload.get_id()))

    def __relevant(self, event):
        if not event[ACTION] == START:
            self.ignored_event(event, "not a START event")
            return False

        for expected_label in REQUIRED_LABELS:
            if expected_label not in event[ACTOR][ATTRIBUTES]:
                self.ignored_event(event, "container created without expected label: '{}'".format(expected_label))
                return False

        return True

    def __get_workload(self, event):
        config_manager = get_config_manager()
        retry_count = config_manager.get_int(GET_WORKLOAD_RETRY_COUNT, DEFAULT_GET_WORKLOAD_RETRY_COUNT)
        retry_interval = config_manager.get_int(GET_WORKLOAD_RETRY_INTERVAL_SEC, DEFAULT_GET_WORKLOAD_RETRY_INTERVAL_SEC)

        for i in range(retry_count):
            workload = get_workload_from_kubernetes(get_container_name(event))
            if workload is not None:
                return workload

            sleep(retry_interval)

        return None


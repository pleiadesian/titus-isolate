import datetime
import uuid
from queue import Queue
from threading import Thread

from titus_isolate import log
from titus_isolate.metrics.constants import EVENT_LOG_SUCCESS, EVENT_LOG_RETRY, EVENT_LOG_FAILURE
from titus_isolate.metrics.event_log_manager import EventLogManager


class LocalEventLogManager(EventLogManager):

    def __init__(self):
        self.__set_address()
        self.__q = Queue()

        self.__reg = None
        self.__succeeded_msg_count = 0
        self.__retry_msg_count = 0
        self.__failed_msg_count = 0

        self.__processing_thread = Thread(target=self.__process_events)
        self.__processing_thread.start()

    def report_event(self, payload: dict):
        try:
            payload['ts'] = str(datetime.datetime.utcnow())
            event = {
                "uuid": str(uuid.uuid4()),
                "payload": payload
            }
            self.__q.put_nowait(event)
        except:
            self.__failed_msg_count += 1
            log.exception("Failed to report event for payload: {}".format(payload))

    def set_registry(self, registry, tags):
        self.__reg = registry

    def report_metrics(self, tags):
        self.__reg.gauge(EVENT_LOG_SUCCESS, tags).set(self.__succeeded_msg_count)
        self.__reg.gauge(EVENT_LOG_RETRY, tags).set(self.__retry_msg_count)
        self.__reg.gauge(EVENT_LOG_FAILURE, tags).set(self.__failed_msg_count)

    def __process_events(self):
        while True:
            msg = self.__q.get()
            log.debug("Sending event log message: {}".format(msg))

    def __set_address(self):
        self.__address = ''
        log.info("Set keystone address to: None")

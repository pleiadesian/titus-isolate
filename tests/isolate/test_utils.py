import unittest
import uuid

from titus_isolate.isolate.utils import get_thread_ids
from titus_isolate.model.processor.thread import Thread


class TestUtils(unittest.TestCase):

    def test_get_thread_ids(self):
        t_id0 = 42
        thread0 = Thread(t_id0)

        t_id1 = 43
        thread1 = Thread(t_id1)

        workload_id = uuid.uuid4()
        thread0.claim(workload_id)

        thread_ids = get_thread_ids(workload_id, [thread0, thread1])
        self.assertEqual([thread0.get_id()], thread_ids)

import time
import unittest
from job_manager.broker import Broker
from task_manager.worker import Worker


class MyTestCase(unittest.TestCase):
    def setUp(self):
        # start non-blocking queue
        self.broker = Broker()
        self.broker.start()
        # start a worker
        self.workers = []

    def tearDown(self):
        for worker in self.workers:
            worker.quit()
        self.broker.quit()

    def test_message_queue(self):
        # add the worker
        worker = Worker()
        worker.start()
        self.workers.append(worker)
        # send a message to the worker
        self.broker.put_on_queue('Hello')
        # wait for the worker to process the message
        while not worker.working:
            time.sleep(.1)
        self.assertEqual('Hello', worker.message.decode())


if __name__ == '__main__':
    unittest.main()

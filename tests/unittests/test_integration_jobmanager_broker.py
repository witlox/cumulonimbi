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
            worker.join()
        self.broker.quit()
        self.broker.join()

    def test_1_message_1_worker(self):
        # add the worker
        worker = Worker()
        worker.start()
        self.workers.append(worker)

        # send a message to the worker
        self.broker.put_on_queue('Hello')

        # wait for the worker to process the message
        while not len(worker.finished) > 0:
            time.sleep(.1)

        self.assertEqual('Hello', worker.finished[0].decode())

    def test_1_message_2_workers(self):
        # add the workers
        worker1 = Worker()
        worker2 = Worker()
        worker1.start()
        worker2.start()
        self.workers.append(worker1)
        self.workers.append(worker2)

        # send a message to the workers
        self.broker.put_on_queue('Hello')

        # wait for the workers to process the message
        while not len(worker1.finished) + len(worker2.finished) == 1:
            time.sleep(.1)

        finished_work = worker1.finished + worker2.finished
        self.assertTrue('Hello' in finished_work)

    def test_5_messages_1_worker(self):
        # add the worker
        worker = Worker()
        worker.start()
        self.workers.append(worker)
        # send a message to the worker
        self.broker.put_on_queue('Hello1')
        self.broker.put_on_queue('Hello2')
        self.broker.put_on_queue('Hello3')
        self.broker.put_on_queue('Hello4')
        self.broker.put_on_queue('Hello5')
        # wait for the worker to process the message
        while not len(worker.finished) == 5:
            time.sleep(.1)
        self.assertEqual('Hello1', worker.finished[0].decode())
        self.assertEqual('Hello2', worker.finished[1].decode())
        self.assertEqual('Hello3', worker.finished[2].decode())
        self.assertEqual('Hello4', worker.finished[3].decode())
        self.assertEqual('Hello5', worker.finished[4].decode())

    def test_5_messages_2_workers(self):
        # add the workers
        worker1 = Worker()
        worker2 = Worker()
        worker1.start()
        worker2.start()
        self.workers.append(worker1)
        self.workers.append(worker2)

        # send a messages to the workers
        self.broker.put_on_queue('Hello1')
        self.broker.put_on_queue('Hello2')
        self.broker.put_on_queue('Hello3')
        self.broker.put_on_queue('Hello4')
        self.broker.put_on_queue('Hello5')
        # wait for the worker to process the message
        while not len(worker1.finished) + len(worker2.finished) == 5:
            time.sleep(.1)

        finished_work = worker1.finished + worker2.finished

        self.assertTrue('Hello1' in finished_work)
        self.assertTrue('Hello2' in finished_work)
        self.assertTrue('Hello3' in finished_work)
        self.assertTrue('Hello4' in finished_work)
        self.assertTrue('Hello5' in finished_work)

if __name__ == '__main__':
    unittest.main()

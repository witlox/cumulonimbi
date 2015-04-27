import unittest
from task_manager.worker import Worker


class TestRepository(unittest.TestCase):
    def setUp(self):
        self.worker = Worker()
        self.worker.start()

    def tearDown(self):
        self.worker.stop()

    def test_worker_init(self):
        pass


if __name__ == '__main__':
    unittest.main()

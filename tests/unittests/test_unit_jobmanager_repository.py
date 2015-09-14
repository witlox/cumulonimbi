import unittest
import networkx as nx
from job_manager.repository import JobManagerRepository


class TestRepository(unittest.TestCase):
    def test_insert_job(self):
        # Arrange
        job_name = "new job"
        graph = nx.Graph()
        job_id = "123"

        class TestJobManager(object):
            def insert_job(self, job_name, graph):
                return job_id

        repository = JobManagerRepository(TestJobManager())

        # Act
        return_id = repository.insert_job(job_name, graph)

        # Assert
        self.assertEquals(job_id, return_id)

    def test_get_all_jobs(self):
        # Arrange
        expected_result = [{'name': "new job"}]

        class TestJobManager(object):
            def get_jobs(self):
                return expected_result

        repository = JobManagerRepository(TestJobManager())

        # Act
        jobs = repository.get_all_jobs()

        # Assert
        self.assertEquals(1, len(jobs))

    def test_find_one(self):
        # Arrange
        job_id = "1"
        expectedjob = {'id': job_id, 'name': "new job"}

        class TestJobManager(object):
            def get_job(self, job_id):
                return expectedjob

        repository = JobManagerRepository(TestJobManager())

        # Act
        job = repository.get_job(job_id)

        # Assert
        self.assertEquals(expectedjob, job)


if __name__ == '__main__':
    unittest.main()

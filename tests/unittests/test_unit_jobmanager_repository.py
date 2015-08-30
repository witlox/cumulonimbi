from job_manager.repository import JobManagerRepository
from bson import ObjectId
import mock
import unittest
import networkx as nx


class TestRepository(unittest.TestCase):
    @mock.patch('job_manager.repository.MongoClient')
    def test_insert_job(self, mc):
        # Arrange
        repository = JobManagerRepository()
        job_name = "new job"
        graph = nx.Graph()

        # Act
        repository.insert_job(job_name, graph)

        # Assert
        assert repository.jobs.insert.call_count == 1
        assert repository.jobs.insert.call_args == mock.call({'name': job_name, 'graph': graph, 'status': "Received"})

    @mock.patch('job_manager.repository.MongoClient')
    def test_get_all_jobs(self, mc):
        # Arrange
        repository = JobManagerRepository()
        repository.jobs.find.return_value = [{'name': "new job"}]

        # Act
        jobs = repository.get_all_jobs()

        # Assert
        assert (len(jobs) == 1)
        assert repository.jobs.find.call_count == 1
        assert repository.jobs.find.call_args == mock.call()

    @mock.patch('job_manager.repository.MongoClient')
    def test_find_one(self, mc):
        # Arrange
        job_id = ObjectId()
        expectedjob = {'id': str(job_id), 'name': "new job"}
        repository = JobManagerRepository()
        repository.jobs.find_one.return_value = {'_id': job_id, 'name': "new job"}

        # Act
        job = repository.get_job(str(job_id))

        # Assert
        assert (job['id'] == str(job_id))
        assert repository.jobs.find_one.call_count == 1
        assert repository.jobs.find_one.call_args == mock.call({'_id': job_id})


if __name__ == '__main__':
    unittest.main()

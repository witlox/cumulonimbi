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
        task_graph = nx.Graph()

        # Act
        repository.insert_job(job_name, task_graph)

        # Assert
        repository.jobs.insert.assert_called_with({'name': job_name, 'graph': task_graph})

    @mock.patch('job_manager.repository.MongoClient')
    def test_get_all_jobs(self, mc):
        # Arrange
        repository = JobManagerRepository()
        repository.jobs.find.return_value = [{'name': "new job"}]

        # Act
        jobs = repository.get_all_jobs()

        # Assert
        assert(len(jobs) == 1)
        repository.jobs.find.assert_called_once()

    @mock.patch('job_manager.repository.MongoClient')
    def test_find_one(self, mc):
        # Arrange
        job_id = str(ObjectId())
        job = {'_id': job_id, 'name': "new job"}
        repository = JobManagerRepository()
        repository.jobs.find_one.return_value = job

        # Act
        job = repository.get_job(job['_id'])

        # Assert
        assert(job['_id'] == job_id)
        repository.jobs.find.assert_called_once()

if __name__ == '__main__':
    unittest.main()

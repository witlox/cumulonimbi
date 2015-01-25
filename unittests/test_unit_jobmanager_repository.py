__author__ = 'Johannes'

from job_manager.repository import JobManagerRepository
import mock
import unittest


class TestRepository(unittest.TestCase):
    def test_insert_job(self):
        with mock.patch('job_manager.repository.MongoClient') as mc:
            # Arrange
            repository = JobManagerRepository()

            # Act
            repository.insert_job("new job")

            # Assert
            repository.jobs.insert.assert_called_with({'name': "new job"})

    def test_get_all_jobs(self):
        with mock.patch('job_manager.repository.MongoClient') as mc:
            # Arrange
            repository = JobManagerRepository()
            repository.jobs.find.return_value = [{'name': "new job"}]

            # Act
            jobs = repository.get_all_jobs()

            # Assert
            assert(len(jobs) == 1)
            repository.jobs.find.assert_called_once()

    def test_find_one(self):
        with mock.patch('job_manager.repository.MongoClient') as mc:
            # Arrange
            job = {'_id': 123, 'name': "new job"}
            repository = JobManagerRepository()
            repository.jobs.find_one.return_value = job

            # Act
            job = repository.get_job(job['_id'])

            # Assert
            assert(job['_id'] == 123)
            repository.jobs.find.assert_called_once()

if __name__ == '__main__':
    unittest.main()
__author__ = 'Johannes'

from JobManager.Repository import JobManagerRepository

from mock import patch
import unittest


class TestRepository(unittest.TestCase):
    def test_insert_job(self):
        with patch('JobManager.Repository.MongoClient') as mc:
            # Arrange
            instance = mc.return_value
            repository = JobManagerRepository()

            # Act
            repository.insert_job("new job")

            # Assert
            instance.job_manager.jobs.insert.assert_called_with({'name': "new job"})
            self.assertTrue(True)

    def test_get_all_jobs(self):
        with patch('JobManager.Repository.MongoClient') as mc:
            # Arrange
            instance = mc.return_value
            instance.job_manager.jobs.find.return_value = [{'name': "new job"}]
            repository = JobManagerRepository()

            # Act
            jobs = repository.get_all_jobs()

            # Assert
            instance.job_manager.jobs.find.assert_called_once()


if __name__ == '__main__':
    unittest.main()

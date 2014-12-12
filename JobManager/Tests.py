__author__ = 'Johannes'

from JobManager.Repository import JobManagerRepository

from mock import patch
import unittest


class TestRepository(unittest.TestCase):
    def test_job_insert(self):
        # Arrange
        with patch('JobManager.Repository.MongoClient') as mc:
            instance = mc.return_value
            repository = JobManagerRepository()

            # Act
            ret = repository.insert_job("new job")

            # Assert
            instance.insert.assert_called_with({'name': "new job"})


if __name__ == '__main__':
    unittest.main()

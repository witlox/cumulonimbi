__author__ = 'Johannes'

from JobManager.Repository import JobManagerRepository

from mock import patch
import unittest

class TestRepository(unittest.TestCase):

    def test_job_insert(self):
        # Arrange

        with patch('JobManager.Repository.MongoClient') as mc:
            repository = JobManagerRepository()

            #mc.jobs.insert(repository, str)
            mc.jobs.insert(str).return_value = "abc"

            # Act
            ret = repository.insert_job("new job")

            # Assert
            #mc.assert_any_call('jobs.insert', arg={'name':"new job"})
            assert(ret == "abc")




if __name__ == '__main__':
    unittest.main()

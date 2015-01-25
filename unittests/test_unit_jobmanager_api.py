__author__ = 'Johannes'

import unittest
import json

import mock

from job_manager.repository import JobManagerRepository
from job_manager.api import api


class TestRepository(unittest.TestCase):
    def test_insert_job(self):
        # Arrange
        with mock.patch('job_manager.repository.MongoClient') as mc:
            repository = JobManagerRepository()
            api.config['REPOSITORY'] = repository

            job_id = 1
            repository.jobs.insert.return_value = job_id

            self.app = api.test_client()
            job_name = "new job"

            # Act
            rv = self.app.post('/jobs', data=dict(jobname=job_name))

            # Assert
            body = rv.data.decode(rv.charset)
            self.assertEqual({'job_id': job_id}, json.loads(body))
            repository.jobs.insert.assert_called_with({'name': "new job"})

    def test_get_jobs(self):
        # Arrange
        with mock.patch('job_manager.repository.MongoClient') as mc:
            repository = JobManagerRepository()
            api.config['REPOSITORY'] = repository

            expected_result = [{'name': "new job"}]
            repository.jobs.find.return_value = expected_result

            self.app = api.test_client()

            # Act
            rv = self.app.get('/jobs')

            # Assert
            body = rv.data.decode(rv.charset)
            self.assertEquals(expected_result, json.loads(body))
            repository.jobs.find.assert_called_once()

    def test_get_job(self):
        # Arrange
        with mock.patch('job_manager.repository.MongoClient') as mc:
            repository = JobManagerRepository()
            api.config['REPOSITORY'] = repository

            expected_result = [{'name': "new job"}]
            repository.jobs.find_one.return_value = expected_result

            self.app = api.test_client()

            # Act
            rv = self.app.get('/jobs/1')

            # Assert
            body = rv.data.decode(rv.charset)
            self.assertEquals(expected_result, json.loads(body))
            repository.jobs.find.assert_called_once()

if __name__ == '__main__':
    unittest.main()
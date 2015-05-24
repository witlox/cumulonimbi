__author__ = 'Johannes'

import unittest
import json

import mock
from bson import ObjectId
from job_manager.repository import JobManagerRepository
from job_manager.api import api
import networkx as nx
from networkx.readwrite import json_graph


class TestRepository(unittest.TestCase):

    def setUp(self):
        with mock.patch('job_manager.repository.MongoClient') as mc:
            self.repository = JobManagerRepository()
            api.config['REPOSITORY'] = self.repository

    def test_insert_job(self):
        # Arrange
        job_id = "1"
        self.repository.jobs.insert.return_value = job_id

        self.app = api.test_client()
        job_name = "new job"
        g = nx.Graph()

        # Act
        data = {'job_name': job_name, 'graph': json_graph.node_link_data(g)}
        rv = self.app.post('/jobs', data=json.dumps(data))

        # Assert
        body = rv.data.decode(rv.charset)
        self.assertEqual({'job_id': job_id}, json.loads(body))
        self.repository.jobs.insert.assert_called_with({'name': job_name, 'graph': json_graph.node_link_data(g)})

    def test_get_jobs(self):
        # Arrange
        expected_result = [{'name': "new job"}]
        self.repository.jobs.find.return_value = expected_result

        self.app = api.test_client()

        # Act
        rv = self.app.get('/jobs')

        # Assert
        body = rv.data.decode(rv.charset)
        self.assertEquals(expected_result, json.loads(body))
        self.repository.jobs.find.assert_called_once()

    def test_get_job(self):
        # Arrange
        expected_result = [{'name': "new job"}]
        job_id = str(ObjectId())
        self.repository.jobs.find_one.return_value = expected_result

        self.app = api.test_client()

        # Act
        rv = self.app.get('/jobs/' + job_id)

        # Assert
        body = rv.data.decode(rv.charset)
        self.assertEquals(expected_result, json.loads(body))
        self.repository.jobs.find.assert_called_once()

if __name__ == '__main__':
    unittest.main()

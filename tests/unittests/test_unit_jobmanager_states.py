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

    def test_job_received(self):
        # Arrange
        excpected_job_id = "1"
        self.repository.jobs.insert.return_value = excpected_job_id

        self.app = api.test_client()
        job_name = "new job"
        g = nx.Graph()

        # Act
        data = {'job_name': job_name, 'graph': json_graph.node_link_data(g)}
        rv = self.app.post('/jobs', data=json.dumps(data))

        # Assert
        job_id = json.loads(rv.data.decode(rv.charset))["job_id"]
        self.assertEqual(excpected_job_id, job_id)
        self.repository.jobs.insert.assert_called_with({'name': job_name, 'graph': json_graph.node_link_data(g), 'status': 'RCVD'})

    def test_job_set_accepted(self):
        # Arrange
        excpected_job_id = "1"
        self.repository.jobs.insert.return_value = excpected_job_id

        self.app = api.test_client()
        job_name = "new job"
        g = nx.Graph()

        # Act
        data = {'job_name': job_name, 'graph': json_graph.node_link_data(g)}
        rv = self.app.post('/jobs', data=json.dumps(data))
        rv2 = self.app.put('/jobs/' + excpected_job_id + '/status', data=json.dumps({'status': 'accepted'}))

        # Assert
        job_update = json.loads(rv2.data.decode(rv.charset))

if __name__ == '__main__':
    unittest.main()

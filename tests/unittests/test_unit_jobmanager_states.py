import unittest
from flask import json

import networkx as nx
from networkx.readwrite import json_graph

from job_manager.repository import JobManagerRepository
from job_manager.api import api


class TestRepository(unittest.TestCase):
    def test_job_received(self):
        # Arrange
        expected_job_id = "1"

        class TestJobManager(object):
            def insert_job(self, job_name, graph):
                return expected_job_id

        api.config['REPOSITORY'] = JobManagerRepository(TestJobManager())
        self.app = api.test_client()

        job_name = "new job"
        g = nx.Graph()

        # Act
        data = {'job_name': job_name, 'graph': json_graph.node_link_data(g)}
        rv = self.app.post('/jobs', data=json.dumps(data))

        # Assert
        job_id = json.loads(rv.data.decode(rv.charset))["job_id"]
        self.assertEqual(expected_job_id, job_id)

    def test_job_set_accepted(self):
        # Arrange
        job_id = "1"
        job_name = "new job"
        g = nx.Graph()
        expected_result = {'name': job_name, 'graph': json_graph.node_link_data(g), 'status': "Accepted", 'id': job_id}

        class TestJobManager(object):
            def __init__(self):
                self.job = None

            def get_job(self, job_id):
                return self.job

            def insert_job(self, job_name, graph):
                self.job = {'name': job_name, 'graph': graph, 'status': "Received", "id": job_id}
                return job_id

            def update_job(self, job_id, job):
                self.job['status'] = job['status']

        api.config['REPOSITORY'] = JobManagerRepository(TestJobManager())
        self.app = api.test_client()

        # Act
        data = {'job_name': job_name, 'graph': json_graph.node_link_data(g)}
        rv = self.app.post('/jobs', data=json.dumps(data))
        rv2 = self.app.put('/jobs/' + job_id + '/status', data=json.dumps({'status': 'Accepted'}))
        rv3 = self.app.get('/jobs/' + job_id)

        # Assert
        final_job = json.loads(rv3.data.decode(rv.charset))

        self.assertEqual(expected_result, final_job)

if __name__ == '__main__':
    unittest.main()

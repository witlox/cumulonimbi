import unittest
from flask import json
import networkx as nx

from networkx.readwrite import json_graph
from job_manager.repository import JobManagerRepository
from job_manager.api import api


class TestRepository(unittest.TestCase):
    def test_insert_job(self):
        # Arrange
        job_id = "1"

        class TestJobManager(object):
            def insert_job(self, a, b):
                return job_id

        api.config['REPOSITORY'] = JobManagerRepository(TestJobManager())
        self.app = api.test_client()

        job_name = "new job"
        g = nx.Graph()

        # Act
        data = {'job_name': job_name, 'graph': json_graph.node_link_data(g)}
        rv = self.app.post('/jobs', data=json.dumps(data))

        # Assert
        body = rv.data.decode(rv.charset)
        self.assertEqual({'job_id': job_id}, json.loads(body))

    def test_get_jobs(self):
        # Arrange
        expected_result = [{'name': "new job"}]

        class TestJobManager(object):
            def get_jobs(self):
                return expected_result

        api.config['REPOSITORY'] = JobManagerRepository(TestJobManager())
        self.app = api.test_client()

        # Act
        rv = self.app.get('/jobs')

        # Assert
        body = rv.data.decode(rv.charset)
        self.assertEquals(expected_result, json.loads(body))

    def test_get_job(self):
        # Arrange
        job_id = "1"
        expected_result = dict([{'name': "new job", "id": job_id}])

        class TestJobManager(object):
            def get_job(self, job_id):
                return expected_result

        api.config['REPOSITORY'] = JobManagerRepository(TestJobManager())
        self.app = api.test_client()

        # Act
        rv = self.app.get('/jobs/' + job_id)

        # Assert
        body = rv.data.decode(rv.charset)
        self.assertEquals(expected_result, json.loads(body))


if __name__ == '__main__':
    unittest.main()

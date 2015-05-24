from flask import json
from job_manager.repository import JobManagerRepository
from job_manager.api import api
import unittest
import networkx as nx
from networkx.readwrite import json_graph


class JobManagerIntegrationTests(unittest.TestCase):
    def test_jm(self):
        jm = JobManagerRepository("jobs")
        jm.delete_all_jobs()

        jobs = jm.get_all_jobs()
        assert (len(jobs) == 0)

        id_A = jm.insert_job("A", json_graph.node_link_data(nx.Graph()))
        id_B = jm.insert_job("B", json_graph.node_link_data(nx.Graph()))

        jobs = jm.get_all_jobs()
        assert (len(jobs) == 2)

    def test_api(self):
        api.config['REPOSITORY'] = JobManagerRepository("jobs")
        app = api.test_client()
        app.delete('/jobs')

        rv = app.get('/jobs')
        body = rv.data.decode(rv.charset)
        jobs = json.loads(body)
        assert (len(jobs) == 0)

        graph = json_graph.node_link_data(nx.Graph())

        data_A = {'job_name': "A", 'graph': graph}
        id_A = app.post('/jobs', data=json.dumps(data_A))

        data_B = {'job_name': "B", 'graph': graph}
        id_B = app.post('/jobs', data=json.dumps(data_B))

        rv = app.get('/jobs')
        body = rv.data.decode(rv.charset)
        jobs = json.loads(body)
        assert (len(jobs) == 2)

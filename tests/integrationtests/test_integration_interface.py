import json
import unittest
import requests
import networkx as nx
from networkx.readwrite import json_graph
import flask

class InterfaceIntegrationTests(unittest.TestCase):

    jobs_url = "http://127.0.0.1:5000/jobs"

    def setUp(self):
        requests.delete(self.jobs_url)

    def test_get_jobs(self):
        r = requests.get(self.jobs_url)
        jobs = r.json()

        assert(len(jobs) == 0)

    def test_add_job(self):
        data = {'job_name': 'api_job', 'graph': json_graph.node_link_data(nx.Graph())}
        r = requests.post(self.jobs_url, data=json.dumps(data))
        job = r.json()

        r = requests.get(self.jobs_url)
        jobs = r.json()

        assert(len(jobs) == 1)

    def test_get_specific_job(self):
        data = {'job_name': 'api_job', 'graph': json_graph.node_link_data(nx.Graph())}
        r = requests.post(self.jobs_url, data=json.dumps(data))
        job = r.json()

        r = requests.get(self.jobs_url + '/' + job['job_id'])
        job = r.json()

        assert(job['name'] == data['job_name'])

    def test_get_all_tasks(self):
        g = nx.Graph()
        t1 = "hello"
        t2 = "world"
        t3 = "!"
        g.add_edge(t1, t2)
        g.add_edge(t2, t3)

        data = {'job_name': 'api_job', 'graph': json_graph.node_link_data(g)}
        r = requests.post(self.jobs_url, data=json.dumps(data))
        assert(r.status_code == 200)

        # get all jobs
        r = requests.get(self.jobs_url)
        jobs = r.json()
        tasks = []
        for job in jobs:
            for n in job['graph']['nodes']:
                tasks.append(n)
        assert(len(tasks) == 3)

import unittest
import requests
import networkx as nx


class InterfaceIntegrationTests(unittest.TestCase):

    jobs_url = "http://127.0.0.1:5000/jobs"

    def setUp(self):
        requests.delete(self.jobs_url)

    def test_get_jobs(self):
        r = requests.get(self.jobs_url)
        jobs = r.json()

        assert(len(jobs) == 0)

    def test_add_job(self):
        data = {'jobname': 'api_job', 'task_graph': nx.node_link_data(nx.Graph())}
        r = requests.post(self.jobs_url, data)
        job = r.json()

        r = requests.get(self.jobs_url)
        jobs = r.json()

        assert(len(jobs) == 1)

    def test_update_job_failed(self):
        r = requests.put(self.jobs_url + '/123')
        assert(r.status_code == 500)

    def test_update_job_success(self):
        data = {'jobname': 'api_job', 'task_graph': nx.node_link_data(nx.Graph())}
        r = requests.post(self.jobs_url, data)
        job = r.json()

        r = requests.put(self.jobs_url + '/' + job['job_id'])
        assert(r.status_code == 200)

    def test_get_specific_job(self):
        data = {'jobname': 'api_job', 'task_graph': nx.node_link_data(nx.Graph())}
        r = requests.post(self.jobs_url, data)
        job = r.json()

        r = requests.get(self.jobs_url + '/' + job['job_id'])
        job = r.json()

        assert(job['name'] == data['jobname'])

    def test_get_all_tasks(self):
        g = nx.Graph()
        t1 = "hello"
        t2 = "world"
        t3 = "!"
        g.add_edge(t1, t2)
        g.add_edge(t2, t3)

        data = {'jobname': 'api_job', 'task_graph': nx.node_link_data(g)}
        r = requests.post(self.jobs_url, data)
        assert(r.status_code == 200)

        # get all jobs
        r = requests.get(self.jobs_url)
        jobs = r.json()
        tasks = []
        for job in jobs:
            tasks.append(nx.dfs_edges(job['task_graph']))
        assert(len(tasks) == 3)

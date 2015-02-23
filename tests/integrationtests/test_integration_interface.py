__author__ = 'Johannes'

import unittest
import requests
import json

class InterfaceIntegrationTests(unittest.TestCase):
    def test_get_jobs(self):
        jobs_url = "http://127.0.0.1:5000/jobs"
        requests.delete(jobs_url)

        r = requests.get(jobs_url)
        jobs = r.json()

        assert(len(jobs) == 0)

    def test_add_job(self):
        jobs_url = "http://127.0.0.1:5000/jobs"
        requests.delete(jobs_url)

        data = {'jobname': 'api_job'}
        r = requests.post(jobs_url, data)
        job = r.json()

        r = requests.get(jobs_url + '/' + job['job_id'])
        job = r.json()

        assert(job['name'] == data['jobname'])

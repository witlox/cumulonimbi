__author__ = 'Johannes'

import unittest
import requests


class InterfaceIntegrationTests(unittest.TestCase):
    def test_get_jobs(self):
        get_jobs_url = "http://localhost:5000/jobs"
        r = requests.get(get_jobs_url)

        print r.json()

    def test_add_job(self):
        post_job_url = "http://localhost:5000/jobs"
        data = {'jobname': 'api_job'}
        r = requests.post(post_job_url, data)

        print r.json()

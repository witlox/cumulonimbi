__author__ = 'Johannes'

import unittest
import requests


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

        r = requests.get(jobs_url)
        jobs = r.json()

        assert(len(jobs) == 1)

    def test_update_job_failed(self):
        jobs_url = "http://127.0.0.1:5000/jobs"
        requests.delete(jobs_url)

        r = requests.put(jobs_url + '/123')
        assert(r.status_code == 500)

    def test_update_job_success(self):
        jobs_url = "http://127.0.0.1:5000/jobs"
        requests.delete(jobs_url)

        data = {'jobname': 'api_job'}
        r = requests.post(jobs_url, data)
        job = r.json()

        r = requests.put(jobs_url + '/' + job['job_id'])
        assert(r.status_code == 200)

    def test_get_specific_job(self):
        jobs_url = "http://127.0.0.1:5000/jobs"
        requests.delete(jobs_url)

        data = {'jobname': 'api_job'}
        r = requests.post(jobs_url, data)
        job = r.json()

        r = requests.get(jobs_url + '/' + job['job_id'])
        job = r.json()

        assert(job['name'] == data['jobname'])

from flask import json

__author__ = 'Johannes'

from job_manager.repository import JobManagerRepository
from job_manager.api import api
import unittest


class JobManagerIntegrationTests(unittest.TestCase):

        def test_jm(self):
            jm = JobManagerRepository("test_jobs")
            jm.delete_all_jobs()

            jobs = jm.get_all_jobs()
            assert(len(jobs) == 0)

            id_A = jm.insert_job("A")
            id_B = jm.insert_job("B")

            jobs = jm.get_all_jobs()
            assert(len(jobs) == 2)

        def test_api(self):
            api.config['REPOSITORY'] = JobManagerRepository("test_jobs")
            app = api.test_client()
            app.delete('/jobs')

            rv = app.get('/jobs')
            body = rv.data.decode(rv.charset)
            jobs = json.loads(body)
            assert(len(jobs) == 0)

            id_A = app.post('/jobs', data=dict(jobname="A"))
            id_A = app.post('/jobs', data=dict(jobname="B"))

            rv = app.get('/jobs')
            body = rv.data.decode(rv.charset)
            jobs = json.loads(body)
            assert(len(jobs) == 2)
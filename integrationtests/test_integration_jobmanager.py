from flask import json

__author__ = 'Johannes'

from job_manager.repository import JobManagerRepository
from job_manager.api import api
import unittest


class JobManagerIntegrationTests(unittest.TestCase):
        def test_jm(self):
            jm = JobManagerRepository("test_jobs")

            jobs = jm.get_all_jobs()
            for job in jobs:
                jm.delete_job(job["_id"])

            jobs = jm.get_all_jobs()
            assert(len(jobs) == 0)

            id_A = jm.insert_job("A")
            id_B = jm.insert_job("B")

            jobs = jm.get_all_jobs()
            assert(len(jobs) == 2)

        def test_api(self):
            api.repository = JobManagerRepository("test_jobs")
            app = api.test_client()

            rv = app.get('/jobs')
            jobs = json.loads(rv.data)

            for job in jobs:
                id = job["_id"]["$oid"]
                rv = app.delete('/jobs/' + str(id))

            rv = app.get('/jobs')
            jobs = json.loads(rv.data)
            assert(len(jobs) == 0)

            id_A = app.post('/jobs', data=dict(jobname="A"))
            id_A = app.post('/jobs', data=dict(jobname="B"))

            rv = app.get('/jobs')
            jobs = json.loads(rv.data)
            assert(len(jobs) == 2)

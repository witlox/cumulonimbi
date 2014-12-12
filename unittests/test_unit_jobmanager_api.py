__author__ = 'Johannes'

import unittest
from bson.json_util import dumps
from job_manager import api
from flask import Response


class MyRepository():
    def __init__(self):
        self.jobs = [
            {'name': "first job"},
            {'name': "second job"},
        ]

    def get_all_jobs(self):
        return self.jobs


class TestRepository(unittest.TestCase):
    def setUp(self):
        self.repository = MyRepository()
        api.repository = self.repository
        self.app = api.api.test_client()

    def test_insert_job(self):
        # Arrange
        jobname = "new job"

        # Act
        rv = self.app.post('/jobs', data=dict(jobname=jobname))

        # Assert


    def test_get_jobs(self):
        # Arrange
        expected = Response(dumps(self.repository.jobs), mimetype='application/json')

        # Act
        rv = self.app.get('/jobs')

        # Assert
        assert (expected.data == rv.data)

    def test_get_job(self):
        # Arrange
        expected = Response(dumps(self.repository.jobs), mimetype='application/json')

        # Act
        rv = self.app.get('/jobs')

        # Assert
        assert (expected.data == rv.data)
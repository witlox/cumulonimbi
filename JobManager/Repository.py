__author__ = 'Johannes'

from pymongo import MongoClient


class JobManagerRepository():
    def __init__(self):
        self.client = MongoClient('mongodbhost.cloudapp.net', 27017)
        self.jobs = self.client.job_manager.jobs

    def get_all_jobs(self):
        all_jobs = []
        jobs_cursor = self.jobs.find()
        for job in jobs_cursor:
            all_jobs.append(job)
        return all_jobs

    def insert_job(self, job_name):
        job = {'name':job_name}
        return self.jobs.insert(job)
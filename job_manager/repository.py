__author__ = 'Johannes'

from pymongo import MongoClient


# noinspection PyUnresolvedReferences
class JobManagerRepository():
    def __init__(self, collection=None):
        if collection is None:
            collection = "jobs"
        self.client = MongoClient('127.0.0.1', 27017)
        self.jobs = self.client.job_manager[collection]

    def get_all_jobs(self):
        all_jobs = []
        jobs_cursor = self.jobs.find()
        for job in jobs_cursor:
            all_jobs.append(job)
        return all_jobs

    def insert_job(self, job_name):
        job_id = self.jobs.insert({'name': job_name})
        return job_id

    def get_job(self, job_id):
        job = self.jobs.find_one({"_id": job_id})
        return job

    def delete_job(self, job_id):
        return self.jobs.remove({"_id": ObjectId(job_id)})

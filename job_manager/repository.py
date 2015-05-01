import logging
from pymongo.errors import ConnectionFailure
from pymongo import MongoClient
from bson import ObjectId

class JobManagerRepository():
    def __init__(self, collection=None):
        if collection is None:
            collection = "jobs"

        try:
            self.client = MongoClient('127.0.0.1', 27017)
        except ConnectionFailure(str):
            logging.error("Cannot connect with the MongoDB server: " + str)
            raise

        self.jobs = self.client.job_manager[collection]

    def get_all_jobs(self):
        all_jobs = []
        jobs_cursor = self.jobs.find()
        for job in jobs_cursor:
            all_jobs.append(job)
        return all_jobs

    def insert_job(self, job_name, task_graph):
        job_id = str(self.jobs.insert({'name': job_name, 'graph': task_graph}))
        return job_id

    def update_job(self, job_id, status):
        self.jobs.update({"_id": ObjectId(job_id)}, {"status": status})

    def get_job(self, job_id):
        job = self.jobs.find_one({"_id": ObjectId(job_id)})
        return job

    def delete_job(self, job_id):
        return self.jobs.remove({"_id": ObjectId(job_id)})

    def delete_all_jobs(self):
        return self.jobs.remove({})

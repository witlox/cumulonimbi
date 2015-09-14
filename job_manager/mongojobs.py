import logging
from bson import ObjectId
from pymongo import MongoClient
from pymongo.cursor import Cursor
from pymongo.errors import ConnectionFailure


def fix_job_id(job):
    job_id_object = job.pop("_id", None)
    if job_id_object is None:
        return job

    job["id"] = str(job_id_object)
    return job


class MongoJobmanager(object):
    def __init__(self, host, collection="jobs"):
        self.host = host
        self.collection = collection

    def get_mongo_client(self):
        client = MongoClient(host=self.host)
        try:
            client.admin.command('ping')
            return client.job_manager[self.collection]
        except ConnectionFailure(str):
            logging.error("Cannot connect with the MongoDB server: " + str)
            raise

    def get_jobs(self):
        all_jobs = []
        jobs_cursor = self.get_mongo_client().find()
        for job in jobs_cursor:
            all_jobs.append(fix_job_id(job))
        if type(jobs_cursor) is Cursor:
            jobs_cursor.close()
        return all_jobs

    def insert_job(self, job_name, graph):
        return str(self.get_mongo_client().insert({'name': job_name, 'graph': graph, 'status': "Received"}))

    def get_job(self, job_id):
        return self.get_mongo_client().find_one({"_id": ObjectId(job_id)})

    def update_job(self, job_id, job):
        self.get_mongo_client().update({"_id": ObjectId(job_id)}, job)

    def delete_job(self, job_id):
        self.get_mongo_client().remove({"_id": ObjectId(job_id)})

    def delete_all_jobs(self):
        self.get_mongo_client().remove({})

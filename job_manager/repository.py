import logging
from TransitionError import TransitionError
from StatusUnknownError import StatusUnknownError
from pymongo.errors import ConnectionFailure
from pymongo import MongoClient
from bson import ObjectId
import settings


def fix_job_id(job):
    job_id_object = job.pop("_id", None)
    if job_id_object is None:
        return job

    job["id"] = str(job_id_object)
    return job


class JobManagerRepository:
    def __init__(self, collection=None):
        if collection is None:
            collection = "jobs"

        self.settings = settings.Settings()

        try:
            self.client = MongoClient(host=self.settings.job_manager_mongo_connect_host,
                                      port=self.settings.job_manager_mongo_client_port,
                                      socketKeepAlive=True,
                                      socketTimeoutMS=1000,
                                      connectTimeMS=1000)
        except ConnectionFailure(str):
            logging.error("Cannot connect with the MongoDB server: " + str)
            raise

        self.jobs = self.client.job_manager[collection]
        self.states_from = {
            'Received': ["Rejected", "Accepted"],
            'Rejected': [],
            'Accepted': ["Stale", "Running"],
            'Running': ["Stale", "Failed", "Done"],
            'Done': []
        }

    def get_all_jobs(self):
        all_jobs = []
        jobs_cursor = self.jobs.find()
        for job in jobs_cursor:
            all_jobs.append(fix_job_id(job))
        return all_jobs

    def insert_job(self, job_name, graph):
        job_id = str(self.jobs.insert({'name': job_name, 'graph': graph, 'status': "Received"}))
        return job_id

    def update_job_status(self, job_id, status):
        job = self.jobs.find_one({"_id": ObjectId(job_id)})
        if job["status"] not in self.states_from.keys():
            raise StatusUnknownError(job["status"])
        if status not in self.states_from[job["status"]]:
            raise TransitionError(job["status"], status)

        job["status"] = status
        self.jobs.update({"_id": ObjectId(job_id)}, job)

    def update_job_machine(self, job_id, machine):
        job = self.jobs.find_one({"_id": ObjectId(job_id)})
        job["machine"] = machine
        self.jobs.update({"_id": ObjectId(job_id)}, job)

    def get_job(self, job_id):
        job = self.jobs.find_one({"_id": ObjectId(job_id)})
        return fix_job_id(job)

    def delete_job(self, job_id):
        return self.jobs.remove({"_id": ObjectId(job_id)})

    def delete_all_jobs(self):
        return self.jobs.remove({})

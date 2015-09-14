from TransitionError import TransitionError
from StatusUnknownError import StatusUnknownError
import settings


class JobManagerRepository:
    def __init__(self, store):
        self.settings = settings.Settings()
        self.states_from = {
            'Received': ["Rejected", "Accepted"],
            'Rejected': [],
            'Accepted': ["Stale", "Running"],
            'Running': ["Stale", "Failed", "Done"],
            'Done': []
        }
        self.store = store

    def get_all_jobs(self):
        return self.store.get_jobs()

    def insert_job(self, job_name, graph):
        return self.store.insert_job(job_name, graph)

    def update_job_status(self, job_id, status):
        job = self.store.get_job(job_id)
        if job["status"] not in self.states_from.keys():
            raise StatusUnknownError(job["status"])
        if status not in self.states_from[job["status"]]:
            raise TransitionError(job["status"], status)

        job["status"] = status
        self.store.update_job(job_id, job)

    def update_job_machine(self, job_id, machine):
        job = self.store.get_job(job_id)
        job["machine"] = machine
        self.store.update_job(job_id, job)

    def get_job(self, job_id):
        return self.store.get_job(job_id)

    def delete_job(self, job_id):
        return self.store.delete_job(job_id)

    def delete_all_jobs(self):
        return self.store.delete_all_jobs()

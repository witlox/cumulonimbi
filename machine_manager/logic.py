class MachineManagerLogic(object):
    def __init__(self):
        self.jobs = []

    def check_machines(self):
        pass

    def job_added(self, job_id):
        self.jobs.append(job_id)

    def job_removed(self, job_id):
        self.jobs.remove(job_id)
from base64 import b64encode
import logging
from threading import Thread, Event
from time import sleep
from flask import json
from requests import Session
import requests


def update_status(status, user_id, machine_id):
    cagaas_base_url = 'http://cagaas.nl/'
    cagaas_status_url = 'api/VirtualMachines/{0}/status'
    s = Session()
    s.headers.update({'Authorization': 'Basic ' + b64encode(user_id)})
    data = {u'': status}
    full_url = cagaas_base_url + cagaas_status_url.replace('{0}', machine_id)
    r = s.put(full_url, data=data)
    if r.status_code != 200:
        raise Exception("Could not update status")


def get_jobs():
    r = requests.get("http://docker-cluster.cloudapp.net:5000/jobs")
    if r.status_code != 200:
        raise Exception("Could not get jobs")
    return json.loads(r.content)


def get_new_job(machine_id):
    jobs = get_jobs()
    for job in jobs:
        if job["status"] == u'Received' and "machine" in job and job["machine"] == machine_id:
            return job
    return None


def accept_job(job):
    requests.put("http://docker-cluster.cloudapp.net:5000/jobs/" + job['id'] + "/status", json.dumps({u'status': 'Accepted'}))


def working_on_job(job):
    requests.put("http://docker-cluster.cloudapp.net:5000/jobs/" + job['id'] + "/status", json.dumps({u'status': 'Running'}))


def finish_job(job):
    requests.put("http://docker-cluster.cloudapp.net:5000/jobs/" + job['id'] + "/status", json.dumps({u'status': 'Done'}))


class Machine(Thread):
    def __init__(self, machine):
        Thread.__init__(self)
        self._quit = Event()
        self.daemon = True
        self.log = logging.getLogger(__name__)
        self.info = machine

    def run(self):
        update_status('Idle', self.info['UserId'], self.info['MachineId'])

        # dislike of unstoppable threads
        while not self._quit.is_set():
            self.log.info(self.info['Name'] + " getting new job from api")
            job = get_new_job(self.info["MachineId"])
            if job:
                accept_job(job)
                sleep(3)
                working_on_job(job)
                sleep(10)
                finish_job(job)

            sleep(10)

    def quit(self):
        self.log.info(self.info['Name'] + " is going down!")
        update_status('Removed', self.info['UserId'], self.info['MachineId'])
        self._quit.set()

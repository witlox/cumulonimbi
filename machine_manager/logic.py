from base64 import b64encode
from flask import json
import logging
import random
import requests
import settings


def get_live_machines(user_id):
    cagaas_base_url = 'http://cagaas.nl/api/VirtualMachines'
    s = requests.Session()
    s.headers.update({'Authorization': 'Basic ' + b64encode(user_id)})
    r = s.get(cagaas_base_url)
    if r.status_code != 200:
        raise Exception("Could not update status")
    machines = json.loads(r.content)
    return [x for x in machines if x["Status"] != 'Removed']


def get_idle_machines(user_id):
    live_machines = get_live_machines(user_id)
    return [x for x in live_machines if x["Status"] == 'Idle']


def get_jobs():
    r = requests.get('http://docker-cluster.cloudapp.net:5000/jobs')
    if r.status_code != 200:
        logging.error("Could not get jobs: " + str(r))
        raise Exception("Could not get jobs.")
    return json.loads(r.content)


def get_unassigned_jobs():
    all_jobs = get_jobs()
    return [job for job in all_jobs if "machine" not in job]


def assign_job_to_machine(job_id, machine_id):
    logging.info("Assigning job with id: " + job_id + " to machine with id: " + machine_id)
    r = requests.put('http://docker-cluster.cloudapp.net:5000/jobs/' + job_id + '/machine',
                     json.dumps({"machine": machine_id}))
    if r.status_code != 200:
        logging.error("Could not assign job to machine: " + str(r))
        raise Exception("Could not assign job to machine")


def start_new_machine(user_id, machine_name):
    logging.info("Creating machine with machine name: " + machine_name)
    cagaas_base_url = 'http://cagaas.nl/api/VirtualMachines'
    s = requests.Session()
    s.headers.update({
        'Authorization': 'Basic ' + b64encode(user_id),
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })
    r = s.post(cagaas_base_url, json.dumps({
        'Provider': 'Grid-Simulated',
        'Name': machine_name
    }))
    if r.status_code != 201:
        logging.error("Could not create new machine" + str(r))
        raise Exception("Could not create new machine")
    logging.info("Created machine:" + str(json.loads(r.content)))


class MachineManagerLogic(object):
    def __init__(self):
        self.settings = settings.Settings()

    def check_machines(self):
        idle_machines = get_idle_machines(self.settings.cagaas_super_user)
        if idle_machines:
            logging.info("Idle machines: " + str(idle_machines))

            # get jobs without machine
            jobs = get_unassigned_jobs()

            # for each job assign idle machine (till no machines left)
            for job in jobs:
                if idle_machines:
                    random_machine = random.choice(idle_machines)
                    assign_job_to_machine(job["id"], random_machine["MachineId"])
                    idle_machines.remove(random_machine)

    def job_added(self, job_id):
        idle_machines = get_idle_machines(self.settings.cagaas_super_user)
        if idle_machines:
            target_machine = random.choice(idle_machines)
            assign_job_to_machine(job_id, target_machine["MachineId"])
        else:
            start_new_machine(self.settings.cagaas_super_user, "Machine_for_" + job_id)

    def job_removed(self, job_id):
        pass

    def job_assigned(self, job_id, machine_id):
        pass

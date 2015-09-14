from base64 import b64encode
from time import sleep, time
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


def shutdown_machine(user_id, machine_id):
    logging.info("Shutting down machine: " + machine_id)
    cagaas_base_url = 'http://cagaas.nl/api/VirtualMachines'
    s = requests.Session()
    s.headers.update({
        'Authorization': 'Basic ' + b64encode(user_id),
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })
    r = s.delete(cagaas_base_url + '/' + machine_id)
    if r.status_code != 204:
        logging.error("Could not delete machine " + str(r))
        raise Exception("Could not delete machine " + machine_id)
    logging.info("Shut down machine:" + machine_id)


class MachineManagerLogic(object):
    def __init__(self):
        self.settings = settings.Settings()

    def check_machines(self):
        idle_machines = get_idle_machines(self.settings.cagaas_super_user)
        logging.info("Idle machines before: " + str(idle_machines))
        unassigned_jobs = get_unassigned_jobs()
        logging.info("Unassigned jobs: " + str(unassigned_jobs))

        missing_machines = len(unassigned_jobs) - len(idle_machines)
        logging.info("Amount of missing machines: " + str(missing_machines))

        while missing_machines < 0:
            to_shutdown = idle_machines.pop()
            shutdown_machine(self.settings.cagaas_super_user, to_shutdown["MachineId"])
            missing_machines += 1

        while missing_machines > 0:
            start_new_machine(self.settings.cagaas_super_user, "NewMachine" + str(time()))
            missing_machines -= 1

        sleep(10)  # let them start/get removed
        idle_machines = get_idle_machines(self.settings.cagaas_super_user)
        logging.info("Idle machines after: " + str(idle_machines))

        # for each job assign idle machine (till no machines left)
        for job in unassigned_jobs:
            if idle_machines:
                random_machine = random.choice(idle_machines)
                logging.info("Assigning job: " + job["id"] + " to machine: " + random_machine["MachineId"])
                assign_job_to_machine(job["id"], random_machine["MachineId"])
                idle_machines.remove(random_machine)

    def job_added(self, job_id):
        pass

    def job_removed(self, job_id):
        pass

    def job_assigned(self, job_id, machine_id):
        pass

from base64 import b64encode
import logging
from flask import json
from requests import Session
import settings


def get_live_machines(user_id):
    cagaas_base_url = 'http://cagaas.nl/api/VirtualMachines'
    s = Session()
    s.headers.update({'Authorization': 'Basic ' + b64encode(user_id)})
    r = s.get(cagaas_base_url)
    if r.status_code != 200:
        raise Exception("Could not update status")
    machines = json.loads(r.content)
    return [x for x in machines if x["Status"] != 'Removed']


class MachineManagerLogic(object):
    def __init__(self):
        self.settings = settings.Settings()

    def check_machines(self):
        # check if any machine are idle
        machines = get_live_machines(self.settings.cagaas_super_user)
        logging.info("Machines: " + str(machines))

        # keep track of how long they have been idle, remove if too long
        pass

    def job_added(self, job_id):
        # check if any machine idle

        # assign job to machine
        pass

    def job_removed(self, job_id):
        pass

    def job_assigned(self, job_id, machine_id):
        pass

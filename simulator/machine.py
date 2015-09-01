from base64 import b64encode
from threading import Thread, Event
from time import sleep
from requests import Session


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


class Machine(Thread):
    def __init__(self, machine):
        Thread.__init__(self)
        self._quit = Event()
        self.daemon = True

        self.info = machine

    def run(self):
        update_status('Running', self.info['UserId'], self.info['MachineId'])

        # dislike of unstoppable threads
        while not self._quit.is_set():
            print self.info['Name'] + " is still alive..."
            sleep(10)

    def quit(self):
        print self.info['Name'] + " is going down!"
        update_status('Removed', self.info['UserId'], self.info['MachineId'])
        self._quit.set()

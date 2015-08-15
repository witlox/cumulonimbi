import base64
import requests
import sys

"""" This is a test to see if the started machines can at least update the status """""


class StatusUpdate:
    cagaas_base_url = 'https://cagaas.nl/'
    cagaas_status_url = 'api/VirtualMachines/{0}/status'
    s = requests.Session()

    def run(self):
        self.update_status('Running', '265a90c3-3213-48dc-91be-cb48f0a5830d', 'c2229f53-3e8c-440d-b0fd-9f2ae22ee159')

    def update_status(self, status, user_id, machine_id):
        self.s.headers.update({'Authorization': 'Basic ' + base64.b64encode(user_id)})
        data = {u'': status}
        full_url = self.cagaas_base_url + self.cagaas_status_url.replace('{0}', machine_id)
        r = self.s.put(full_url, data=data, verify=False)
        if r.status_code != 200:
            raise Exception("Could not update status")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print 'Run script as follows:'
        print ' status_update.py status user_id machine_id'
    StatusUpdate().update_status(sys.argv[1], sys.argv[2], sys.argv[3])

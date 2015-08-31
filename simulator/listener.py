from base64 import b64decode
from threading import Thread, Event
from time import sleep

from azure.storage import QueueService
from flask import json
import requests

from settings import Settings


class SimulationListener(Thread):
    def __init__(self):
        Thread.__init__(self)
        self._quit = Event()
        self.daemon = True

        settings = Settings()
        self.create_queue = 'create-simulated-machine'
        self.destroy_queue = 'destroy-simulated-machine'

        self.queue_service = QueueService(
            account_name=settings.azure_queue_account,
            account_key=settings.azure_queue_key
        )
        self.queue_service.create_queue(self.create_queue)
        self.queue_service.create_queue(self.destroy_queue)

    def run(self):
        # dislike of unstoppable threads
        while not self._quit.is_set():
            messages = self.queue_service.get_messages(self.create_queue, numofmessages=10)
            for m in messages:
                machine_json = b64decode(m.message_text)
                machine = json.loads(machine_json)
                print "Creating: " + machine["Name"] + " on " + machine["Provider"]
                print machine_json
                requests.post("http://localhost:8080/machines", machine_json)
                self.queue_service.delete_message(self.create_queue, m.message_id, m.pop_receipt)

            messages = self.queue_service.get_messages(self.destroy_queue, numofmessages=10)
            for m in messages:
                machine_json = b64decode(m.message_text)
                machine = json.loads(machine_json)
                print "Deleting: " + machine["Name"] + " on " + machine["Provider"]
                print machine_json
                requests.delete("http://localhost:8080/machines/" + machine["MachineId"])
                self.queue_service.delete_message(self.destroy_queue, m.message_id, m.pop_receipt)

            sleep(1)

    def quit(self):
        self._quit.set()

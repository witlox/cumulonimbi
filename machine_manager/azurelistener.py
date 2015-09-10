import logging
from threading import Thread, Event
from time import sleep
from azure.servicebus import ServiceBusService
from flask import json
from settings import Settings


class AzureListener(Thread):
    def __init__(self, machine_manager_logic):
        Thread.__init__(self)
        self._quit = Event()
        self.daemon = True
        self.log = logging.getLogger(__name__)
        self.notification_topic = 'jobs_changed'
        self.subscription = 'AllMessages'
        self.machine_manager_logic = machine_manager_logic

        settings = Settings()
        self.bus_service = ServiceBusService(
            service_namespace=settings.azure_topic_namespace,
            shared_access_key_name=settings.azure_topic_keyname,
            shared_access_key_value=settings.azure_topic_key
        )
        self.bus_service.create_topic(self.notification_topic)
        self.bus_service.create_subscription(self.notification_topic, self.subscription)

    def quit(self):
        self._quit.set()

    def run(self):
        # dislike of unstoppable threads
        while not self._quit.is_set():
            msg = self.bus_service.receive_subscription_message(self.notification_topic, self.subscription,
                                                                peek_lock=False, timeout=0.1)
            if msg.body is not None:
                self.log.info(msg.body + ":" + json.dumps(msg.custom_properties))

                if "Created" in msg.body:
                    self.machine_manager_logic.job_added(msg.custom_properties['job_id'])

                if "Assigned" in msg.body:
                    self.machine_manager_logic.job_assigned(msg.custom_properties['job_id'], msg.custom_properties['machine_id'])

                if "Finished" in msg.body:
                    self.machine_manager_logic.job_removed(msg.custom_properties['job_id'])

            self.machine_manager_logic.check_machines()
            sleep(10)

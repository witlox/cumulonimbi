import logging
from threading import Thread, Event
from time import sleep
from azure.servicebus import ServiceBusService
from settings import Settings


class AzureListener(Thread):
    def __init__(self):
        Thread.__init__(self)
        self._quit = Event()
        self.daemon = True
        self.log = logging.getLogger(__name__)
        self.notification_topic = 'jobs_changed'
        self.subscription = 'AllMessages'

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
                self.log.info(msg.body + ":" + msg.custom_properties['job_id'])

            sleep(3)

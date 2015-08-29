from threading import Thread, Event
import time

from azure.servicebus import ServiceBusService, Message
from azure.storage import QueueService

from settings import Settings


class AzureBroker(Thread):
    def __init__(self):
        Thread.__init__(self)
        self._quit = Event()
        self.daemon = True
        self.outgoing_queue = 'outgoing'
        self.incoming_queue = 'incoming'

        self.outgoing_topic = 'outgoing'
        self.incoming_topic = 'incoming'

        settings = Settings()
        try:
            self.queue_service = QueueService(
                account_name=settings.azure_queue_account,
                account_key=settings.azure_queue_key)
            self.queue_service.create_queue(self.outgoing_queue)
            self.queue_service.create_queue(self.incoming_queue)
        except Exception as e:
            print e

        try:
            self.bus_service = ServiceBusService(
                service_namespace=settings.azure_topic_namespace,
                shared_access_key_name=settings.azure_topic_keyname,
                shared_access_key_value=settings.azure_topic_key
            )
            self.bus_service.create_topic(self.incoming_topic)
            self.bus_service.create_topic(self.outgoing_topic)
            self.incoming_topic_subscription = 'AllMessages'
            self.bus_service.create_subscription(self.incoming_topic, self.incoming_topic_subscription)
        except Exception as e:
            print e

    def run(self):
        # dislike of unstoppable threads
        while not self._quit.is_set():
            messages = self.queue_service.get_messages(self.incoming_queue, numofmessages=10)
            for m in messages:
                print m.message_text
                self.queue_service.delete_message(self.incoming_queue, m.message_id, m.pop_receipt)

            msg = self.bus_service.receive_subscription_message(self.incoming_topic, self.incoming_topic,
                                                                peek_lock=False, timeout=0.1)
            if msg.body is not None:
                print msg.body + ":" + msg.custom_properties['job_id']

            time.sleep(3)

    def put_on_queue(self, job_id):
        # add something to the outgoing queue
        self.queue_service.put_message(self.outgoing_queue, job_id)

        msg = Message('Created'.encode('utf-8'), custom_properties={'job_id': job_id})
        self.bus_service.send_topic_message(self.outgoing_topic, msg)

        print "Adding job to queue and topic " + job_id

    def quit(self):
        self._quit.set()

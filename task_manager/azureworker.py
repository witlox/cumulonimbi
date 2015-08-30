from threading import Thread, Event
from time import sleep
from azure.servicebus import ServiceBusService
import logging
import requests
from settings import Settings
from task_manager.executor import Executor


class AzureWorker(Thread):
    def __init__(self):
        Thread.__init__(self)
        self._quit = Event()

        settings = Settings()
        settings.configure_logging('../logs/task_manager.log', 'TaskManagerAzureWorker')

        self.job_manager_url = 'http://' + settings.job_manager_api_connect + ':5000'

        self.unfinished = []
        self.finished = []
        self.executor = Executor(self.unfinished, self.finished)

        self.outgoing_topic = 'finished_jobs'
        self.incoming_topic = 'pending_jobs'

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

    def quit(self):
        self._quit.set()

    def run(self):
        self.executor.start()

        # dislike of unstoppable threads
        while not self._quit.is_set():
            msg = self.bus_service.receive_subscription_message(self.incoming_topic, self.incoming_topic_subscription,
                                                                peek_lock=True)
            if msg.body is not None:
                # New job for us!
                job_id = msg.custom_properties['job_id']
                logging.info('getting job with id: ' + job_id + ' from the API')

                r = requests.get(self.job_manager_url + '/jobs/' + job_id)
                job = r.json()

                msg.delete()

                logging.info('appending tasks from job with id: ' + job['id'] + ' and name: ' + job['name'])
                self.unfinished.append(job['name'])

            sleep(3)

        # stop executor
        self.executor.quit()
        self.executor.join()

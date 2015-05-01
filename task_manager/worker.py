from random import randint
from threading import Thread
import threading
import time
import zmq
import logging
from settings import Settings

class Worker(Thread):
    """
    Task manager worker, get work from the job manager broker, and execute it.
    """

    def __init__(self):
        Thread.__init__(self)
        self._quit = threading.Event()
        self.daemon = True

        self.settings = Settings()
        self.settings.configure_logging('../logs/task_manager.log')

        self.ppp_settings = self.settings.ParanoidPirateProtocolSetting()

        self.context = zmq.Context.instance()
        self.poller = zmq.Poller()

        self.working = False
        self.message = None

    def worker_socket(self, settings, context, poller):
        """
        Helper function that returns a new configured socket connected to the Paranoid Pirate queue
        """
        worker = context.socket(zmq.DEALER)
        identity = u'%04X-%04X' % (randint(0, 0x10000), randint(0, 0x10000))
        worker.setsockopt_string(zmq.IDENTITY, identity)
        poller.register(worker, zmq.POLLIN)
        worker.connect('tcp://%s:%d' % (settings.job_manager_api, settings.job_manager_router_port))
        worker.send_string(self.ppp_settings.PPP_READY)
        return worker

    def quit(self):
        self._quit.set()

    def run(self):
        liveliness = self.ppp_settings.HEARTBEAT_LIVELINESS
        interval = self.ppp_settings.INTERVAL_INIT

        heartbeat_at = time.time() + self.ppp_settings.HEARTBEAT_INTERVAL

        worker = self.worker_socket(self.settings, self.context, self.poller)

        while not self._quit.is_set():
            socks = dict(self.poller.poll(self.ppp_settings.HEARTBEAT_INTERVAL * 1000))
            # Handle worker activity on backend
            if socks.get(worker) == zmq.POLLIN:
                # Get message
                # - 3-part envelope + content -> request
                # - 1-part HEARTBEAT -> heartbeat
                frames = worker.recv_multipart()
                if not frames:
                    break  # Interrupted
                if len(frames) == 3:
                    worker.send_multipart(frames)
                    liveliness = self.ppp_settings.HEARTBEAT_LIVELINESS
                    time.sleep(1)  # Do some heavy work
                elif len(frames) == 1 and frames[0] == self.ppp_settings.PPP_HEARTBEAT:
                    logging.debug('Queue heartbeat')
                    liveliness = self.ppp_settings.HEARTBEAT_LIVELINESS
                else:
                    logging.info('received message: %s' % frames)
                    self.message = frames[0]
                    self.working = True  # magic process
                interval = self.ppp_settings.INTERVAL_INIT
            else:
                liveliness -= 1
                if liveliness == 0:
                    logging.warning('Heartbeat failure, cannot reach queue, reconnecting in %s' % str(interval))
                    time.sleep(interval)
                    if interval < self.ppp_settings.INTERVAL_MAX:
                        interval *= 2
                    self.poller.unregister(worker)
                    worker.setsockopt(zmq.LINGER, 0)
                    worker.close()
                    worker = self.worker_socket(self.settings, self.context, self.poller)
                    liveliness = self.ppp_settings.HEARTBEAT_LIVELINESS
            if time.time() > heartbeat_at:
                heartbeat_at = time.time() + self.ppp_settings.HEARTBEAT_INTERVAL
                logging.debug('Worker heartbeat')
                worker.send(self.ppp_settings.PPP_HEARTBEAT)

        # cleanup context
        worker.close()
        self.context.term()

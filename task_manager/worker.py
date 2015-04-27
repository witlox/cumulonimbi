from random import randint
from threading import Thread
import threading
import time
import zmq
import logging
from settings import Settings


class StoppableThread(Thread):
    """
    Thread class with a stop() method. The thread itself has to check regularly for the stopped() condition.
    """

    def __init__(self):
        super(StoppableThread, self).__init__()
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()


class Worker(StoppableThread):
    HEARTBEAT_LIVELINESS = 3
    HEARTBEAT_INTERVAL = 1
    INTERVAL_INIT = 1
    INTERVAL_MAX = 32

    # Paranoid Pirate Protocol constants
    PPP_READY = '\x01'  # Signals worker is ready
    PPP_HEARTBEAT = '\x02'  # Signals worker heartbeat

    def worker_socket(self, settings, context, poller):
        """
        Helper function that returns a new configured socket connected to the Paranoid Pirate queue
        """
        worker = context.socket(zmq.DEALER)
        identity = '%04X-%04X' % (randint(0, 0x10000), randint(0, 0x10000))
        worker.setsockopt(zmq.IDENTITY, identity)
        poller.register(worker, zmq.POLLIN)
        worker.connect('tcp://%s:%d' % (settings.job_manager_api, settings.job_manager_router_port))
        worker.send(self.PPP_READY)
        return worker

    def __init__(self):
        StoppableThread.__init__(self)
        self.daemon = True

        self.settings = Settings()
        self.settings.configure_logging('../logs/task_manager.log')

        self.context = zmq.Context.instance()
        self.poller = zmq.Poller()


    def run(self):
        liveliness = self.HEARTBEAT_LIVELINESS
        interval = self.INTERVAL_INIT

        heartbeat_at = time.time() + self.HEARTBEAT_INTERVAL

        worker = self.worker_socket(self.settings, self.context, self.poller)

        while not self.stopped():
            socks = dict(self.poller.poll(self.HEARTBEAT_INTERVAL * 1000))
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
                    liveliness = self.HEARTBEAT_LIVELINESS
                    time.sleep(1)  # Do some heavy work
                elif len(frames) == 1 and frames[0] == self.PPP_HEARTBEAT:
                    logging.debug('Queue heartbeat')
                    liveliness = self.HEARTBEAT_LIVELINESS
                else:
                    logging.info('received message: %s' % frames)
                interval = self.INTERVAL_INIT
            else:
                liveliness -= 1
                if liveliness == 0:
                    logging.warn('Heartbeat failure, cannot reach queue, reconnecting in %s' % str(interval))
                    time.sleep(interval)
                    if interval < self.INTERVAL_MAX:
                        interval *= 2
                    self.poller.unregister(worker)
                    worker.setsockopt(zmq.LINGER, 0)
                    worker.close()
                    worker = self.worker_socket(self.settings, self.context, self.poller)
                    liveliness = self.HEARTBEAT_LIVELINESS
            if time.time() > heartbeat_at:
                heartbeat_at = time.time() + self.HEARTBEAT_INTERVAL
                logging.debug('Worker heartbeat')
                worker.send(self.PPP_HEARTBEAT)

        # cleanup context
        worker.close()
        self.context.term()

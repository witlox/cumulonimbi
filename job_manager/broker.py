import logging
from threading import Thread
import threading
from settings import Settings

import zmq


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


class Broker(StoppableThread):

    """
    Broker that receives Jobs, and queue's them for use by a worker
    """

    def __init__(self):
        StoppableThread.__init__(self)
        self.daemon = True
        # load settings
        settings = Settings()
        # prepare context
        context = zmq.Context.instance()
        # connect sockets
        self.frontend = context.socket(zmq.ROUTER)
        self.backend = context.socket(zmq.DEALER)
        self.frontend.bind("tcp://*:%d" % settings.job_manager_router_port)
        self.backend.bind("tcp://*:%d" % settings.job_manager_dealer_port)

    def run(self):
        # Initialize poll set
        poller = zmq.Poller()
        poller.register(self.frontend, zmq.POLLIN)
        poller.register(self.backend, zmq.POLLIN)

        # dislike of unstoppable threads
        while not self.stopped():
            # Switch messages between sockets
            socks = dict(poller.poll())

            if socks.get(self.frontend) == zmq.POLLIN:
                message = self.frontend.recv_multipart()
                self.backend.send_multipart(message)
                self.frontend.send_multipart(message)

            if socks.get(self.backend) == zmq.POLLIN:
                message = self.backend.recv_multipart()
                logging.info(message)

                # Update state in backend/api/jobmanager/database?
                # frontend.send_multipart(message)

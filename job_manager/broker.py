import logging
from threading import Thread
import threading

__author__ = 'johannes.bertens'

import zmq


class StoppableThread(Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self):
        super(StoppableThread, self).__init__()
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()


class Broker(StoppableThread):
    def __init__(self):
        StoppableThread.__init__(self)
        self.daemon = True

        # Prepare our context and sockets
        context = zmq.Context()
        self.frontend = context.socket(zmq.ROUTER)
        self.backend = context.socket(zmq.DEALER)
        self.frontend.bind("tcp://*:5559")
        self.backend.bind("tcp://*:5560")


    def run(self):
        # Initialize poll set
        poller = zmq.Poller()
        poller.register(self.frontend, zmq.POLLIN)
        poller.register(self.backend, zmq.POLLIN)

        # Switch messages between sockets
        while not self.stopped():
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

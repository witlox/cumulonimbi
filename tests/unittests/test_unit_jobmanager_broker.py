# python 2 <-> 3 compatibility
from __future__ import unicode_literals

from random import randint
import time
import unittest
import zmq
from job_manager.broker import Broker, StoppableThread
from settings import Settings


HEARTBEAT_LIVELINESS = 3
HEARTBEAT_INTERVAL = 1
INTERVAL_INIT = 1
INTERVAL_MAX = 32

#  Paranoid Pirate Protocol constants
PPP_READY = bytes('\x01')      # Signals worker is ready
PPP_HEARTBEAT = bytes('\x02')  # Signals worker heartbeat


class TestWorker(StoppableThread):

    message = None
    processed = False

    def __init__(self):
        StoppableThread.__init__(self)
        self.daemon = True
        self.settings = Settings()
        self.context = zmq.Context.instance()
        self.poller = zmq.Poller()

    def worker_socket(self):
        """
        Helper function that returns a new configured socket connected to the Paranoid Pirate queue
        """
        worker = self.context.socket(zmq.DEALER)
        identity = '%04X-%04X' % (randint(0, 0x10000), randint(0, 0x10000))
        worker.setsockopt(zmq.IDENTITY, bytes(identity))
        self.poller.register(worker, zmq.POLLIN)
        worker.connect('tcp://%s:%d' % (self.settings.job_manager_api, self.settings.job_manager_router_port))
        worker.send(PPP_READY)
        return worker

    def run(self):
        liveliness = HEARTBEAT_LIVELINESS
        interval = INTERVAL_INIT
        heartbeat_at = time.time() + HEARTBEAT_INTERVAL
        worker = self.worker_socket()
        while not self.stopped():
            socks = dict(self.poller.poll(HEARTBEAT_INTERVAL * 1000))
            # Handle worker activity on backend
            if socks.get(worker) == zmq.POLLIN:
                #  Get message
                #  - 3-part envelope + content -> request
                #  - 1-part HEARTBEAT -> heartbeat
                frames = worker.recv_multipart()
                if not frames:
                    break  # Interrupted
                if len(frames) == 3:
                    worker.send_multipart(frames)
                    liveliness = HEARTBEAT_LIVELINESS
                    time.sleep(1)  # Do some heavy work
                elif len(frames) == 1 and frames[0] == PPP_HEARTBEAT:
                    print('Queue heartbeat')
                    liveliness = HEARTBEAT_LIVELINESS
                else:
                    print('received message: %s' % frames)
                    self.message = str(frames[0])
                    self.processed = True
                interval = INTERVAL_INIT
            else:
                liveliness -= 1
                if liveliness == 0:
                    print('Heartbeat failure, cannot reach queue')
                    print('Reconnecting in %d' % interval)
                    time.sleep(interval)
                    if interval < INTERVAL_MAX:
                        interval *= 2
                    self.poller.unregister(worker)
                    worker.setsockopt(zmq.LINGER, 0)
                    worker.close()
                    worker = self.worker_socket()
                    liveliness = HEARTBEAT_LIVELINESS
            if time.time() > heartbeat_at:
                heartbeat_at = time.time() + HEARTBEAT_INTERVAL
                print('Worker heartbeat')
                worker.send(PPP_HEARTBEAT)
        worker.close()
        self.context.term()


class MyTestCase(unittest.TestCase):
    def setUp(self):
        settings = Settings()
        # create a socket to send our messages to
        context = zmq.Context.instance()
        self.socket = context.socket(zmq.REQ)
        self.socket.connect('tcp://%s:%d' % (settings.job_manager_api, settings.job_manager_router_port))
        # start non-blocking queue
        self.broker = Broker()
        self.broker.start()
        # start a worker
        self.workers = []

    def tearDown(self):
        for worker in self.workers:
            worker.stop()
        self.broker.stop()

    def test_message_queue(self):
        # add the worker
        worker = TestWorker()
        worker.start()
        self.workers.append(worker)
        # send a message to the worker
        self.broker.put_on_queue('Hello')
        # wait for the worker to process the message
        while not worker.processed:
            time.sleep(3)
        self.assertEqual('Hello', worker.message)


if __name__ == '__main__':
    unittest.main()

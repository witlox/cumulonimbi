# python 2 <-> 3 compatibility
try:
    from Queue import Queue
except ImportError:
    from queue import Queue

import logging
import threading
import time
import zmq

from collections import OrderedDict
from threading import Thread
from settings import Settings


class Worker(object):
    def __init__(self, address):
        ppp_settings = Settings.ParanoidPirateProtocolSetting()
        self.address = address
        self.expiry = time.time() + ppp_settings.HEARTBEAT_INTERVAL * ppp_settings.HEARTBEAT_LIVELINESS


class WorkerQueue(object):
    def __init__(self):
        self.queue = OrderedDict()

    def ready(self, worker):
        self.queue.pop(worker.address, None)
        self.queue[worker.address] = worker

    def purge(self):
        """Look for & kill expired workers."""
        t = time.time()
        expired = []
        for address, worker in self.queue.items():
            if t > worker.expiry:  # Worker expired
                expired.append(address)
        for address in expired:
            self.queue.pop(address, None)

    def size(self):
        return len(self.queue.items())

    def next(self):
        if len(self.queue.items()) == 0:
            return None

        address, worker = self.queue.popitem(False)
        return address


class ZmqBroker(Thread):
    """
    Put tasks on the queue for use by a worker, this implements half of the Paranoid Pirate pattern
    """

    def __init__(self):
        Thread.__init__(self)
        self._quit = threading.Event()
        self.daemon = True
        # load settings
        settings = Settings()
        self.ppp_settings = Settings.ParanoidPirateProtocolSetting()
        # prepare synchronized queue
        self.queue = Queue()
        # prepare context
        self.context = zmq.Context.instance()
        # connect dealer socket
        self.dealer = self.context.socket(zmq.ROUTER)
        self.dealer.bind('tcp://*:%d' % settings.job_manager_router_port)

    def put_on_queue(self, work):
        self.queue.put(work)

    def quit(self):
        self._quit.set()

    def run(self):
        # zmq queue mechanism for the dealer
        poll_workers = zmq.Poller()
        poll_workers.register(self.dealer, zmq.POLLIN)
        workers = WorkerQueue()
        heartbeat_at = time.time() + self.ppp_settings.HEARTBEAT_INTERVAL
        # dislike of unstoppable threads
        while not self._quit.is_set():
            # check for active workers
            socks = dict(poll_workers.poll(self.ppp_settings.HEARTBEAT_INTERVAL * 1000))
            # Handle worker activity on backend
            if socks.get(self.dealer) == zmq.POLLIN:
                # Use worker address for LRU routing
                frames = self.dealer.recv_multipart()
                if not frames:
                    break
                address = frames[0]
                workers.ready(Worker(address))
                # Validate control message, or return reply to client
                msg = frames[1:]
                if len(msg) == 1:
                    if msg[0] not in (self.ppp_settings.PPP_READY, self.ppp_settings.PPP_HEARTBEAT):
                        logging.error('Invalid message from worker: %s' % msg[0].decode())
                # Send heartbeats to idle workers if it's time
                if time.time() >= heartbeat_at:
                    for worker in workers.queue:
                        msg = [worker, self.ppp_settings.PPP_HEARTBEAT]
                        self.dealer.send_multipart(msg)
                    heartbeat_at = time.time() + self.ppp_settings.HEARTBEAT_INTERVAL

            if self.queue.qsize() > 0 and workers.size() == 0:
                logging.info('amount of unfinished tasks: {0}, amount of workers: {1}'.format(self.queue.qsize(),
                                                                                              workers.size()))
                time.sleep(1)

            # send the work to the queue
            next_worker = workers.next()
            if next_worker and not self.queue.empty():
                qi = self.queue.get()
                frames = [next_worker, qi.encode()]
                self.dealer.send_multipart(frames)

        workers.purge()
        # out of loop, cleanup connections
        self.dealer.close()

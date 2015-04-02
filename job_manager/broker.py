import logging
import threading
import time
import zmq

from collections import OrderedDict
from Queue import Queue
from threading import Thread
from settings import Settings


#  check intervals
HEARTBEAT_LIVELINESS = 3   # 3..5 is reasonable
HEARTBEAT_INTERVAL = 1.0   # Seconds

#  Paranoid Pirate Protocol constants
PPP_READY = '\x01'      # Signals worker is ready
PPP_HEARTBEAT = '\x02'  # Signals worker heartbeat


class Worker(object):
    def __init__(self, address):
        self.address = address
        self.expiry = time.time() + HEARTBEAT_INTERVAL * HEARTBEAT_LIVELINESS


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
        for address,worker in self.queue.iteritems():
            if t > worker.expiry:  # Worker expired
                expired.append(address)
        for address in expired:
            print "W: Idle worker expired: %s" % address
            self.queue.pop(address, None)

    def next(self):
        address, worker = self.queue.popitem(False)
        return address


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
    Put tasks on the queue for use by a worker, this implements half of the Paranoid Pirate pattern
    """

    def __init__(self):
        StoppableThread.__init__(self)
        self.daemon = True
        # load settings
        settings = Settings()
        # prepare synchronized queue
        self.queue = Queue()
        # prepare context
        self.context = zmq.Context.instance()
        # connect dealer socket
        self.dealer = self.context.socket(zmq.ROUTER)
        self.dealer.bind('tcp://*:%d' % settings.job_manager_router_port)

    def put_on_queue(self, work):
        self.queue.put(work)

    def run(self):
        # zmq queue mechanism for the dealer
        poll_workers = zmq.Poller()
        poll_workers.register(self.dealer, zmq.POLLIN)
        workers = WorkerQueue()
        heartbeat_at = time.time() + HEARTBEAT_INTERVAL
        # dislike of unstoppable threads
        while not self.stopped():
            # check for active workers
            socks = dict(poll_workers.poll(HEARTBEAT_INTERVAL * 1000))
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
                    if msg[0] not in (PPP_READY, PPP_HEARTBEAT):
                        logging.error('Invalid message from worker: %s' % msg)
                # Send heartbeats to idle workers if it's time
                if time.time() >= heartbeat_at:
                    for worker in workers.queue:
                        msg = [worker, PPP_HEARTBEAT]
                        self.dealer.send_multipart(msg)
                    heartbeat_at = time.time() + HEARTBEAT_INTERVAL
            # send the work to the queue
            while not self.queue.empty():
                frames = [workers.next(), self.queue.get()]
                self.dealer.send_multipart(frames)
            workers.purge()
        # out of loop, cleanup connections
        self.dealer.close()
        self.context.term()

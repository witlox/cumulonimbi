from random import randint
import time
import zmq
import logging
from settings import Settings

HEARTBEAT_LIVELINESS = 3
HEARTBEAT_INTERVAL = 1
INTERVAL_INIT = 1
INTERVAL_MAX = 32

#  Paranoid Pirate Protocol constants
PPP_READY = '\x01'      # Signals worker is ready
PPP_HEARTBEAT = '\x02'  # Signals worker heartbeat


def worker_socket(settings, context, poller):
    """
    Helper function that returns a new configured socket connected to the Paranoid Pirate queue
    """
    worker = context.socket(zmq.DEALER)
    identity = '%04X-%04X' % (randint(0, 0x10000), randint(0, 0x10000))
    worker.setsockopt(zmq.IDENTITY, identity)
    poller.register(worker, zmq.POLLIN)
    worker.connect('tcp://%s:%d' % (settings.job_manager_api, settings.job_manager_router_port))
    worker.send(PPP_READY)
    return worker

settings = Settings()
settings.configure_logging('../logs/task_manager.log')


context = zmq.Context.instance()
poller = zmq.Poller()

liveliness = HEARTBEAT_LIVELINESS
interval = INTERVAL_INIT

heartbeat_at = time.time() + HEARTBEAT_INTERVAL

worker = worker_socket(settings, context, poller)

while True:
    socks = dict(poller.poll(HEARTBEAT_INTERVAL * 1000))
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
            logging.debug('Queue heartbeat')
            liveliness = HEARTBEAT_LIVELINESS
        else:
            logging.info('received message: %s' % frames)
        interval = INTERVAL_INIT
    else:
        liveliness -= 1
        if liveliness == 0:
            logging.warn('Heartbeat failure, cannot reach queue, reconnecting in %d' % str(interval))
            time.sleep(interval)
            if interval < INTERVAL_MAX:
                interval *= 2
            poller.unregister(worker)
            worker.setsockopt(zmq.LINGER, 0)
            worker.close()
            worker = worker_socket(settings, context, poller)
            liveliness = HEARTBEAT_LIVELINESS
    if time.time() > heartbeat_at:
        heartbeat_at = time.time() + HEARTBEAT_INTERVAL
        logging.debug('Worker heartbeat')
        worker.send(PPP_HEARTBEAT)

# cleanup context
worker.close()
context.term()

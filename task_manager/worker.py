__author__ = 'johannes.bertens'

import zmq
import logging
from settings import Settings

settings = Settings()
settings.configure_logging('../logs/task_manager.log')

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.connect('tcp://%s:%d' % (settings.job_manager_api, settings.job_manager_dealer_port))

while True:
    message = socket.recv()
    logging.info("Received request: %s" % message)
    socket.send(b"World")

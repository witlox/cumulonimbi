__author__ = 'johannes.bertens'

import zmq
import logging
from settings import Settings

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.connect("tcp://localhost:5560")

settings = Settings()
settings.configure_logging()

while True:
    message = socket.recv()
    logging.info("Received request: %s" % message)
    socket.send(b"World")
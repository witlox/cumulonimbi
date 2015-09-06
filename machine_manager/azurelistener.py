import logging
from threading import Thread, Event
from time import sleep


class AzureListener(Thread):
    def __init__(self):
        Thread.__init__(self)
        self._quit = Event()
        self.log = logging.getLogger(__name__)

    def quit(self):
        self._quit.set()

    def run(self):
        # dislike of unstoppable threads
        while not self._quit.is_set():
            self.log.info("test")
            sleep(3)

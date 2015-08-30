from threading import Thread
import threading
import logging
import time
from settings import Settings


class Executor(Thread):
    """
    Execute tasks
    """

    def __init__(self, unfinished, finished):
        Thread.__init__(self)
        self._quit = threading.Event()
        self.daemon = True
        # load settings
        self.settings = Settings()
        self.settings.configure_logging('../logs/task_manager.log', 'TaskManagerExecutor')
        self.unfinished = unfinished
        self.finished = finished

    def quit(self):
        self._quit.set()

    def do_work(self):
        workload = self.unfinished.pop()
        logging.info('executing workload: %s' % workload)
        time.sleep(.1)
        self.finished.append(workload)

    def run(self):
        logging.info('starting task executor')

        # dislike of unstoppable threads
        while not self._quit.is_set():
            # check for work
            if len(self.unfinished) > 0:
                self.do_work()
            else:
                time.sleep(.1)

        logging.info('stopping task executor')

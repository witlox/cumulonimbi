import os
import logging
import logging.config


class Settings(object):
    debug = False
    project_root = os.path.abspath(os.path.dirname(__file__))

    def configure_logging(self):
        log_ini = os.path.join(self.project_root, 'logging.ini')
        if os.path.exists(log_ini):
            logging.config.fileConfig(log_ini)
import os
from logging.config import dictConfig, logging


class Settings(object):
    debug = False
    project_root = os.path.abspath(os.path.dirname(__file__))

    job_manager_api = "localhost"
    job_manager_router_port = 5559
    job_manager_dealer_port = 5560

    log_file_level = 'DEBUG'
    log_file_size = 1024 * 1024 * 100
    log_file_rotate = 10

    log_stash_level = 'INFO'
    log_stash_host = 'localhost'
    log_stash_port = 9300

    def configure_logging(self, file_name):
        logging_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {'format': '%(asctime)s[%(levelname)s](%(name)s):%(message)s',
                             'datefmt': '%Y-%m-%d %H:%M:%S'}
            },
            'handlers': {
                'fh': {'class': 'logging.handlers.RotatingFileHandler',
                       'formatter': 'standard',
                       'level': self.log_file_level,
                       'filename': file_name,
                       'mode': 'a',
                       'maxBytes': self.log_file_size,
                       'backupCount': self.log_file_rotate},
                'ls': {'class': 'logstash.TCPLogstashHandler',
                       'formatter': 'standard',
                       'level': self.log_stash_level,
                       'host': self.log_stash_host,
                       'port': self.log_stash_port,
                       'version': 1}
            },
            'loggers': {
                '': {'handlers': ['fh', 'ls'],
                     'level': 'DEBUG',
                     'propagate': True}
            }
        }
        dictConfig(logging_config)
        logging.debug('logging configured')

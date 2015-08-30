import json
import os
from logging.config import dictConfig, logging


class Settings(object):
    """
    This class contains all settings for the cumulonimbi project
    """

    class ParanoidPirateProtocolSetting(object):
        """
        These are the socket timing settings and protocol specs for the Paranoid Pirate Protocol (PPP) implementation
        Change these at your own risk :)
        """

        HEARTBEAT_LIVELINESS = 3
        HEARTBEAT_INTERVAL = 1
        INTERVAL_INIT = 1
        INTERVAL_MAX = 32

        # Paranoid Pirate Protocol constants
        PPP_READY = '\x01'.encode()  # Signals worker is ready
        PPP_HEARTBEAT = '\x02'.encode()  # Signals worker heartbeat

    debug = False  # False seems better
    project_root = os.path.abspath(os.path.dirname(__file__))

    try:
        with open("../Config.json") as json_data_file:
            data = json.load(json_data_file)
        print data
        azure_topic_namespace = data['azure']['topic']['namespace']
        azure_topic_keyname = data['azure']['topic']['keyname']
        azure_topic_key = data['azure']['topic']['key']
        job_manager_api_bind = data['jm']['api']['bind']
        job_manager_api_connect = data['jm']['api']['connect']
    except IOError as e:
        azure_topic_namespace = 'abc'
        azure_topic_keyname = 'abc'
        azure_topic_key = 'abc'
        job_manager_api_bind = '0.0.0.0'.encode()
        job_manager_api_connect = 'docker-cluster.cloudapp.net'.encode()

    job_manager_mongo_client_host = '0.0.0.0'.encode()
    job_manager_mongo_client_port = 27017
    job_manager_router_port = 5559

    log_file_level = 'DEBUG'
    log_file_size = 1024 * 1024 * 100
    log_file_rotate = 10

    log_stash_level = 'INFO'
    log_stash_host = 'localhost'
    log_stash_port = 9300

    repository = None

    def configure_logging(self, file_path, module_name):
        """
        Configure logging per instance, set the file path for the rotating file logger
        """

        path_dir = os.path.dirname(file_path)
        if not os.path.exists(path_dir):
            os.makedirs(path_dir)

        logging_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {'format': '[' + module_name + ']-%(asctime)s[%(levelname)s](%(name)s):%(message)s',
                             'datefmt': '%Y-%m-%d %H:%M:%S'},
                'logstash': {'format': '[' + module_name + ']-[%(levelname)s] %(message)s'}
            },
            'handlers': {
                'fh': {'class': 'logging.handlers.RotatingFileHandler',
                       'formatter': 'standard',
                       'level': self.log_file_level,
                       'filename': file_path,
                       'mode': 'a',
                       'maxBytes': self.log_file_size,
                       'backupCount': self.log_file_rotate},
                'ls': {'class': 'logstash.TCPLogstashHandler',
                       'formatter': 'logstash',
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

        # always send an initial debug message so we can see if the logger is working as desired
        logging.info('logging configured')

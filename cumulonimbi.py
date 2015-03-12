
__author__ = 'witlox'

import argparse
import logging
from settings import Settings
from job_manager.repository import JobManagerRepository
import job_manager.api as jmapi

class Cumulonimbi:

    args = None
    settings = None

    def __init__(self):
        settings = Settings()
        settings.configure_logging()

    def run(self):
        # Parse command line arguments.
        self.parse_arguments()
        try:
            # Determine type of run
            if self.args.__dict__["run_mode"] == "all":
                self.start_job_manager()
            elif self.args.__dict__["run_mode"] == "jm":
                self.start_job_manager()
            elif self.args.__dict__["run_mode"] == "tm":
                pass

        except Exception, e:
            logging.error(e)

    def parse_arguments (self) :

        parser = argparse.ArgumentParser(description='Test Bench Version 3, test runner for black box tests.')

        # Compulsory arguments
        run_mode_group = parser.add_mutually_exclusive_group(required=True)
        run_mode_group.add_argument("-a", "--all",
                                  help="Launch all modules: job manager, task manager, ...",
                                  dest="run_mode",
                                  action="store_const",
                                  const="all")
        run_mode_group.add_argument("-jm", "--job-manager",
                                  help="Launch job manager",
                                  dest="run_mode",
                                  action="store_const",
                                  const="jm")
        run_mode_group.add_argument("-tm", "--task-manager",
                                  help="Launch task manager",
                                  dest="run_mode",
                                  action="store_const",
                                  const="tm")

        # Optional arguments
        parser.add_argument("--log-level",
                          default="",
                          help="CRITICAL, ERROR, WARNING, INFO or DEBUG",
                          dest="loglevel")

        # Start parsing
        self.args = parser.parse_args()

        # configure optional debug level settings
        if self.args.__dict__["loglevel"] != "":
            level = self.args.__dict__["loglevel"]
            root_logger = logging.getLogger('')
            if not level:
                root_logger.setLevel(logging.DEBUG)
            if "info" in str(level).lower():
                root_logger.setLevel(logging.INFO)
            if "warn" in str(level).lower():
                root_logger.setLevel(logging.WARNING)
            if "err" in str(level).lower():
                root_logger.setLevel(logging.ERROR)


    def start_job_manager(self):
        jmapi.api.config.from_object(__name__)
        jmapi.api.config.from_pyfile('../../cumulonimbi.jm.py', silent=True)
        if jmapi.api.config['REPOSITORY'] is None:
            jmapi.api.config['REPOSITORY'] = JobManagerRepository()
        jmapi.api.run(host='0.0.0.0', debug=self.settings.debug)


if __name__ == "__main__":
    Cumulonimbi().run()

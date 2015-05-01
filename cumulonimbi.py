import argparse
import logging
from os import path
from settings import Settings
import job_manager.api as jmapi
import task_manager.worker as tmworker


""" This is the starting class for all Cumulonimbi. """


class Cumulonimbi:
    args = None
    settings = None

    def __init__(self):
        settings = Settings()
        logfile = path.dirname(path.abspath(__file__)) + '/logs/job_manager.log'
        settings.configure_logging(logfile)

    def run(self):
        # Parse command line arguments.
        self.parse_arguments()
        try:
            print("Runmode: %s" % self.args.__dict__["run_mode"])
            # Determine type of run
            if self.args.__dict__["run_mode"] == "all":
                self.start_job_manager()
            elif self.args.__dict__["run_mode"] == "jm":
                self.start_job_manager()
            elif self.args.__dict__["run_mode"] == "tm":
                pass

        except Exception as e:
            logging.error(e)
            raise

    def parse_arguments(self):

        parser = argparse.ArgumentParser(description='Cumulonimbi Scheduler.')

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
        jmapi.start()

    def start_task_manager(self):
        pass

if __name__ == "__main__":
    Cumulonimbi().run()

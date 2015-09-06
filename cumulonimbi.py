import argparse
import logging
from os import path
from settings import Settings
import job_manager.api as jmapi
import machine_manager.api as mmapi
from task_manager import launcher as tmlauncher
import simulator.api as simulator_api

""" This is the starting class for all Cumulonimbi. """


def start_job_manager():
    print "Starting JobManager"
    jmapi.start()


def start_task_manager():
    print "Starting TaskManager"
    tmlauncher.start()


def start_machine_manager():
    print "Starting MachineManager"
    mmapi.start()


def start_simulator():
    print "Starting Simulator"
    simulator_api.start()


class Cumulonimbi:
    args = None
    settings = None

    def __init__(self):
        settings = Settings()
        logfile = path.dirname(path.abspath(__file__)) + '/logs/job_manager.log'
        settings.configure_logging(logfile, 'Cumulonimbi')

    def run(self):
        # Parse command line arguments.
        self.parse_arguments()
        try:
            print("Runmode: %s" % self.args.__dict__["run_mode"])
            # Determine type of run
            if self.args.__dict__["run_mode"] == "all":
                start_job_manager()
            elif self.args.__dict__["run_mode"] == "jm":
                start_job_manager()
            elif self.args.__dict__["run_mode"] == "tm":
                start_task_manager()
            elif self.args.__dict__["run_mode"] == "mm":
                start_machine_manager()
            elif self.args.__dict__["run_mode"] == "s":
                start_simulator()

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
        run_mode_group.add_argument("-mm", "--machine-manager",
                                    help="Launch machine manager",
                                    dest="run_mode",
                                    action="store_const",
                                    const="mm")
        run_mode_group.add_argument("-s", "--simulator",
                                    help="Launch simulator",
                                    dest="run_mode",
                                    action="store_const",
                                    const="s")
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


if __name__ == "__main__":
    print "Starting Cumulonimbi"
    Cumulonimbi().run()

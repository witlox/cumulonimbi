from flask import Flask, Response
from flask.json import dumps
from machine_manager.azurelistener import AzureListener
from settings import Settings


class MachineManagerState(object):
    def __init__(self):
        self.jobs = []

    def job_added(self, job_id):
        self.jobs.append(job_id)

    def job_removed(self, job_id):
        self.jobs.remove(job_id)


state = MachineManagerState()
app = Flask(__name__)


@app.route("/")
def hello():
    return app.send_static_file("index.html")


@app.route("/machines")
def get_machines():
    # jsonify does not play well with lists
    return Response(dumps(state.jobs), mimetype='application/json')


def start():
    settings = Settings()
    settings.configure_logging('../logs/machine_manager.log', 'MachineManager')

    listener = AzureListener(state)
    listener.start()

    app.run("0.0.0.0", settings.machine_manager_api_port, debug=False)

    listener.quit()
    listener.join()

from flask import Flask, Response
from flask.json import dumps
from machine_manager.azurelistener import AzureListener
from machine_manager.logic import MachineManagerLogic
from settings import Settings

logic = MachineManagerLogic()
app = Flask(__name__)


@app.route("/")
def hello():
    return app.send_static_file("index.html")


@app.route("/machines")
def get_machines():
    # jsonify does not play well with lists
    return Response(dumps(logic.jobs), mimetype='application/json')


def start():
    settings = Settings()
    settings.configure_logging('../logs/machine_manager.log', 'MachineManager')

    listener = AzureListener(logic)
    listener.start()

    app.run("0.0.0.0", settings.machine_manager_api_port, debug=False)

    listener.quit()
    listener.join()

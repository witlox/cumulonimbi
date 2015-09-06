from flask import Flask, Response, jsonify, request
from flask.json import dumps
from settings import Settings
from simulator.listener import SimulationListener
from simulator.machine import Machine


class SimulatorState(object):
    def __init__(self):
        self.machines = []


state = SimulatorState()
app = Flask(__name__)


@app.route("/")
def hello():
    return app.send_static_file("index.html")


@app.route("/machines", methods=['GET'])
def get_machines():
    # jsonify does not play well with lists
    machines = [machine.info for machine in state.machines]
    return Response(dumps(machines), mimetype='application/json')


@app.route('/machines', methods=['POST'])
def add_machine():
    data = request.get_json(force=True)

    machine = Machine(data)
    machine.start()

    state.machines.append(machine)
    return jsonify(machine.info)


@app.route('/machines/<machine_id>', methods=['DELETE'])
def delete_machines(machine_id):
    for m in state.machines:
        if m.info['MachineId'] == machine_id:
            m.quit()
            m.join()

    machines = [machine.info for machine in state.machines]
    return Response(dumps(machines))


def start():
    settings = Settings()
    settings.configure_logging('../logs/simulator.log', 'Simulator')

    worker = SimulationListener()
    worker.start()

    app.run(host="0.0.0.0", port=settings.simulator_api_port, debug=False)

    worker.quit()
    worker.join()

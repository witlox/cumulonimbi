from flask import Flask, Response, jsonify, request
from flask.json import dumps
from simulator.listener import SimulationListener


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
    return Response(dumps(state.machines), mimetype='application/json')


@app.route('/machines', methods=['POST'])
def add_machine():
    data = request.get_json(force=True)
    state.machines.append(data)
    return jsonify(state.machines)


@app.route('/machines', methods=['PUT'])
def update_machine():
    to_delete = None
    data = request.get_json(force=True)
    for m in state.machines:
        if m['MachineId'] == data['MachineId']:
            to_delete = m

    if to_delete is not None:
        state.machines.remove(to_delete)
    state.machines.append(data)
    return jsonify(state.machines)


@app.route('/machines/<machine_id>', methods=['DELETE'])
def delete_machines(machine_id):
    for m in state.machines:
        if m['MachineId'] == machine_id:
            m['IsDeleted'] = True

    return jsonify(state.machines)


def start():
    worker = SimulationListener()
    worker.start()

    app.run("0.0.0.0", 8080, debug=False)

    worker.quit()
    worker.join()

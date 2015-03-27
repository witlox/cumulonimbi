"""
This is needed for 2.x and 3.x compatibility regarding imports
"""
if __name__ == '__main__' and __package__ is None:
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from job_manager.broker import Broker
from bson.json_util import dumps
from job_manager.repository import JobManagerRepository
from flask import Flask, Response, request
from settings import Settings
import zmq


"""
This is the main api for the job manager, entry point to Cumulonimbi
"""
api = Flask(__name__, instance_relative_config=True)

"""
Define the ZMQ socket as not initialized
"""
socket = None

@api.route('/jobs', methods=['GET'])
def get_jobs():
    repository = api.config['REPOSITORY']
    response = dumps(repository.get_all_jobs())
    return Response(response, mimetype='application/json')

@api.route('/jobs', methods=['DELETE'])
def delete_jobs():
    repository = api.config['REPOSITORY']
    response = dumps(repository.delete_all_jobs())
    return Response(response, mimetype='application/json')

@api.route('/jobs', methods=['POST'])
def create_job():
    job_name = request.form['jobname']
    repository = api.config['REPOSITORY']
    response = {'job_id': repository.insert_job(job_name)}
    if socket:
        socket.send(b"Hello")
        socket.recv()
    return Response(dumps(response), mimetype='application/json')

@api.route('/jobs/<job_id>', methods=['PUT'])
def edit_job(job_id):
    pass

@api.route('/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    repository = api.config['REPOSITORY']
    response = repository.get_job(job_id)
    return Response(dumps(response), mimetype='application/json')


@api.route('/jobs/<job_id>', methods=['DELETE'])
def delete_job(job_id):
    repository = api.config['REPOSITORY']
    response = repository.delete_job(job_id)
    return Response(dumps(response), mimetype='application/json')


if __name__ == "__main__":
    """
    Run the JobManager API from here with the configured settings
    """

    settings = Settings()
    settings.configure_logging('../logs/job_manager.log')

    # prepare our context and sockets
    context = zmq.Context.instance()
    socket = context.socket(zmq.REQ)
    socket.connect('tcp://%s:%d' % (settings.job_manager_api, settings.job_manager_router_port))

    # configure storage
    REPOSITORY = None
    api.config.from_object(__name__)
    api.config.from_pyfile('../../cumulonimbi.jm.py', silent=True)
    if api.config['REPOSITORY'] is None:
        api.config['REPOSITORY'] = JobManagerRepository()

    # start non-blocking queue
    broker = Broker()
    broker.start()

    # start flask
    api.run(host='%s' % settings.job_manager_api, debug=settings.debug)

    # cleanup
    broker.stop()
    broker.join()

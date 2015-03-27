__author__ = 'Johannes'

""" This is needed for 2.x and 3.x compatibility regarding imports """
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
    socket.send(b"Hello")
    socket.recv_string()
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
    settings = Settings()
    settings.configure_logging('../logs/job_manager.log')

    #  Prepare our context and sockets
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect('tcp://%s:%d' % (settings.job_manager_api, settings.job_manager_router_port))

    REPOSITORY = None
    api.config.from_object(__name__)
    api.config.from_pyfile('../../cumulonimbi.jm.py', silent=True)
    if api.config['REPOSITORY'] is None:
        api.config['REPOSITORY'] = JobManagerRepository()

    broker = Broker()
    broker.start()

    api.run(host='%s' % settings.job_manager_api, debug=settings.debug)

    broker.stop()
    broker.join()

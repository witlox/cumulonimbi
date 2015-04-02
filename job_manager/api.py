"""
This is needed for 2.x and 3.x compatibility regarding imports
"""

from job_manager.broker import Broker
from bson.json_util import dumps
from job_manager.repository import JobManagerRepository
from flask import Flask, Response, request, jsonify
from settings import Settings
from os import path
import zmq


"""
This is the main api for the job manager, entry point to Cumulonimbi
"""
api = Flask(__name__, instance_relative_config=True)

"""
Create placeholder for broker with message queue
"""
api.broker = None

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
    if api.broker:
        api.broker.put_on_queue(job_name)
    return Response(dumps(response), mimetype='application/json')


@api.route('/jobs/<job_id>', methods=['PUT'])
def edit_job(job_id):
    repository = api.config['REPOSITORY']
    try:
        repository.update_job(job_id)
    except Exception, e:
        response = jsonify(message=str(e))
        response.status_code = 500
        return Response(response, mimetype='application/json')

    response = jsonify(message="OK")
    response.status_code = 200
    return Response(response, mimetype='application/json')



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


def start():
    """
    Run the JobManager API from here with the configured settings
    This is a blocking call
    """
    settings = Settings()
    logfile = path.dirname(path.dirname(path.abspath(__file__))) + '/logs/job_manager.log'
    settings.configure_logging(logfile)

    # configure storage
    api.config['REPOSITORY'] = settings.repository
    if api.config['REPOSITORY'] is None:
        api.config['REPOSITORY'] = JobManagerRepository()
    api.run(host=settings.job_manager_api, debug=settings.debug)

    # start non-blocking broker with queue
    api.broker = Broker()
    api.broker.start()

    # start flask
    api.run(host=settings.job_manager_api, debug=settings.debug)

    # cleanup
    api.broker.stop()
    api.broker.join()

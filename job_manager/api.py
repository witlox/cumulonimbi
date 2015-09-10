"""
This is needed for 2.x and 3.x compatibility regarding imports
"""

from os import path

# noinspection PyPackageRequirements
from bson.json_util import dumps
from flask import Flask, Response, request, jsonify

from flask_cors.crossdomain import crossdomain
from flask_swagger import swaggerify
from flask_swagger.swaggerify import swagger
from job_manager.azurebroker import AzureBroker
from job_manager.zmqbroker import ZmqBroker
from job_manager.repository import JobManagerRepository
from settings import Settings
from TransitionError import TransitionError
from StatusUnknownError import StatusUnknownError

"""
This is the main api for the job manager, entry point to Cumulonimbi
"""
api = Flask(__name__, instance_relative_config=True)

"""
Create placeholder for broker with message queue
"""
api.broker = None


def handle_invalid_usage(description, code):
    response = jsonify({"error": description})
    response.status_code = code
    return response


class AddJobParameter(object):
    def __init__(self):
        self.job_name = "string"
        self.graph = "string"


class UpdateStatusParameter(object):
    def __init__(self):
        self.status = "string"


class UpdateMachineParameter(object):
    def __init__(self):
        self.machine = "string"


class DefaultResponse(object):
    def __init__(self):
        self.job_id = "string"


class JobListResponse(object):
    def __init__(self):
        self.is_array = True
        self.status = "string"
        self.graph = "string"
        self.name = "string"


class DeleteJobsResponse(object):
    def __init__(self):
        self.n = "int"
        self.ok = "int"


@api.route('/swagger')
@crossdomain(api, origin='*')
def get_swagger():
    return Response(swaggerify.output_swagger(), mimetype='application/json')


@swagger('/jobs', 'GET', 'Get all jobs', JobListResponse())
@api.route('/jobs', methods=['GET', 'OPTIONS'])
@crossdomain(api, origin='*')
def get_jobs():
    """ Have to manually add OPTIONS path for anything but GET in cross-domain """
    repository = api.config['REPOSITORY']
    # jsonify does not play well with lists
    return Response(dumps(repository.get_all_jobs()), mimetype='application/json')


@swagger('/jobs', 'DELETE', 'Delete all jobs', DeleteJobsResponse())
@api.route('/jobs', methods=['DELETE'])
@crossdomain(api, origin='*')
def delete_jobs():
    repository = api.config['REPOSITORY']
    return jsonify(repository.delete_all_jobs())


@swagger('/jobs', 'POST', 'Add a new job', DefaultResponse(), AddJobParameter())
@api.route('/jobs', methods=['POST'])
@crossdomain(api, origin='*')
def create_job():
    try:
        data = request.get_json(force=True)
        repository = api.config['REPOSITORY']
        job_id = repository.insert_job(data["job_name"], data["graph"])
        response = {'job_id': job_id}
        if api.broker:
            api.broker.put_on_queue(job_id)
        return jsonify(response)
    except Exception as e:
        return handle_invalid_usage(e.description, e.code)


@swagger('/jobs/<job_id>/status', 'PUT', 'Update job status', DefaultResponse(), UpdateStatusParameter())
@api.route('/jobs/<job_id>/status', methods=['PUT'])
@crossdomain(api, origin='*')
def set_job_status(job_id):
    data = request.get_json(force=True)
    repository = api.config['REPOSITORY']
    try:
        repository.update_job_status(job_id, data["status"])
    except TransitionError as e:
        response = jsonify(message=str(e.message))
        response.status_code = 500
        return response
    except StatusUnknownError as e:
        response = jsonify(message=str(e.message))
        response.status_code = 500
        return response

    response = jsonify(message="OK")
    response.status_code = 200
    return response


@api.route('/jobs/<job_id>/machine', methods=['PUT'])
@crossdomain(api, origin='*')
def set_job_machine(job_id):
    data = request.get_json(force=True)
    repository = api.config['REPOSITORY']
    repository.update_job_machine(job_id, data["machine"])

    response = jsonify(message="OK")
    response.status_code = 200
    return response


@api.route('/jobs/<job_id>/<param>', methods=['GET'])
@api.route('/jobs/<job_id>', methods=['GET'])
@crossdomain(api, origin='*')
def get_job(job_id, param=None):
    repository = api.config['REPOSITORY']
    if param in ["status", "graph", "name"]:
        job = repository.get_job(job_id)
        response = jsonify({param: job[param]})
        response.status_code = 200
        return response
    else:
        response = repository.get_job(job_id)
        # jsonify does not play well with lists
        return Response(dumps(response), mimetype='application/json')


@api.route('/jobs/<job_id>', methods=['DELETE'])
@crossdomain(api, origin='*')
def delete_job(job_id):
    repository = api.config['REPOSITORY']
    response = repository.delete_job(job_id)
    return jsonify(job=response)


def start():
    """
    Run the JobManager API from here with the configured settings
    This is a blocking call
    """
    settings = Settings()
    settings.configure_logging('../logs/job_manager.log', 'JobManager')

    # configure storage
    api.config['REPOSITORY'] = settings.repository
    if api.config['REPOSITORY'] is None:
        api.config['REPOSITORY'] = JobManagerRepository()

    # configure swagger
    swaggerify.set_info("1.0.0", "Cumulonimbi Job Manager API", "The API for consumers of Cumulonimbi to use",
                        "Pim Witlox & Johannes Bertens")
    swaggerify.set_host(settings.job_manager_api_connect + ":" + str(settings.job_manager_api_port), "/", ["http"])

    # start non-blocking broker with queue
    # api.broker = ZmqBroker()
    api.broker = AzureBroker()
    api.broker.start()

    # start flask
    api.run(host=settings.job_manager_api_bind, port=settings.job_manager_api_port, debug=settings.debug)

    # cleanup
    api.broker.stop()
    api.broker.join()

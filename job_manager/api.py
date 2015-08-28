"""
This is needed for 2.x and 3.x compatibility regarding imports
"""
from functools import update_wrapper

from os import path

from bson.json_util import dumps
from datetime import timedelta
from flask import Flask, Response, request, jsonify, make_response

from job_manager.broker import Broker
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


def crossdomain(origin=None, methods=None, headers='Accept, Content-Type, Origin',
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    """
    Grabbed from Flask snippet 56: http://flask.pocoo.org/snippets/56/
    """
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = api.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = api.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)

    return decorator


class InvalidAPIUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


def handle_invalid_usage(description, code):
    response = jsonify({"error": description})
    response.status_code = code
    return response


@api.route('/swagger')
@crossdomain(origin='*')
def get_swagger():
    try:
        with open('job_manager/swagger.json', 'r') as f:
            return Response(f.read(), mimetype='application/json')
    except Exception as e:
        return e.message + e.description


@api.route('/jobs', methods=['OPTIONS'])
@crossdomain(origin='*')
def get_jobs_options():
    """ Have to manually add OPTIONS path for anything but GET in cross-domain """
    return "OK"


@api.route('/jobs', methods=['GET'])
@crossdomain(origin='*')
def get_jobs():
    repository = api.config['REPOSITORY']
    # jsonify does not play well with lists
    return Response(dumps(repository.get_all_jobs()), mimetype='application/json')


@api.route('/jobs', methods=['DELETE'])
@crossdomain(origin='*')
def delete_jobs():
    repository = api.config['REPOSITORY']
    return jsonify(repository.delete_all_jobs())


@api.route('/jobs', methods=['POST'])
@crossdomain(origin='*')
def create_job():
    try:
        data = request.get_json(force=True)
        repository = api.config['REPOSITORY']
        response = {'job_id': repository.insert_job(data["job_name"], data["graph"])}
        if api.broker:
            api.broker.put_on_queue(data["job_name"])
        return jsonify(response)
    except Exception as e:
        return handle_invalid_usage(e.description, e.code)


@api.route('/jobs/<job_id>/status', methods=['PUT'])
@crossdomain(origin='*')
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


@api.route('/jobs/<job_id>/<param>', methods=['GET'])
@api.route('/jobs/<job_id>', methods=['GET'])
@crossdomain(origin='*')
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
@crossdomain(origin='*')
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
    logfile = path.dirname(path.dirname(path.abspath(__file__))) + '/logs/job_manager.log'
    settings.configure_logging(logfile, 'JobManagerApi')

    # configure storage
    api.config['REPOSITORY'] = settings.repository
    if api.config['REPOSITORY'] is None:
        api.config['REPOSITORY'] = JobManagerRepository()

    # start non-blocking broker with queue
    api.broker = Broker()
    api.broker.start()

    # start flask
    api.run(host=settings.job_manager_api, debug=settings.debug)

    # cleanup
    api.broker.stop()
    api.broker.join()

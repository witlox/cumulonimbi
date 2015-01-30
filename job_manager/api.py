
__author__ = 'Johannes'

from bson.json_util import dumps
from repository import JobManagerRepository
from flask import Flask, Response, request

"""
This is the main api for the job manager
"""

api = Flask(__name__, instance_relative_config=True)

@api.route('/jobs', methods=['GET'])
def get_jobs():
    repository = api.config['REPOSITORY']
    response = dumps(repository.get_all_jobs())
    return Response(response, mimetype='application/json')


@api.route('/jobs', methods=['POST'])
def create_job():
    job_name = request.form['jobname']
    repository = api.config['REPOSITORY']
    response = {'job_id': repository.insert_job(job_name)}
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
    REPOSITORY = JobManagerRepository()
    api.config.from_object(__name__)
    api.config.from_pyfile('../../cumulonimbi.jm.py', silent=True)
    api.run(host='0.0.0.0', debug=True)

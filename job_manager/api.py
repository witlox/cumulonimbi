__author__ = 'Johannes'

from bson.json_util import dumps
from flask import Flask, Response, request
from job_manager.repository import JobManagerRepository

api = Flask(__name__)
repository = JobManagerRepository()


@api.route('/jobs', methods=['GET'])
def get_jobs():
    return Response(dumps(repository.get_all_jobs()), mimetype='application/json')


@api.route('/jobs', methods=['POST'])
def create_job():
    jobname = request.form['jobname']
    response = {'job_id': repository.insert_job(jobname)}
    return Response(dumps(response), mimetype='application/json')


@api.route('/jobs/<job_id>', methods=['PUT'])
def edit_job(job_id):
    pass


@api.route('/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    response = repository.get_job(job_id)
    return Response(dumps(response), mimetype='application/json')


@api.route('/jobs/<job_id>', methods=['DELETE'])
def delete_job(job_id):
    response = repository.delete_job(job_id)
    return Response(dumps(response), mimetype='application/json')


if __name__ == "__main__":
    api.run(debug=True)
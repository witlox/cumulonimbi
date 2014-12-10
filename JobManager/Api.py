__author__ = 'Johannes'

from bson.json_util import dumps
from flask import Flask, Response
from Repository import JobManagerRepository

api = Flask(__name__)
repository = JobManagerRepository()


@api.route('/jobs', methods=['GET'])
def get_jobs():
    return Response(dumps(repository.get_all_jobs()), mimetype='application/json')


@api.route('/jobs', methods=['POST'])
def create_job():
    response = {'job_id': repository.insert_job('second job')}
    return Response(dumps(response), mimetype='application/json')


@api.route('/jobs/:job_id', methods=['PUT'])
def edit_job(job_id):
    pass


@api.route('/jobs/:job_id', methods=['GET'])
def get_job(job_id):
    pass


@api.route('/jobs/:job_id', methods=['DELETE'])
def delete_job(job_id):
    pass


if __name__ == "__main__":
    api.run(debug=True)
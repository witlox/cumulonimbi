__author__ = 'Johannes'

""" This is needed for 2.x and 3.x compatibility regarding imports """
if __name__ == '__main__' and __package__ is None:
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from bson.json_util import dumps
from job_manager.repository import JobManagerRepository
from flask import Flask, Response, request

import logging
import logstash

host = 'localhost'

"""
This is the main api for the job manager, entry point to Cumulonimbi
"""
api = Flask(__name__, instance_relative_config=True, )

@api.route('/jobs', methods=['GET'])
def get_jobs():
    logging.warn("GET /jobs")
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
    REPOSITORY = None
    api.config.from_object(__name__)
    api.config.from_pyfile('../../cumulonimbi.jm.py', silent=True)
    if api.config['REPOSITORY'] is None:
        api.config['REPOSITORY'] = JobManagerRepository()

    import logging
    from logging.handlers import RotatingFileHandler
    formatter = logging.Formatter("%(asctime)s[%(levelname)s](%(lineno)s-%(funcName)s()):%(message)s")
    file_handler = RotatingFileHandler('jobmanager_api.log', maxBytes=1024 * 1024 * 100, backupCount=20)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logstash_handler = logstash.LogstashHandler(host, 9200, version=1)
    logstash_handler.setLevel(logging.INFO)
    logstash_handler.setFormatter(formatter)
    api.logger.addHandler(file_handler)
    api.logger.addHandler(logstash_handler)

    api.run(host='0.0.0.0')

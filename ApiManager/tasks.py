# Create your tasks here
from __future__ import absolute_import, unicode_literals

from celery import shared_task

from ApiManager.utils.operation import add_test_reports
from ApiManager.utils.runner import run_by_project
from httprunner import HttpRunner, logger


@shared_task
def main_hrun(testset_path):
    logger.setup_logger('DEBUG')
    kwargs = {
        "failfast": False,
    }
    runner = HttpRunner(**kwargs)
    runner.run(testset_path)
    add_test_reports(**runner.summary)
    return runner.summary


@shared_task
def periodic_hrun(testset_path):
    testcases_dict = []
    base_url = testset_path.pop('env_name')
    if 'project' in testset_path.keys():
        id = testset_path.pop('project')
        testcases_dict = run_by_project(id, base_url)
    return main_hrun(testcases_dict)

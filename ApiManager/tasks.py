# Create your tasks here
from __future__ import absolute_import, unicode_literals

from celery import shared_task

from ApiManager.utils.operation import add_test_reports
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

# Create your tasks here
from __future__ import absolute_import, unicode_literals

from celery import shared_task

from ApiManager.models import TestReports
from httprunner import HttpRunner


@shared_task
def main_hrun(testset_path):
    kwargs = {
        "failfast": False,
    }
    runner = HttpRunner(**kwargs)
    runner.run(testset_path)
    TestReports.objects.create(report_name=runner.summary['time']['start_at'], reports=runner.summary,
                               status=runner.summary['success'])
    return runner.summary

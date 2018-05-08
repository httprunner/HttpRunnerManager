# Create your tasks here
from __future__ import absolute_import, unicode_literals

import time

from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist

from ApiManager.models import ProjectInfo, ModuleInfo
from ApiManager.utils.operation import add_test_reports
from ApiManager.utils.runner import run_by_project, run_by_module
from httprunner import HttpRunner, logger


@shared_task
def main_hrun(testset_path, report_name):
    logger.setup_logger('DEBUG')
    kwargs = {
        "failfast": False,
    }
    runner = HttpRunner(**kwargs)
    run_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    runner.run(testset_path)
    add_test_reports(run_time, report_name=report_name, **runner.summary)
    return runner.summary


@shared_task
def project_hrun(env_name, project):
    logger.setup_logger('DEBUG')
    kwargs = {
        "failfast": False,
    }
    runner = HttpRunner(**kwargs)
    id = ProjectInfo.objects.get(project_name=project).id
    testcases_dict = run_by_project(id, env_name)

    run_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    runner.run(testcases_dict)
    add_test_reports(run_time, report_name=project, **runner.summary)
    return runner.summary


@shared_task
def module_hrun(env_name, project, module):
    logger.setup_logger('DEBUG')
    kwargs = {
        "failfast": False,
    }
    runner = HttpRunner(**kwargs)
    testcase_lists = []
    module = module.split(',')
    try:
        for module_name in module:
            id = ModuleInfo.objects.get(module_name__exact=module_name, belong_project__project_name=project).id
            testcase_lists.extend(run_by_module(id, env_name))
    except ObjectDoesNotExist:
        return '找不到模块信息'
    run_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    runner.run(testcase_lists)
    add_test_reports(run_time, report_name=project, **runner.summary)
    return runner.summary

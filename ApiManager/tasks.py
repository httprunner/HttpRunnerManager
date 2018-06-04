# Create your tasks here
from __future__ import absolute_import, unicode_literals

import time

from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist

from ApiManager.models import ProjectInfo
from ApiManager.utils.operation import add_test_reports
from ApiManager.utils.runner import run_by_project, run_by_module
from httprunner import HttpRunner, logger


@shared_task
def main_hrun(testset_path, report_name):
    """
    用例运行
    :param testset_path: dict or list
    :param report_name: str
    :return:
    """
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
def project_hrun(name, base_url, project):
    """
    异步运行整个项目
    :param env_name: str: 环境地址
    :param project: str
    :return:
    """
    logger.setup_logger('DEBUG')
    kwargs = {
        "failfast": False,
    }
    runner = HttpRunner(**kwargs)
    id = ProjectInfo.objects.get(project_name=project).id
    testcases_dict = run_by_project(id, base_url)

    run_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    runner.run(testcases_dict)
    add_test_reports(run_time, report_name=name, **runner.summary)
    return runner.summary


@shared_task
def module_hrun(name, base_url, module):
    """
    异步运行模块
    :param env_name: str: 环境地址
    :param project: str：项目所属模块
    :param module: str：模块名称
    :return:
    """
    logger.setup_logger('DEBUG')
    kwargs = {
        "failfast": False,
    }
    runner = HttpRunner(**kwargs)
    testcase_lists = []
    module = list(module)
    try:
        for value in module:
            testcase_lists.extend(run_by_module(value[0], base_url))
    except ObjectDoesNotExist:
        return '找不到模块信息'
    run_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    runner.run(testcase_lists)
    add_test_reports(run_time, report_name=name, **runner.summary)
    return runner.summary

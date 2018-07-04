# Create your tasks here
from __future__ import absolute_import, unicode_literals

import os
import shutil
import time

from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist

from ApiManager.models import ProjectInfo
from ApiManager.utils.emails import send_email_reports
from ApiManager.utils.operation import add_test_reports
from ApiManager.utils.runner import run_by_project, run_by_module, run_by_suite
from ApiManager.utils.testcase import get_time_stamp
from httprunner import HttpRunner, logger


@shared_task
def main_hrun(testset_path, report_name):
    """
    用例运行
    :param testset_path: dict or list
    :param report_name: str
    :return:
    """
    logger.setup_logger('INFO')
    kwargs = {
        "failfast": False,
    }
    runner = HttpRunner(**kwargs)
    run_time = time.strftime('%Y-%m-%d %H-%M-%S', time.localtime(time.time()))
    runner.run(testset_path)
    shutil.rmtree(testset_path)
    add_test_reports(run_time, report_name=report_name, **runner.summary)
    return runner.summary


@shared_task
def project_hrun(name, base_url, project, receiver):
    """
    异步运行整个项目
    :param env_name: str: 环境地址
    :param project: str
    :return:
    """
    logger.setup_logger('INFO')
    kwargs = {
        "failfast": False,
    }
    runner = HttpRunner(**kwargs)
    id = ProjectInfo.objects.get(project_name=project).id

    testcase_dir_path = os.path.join(os.getcwd(), "suite")
    testcase_dir_path = os.path.join(testcase_dir_path, get_time_stamp())

    run_by_project(id, base_url, testcase_dir_path)

    run_time = time.strftime('%Y-%m-%d %H-%M-%S', time.localtime(time.time()))
    runner.run(testcase_dir_path)

    shutil.rmtree(testcase_dir_path)
    add_test_reports(run_time, report_name=name, **runner.summary)

    if receiver != '':
        send_html_reports(receiver, runner)

    return runner.summary


@shared_task
def module_hrun(name, base_url, module, receiver):
    """
    异步运行模块
    :param env_name: str: 环境地址
    :param project: str：项目所属模块
    :param module: str：模块名称
    :return:
    """
    logger.setup_logger('INFO')
    kwargs = {
        "failfast": False,
    }
    runner = HttpRunner(**kwargs)
    module = list(module)

    testcase_dir_path = os.path.join(os.getcwd(), "suite")
    testcase_dir_path = os.path.join(testcase_dir_path, get_time_stamp())

    try:
        for value in module:
            run_by_module(value[0], base_url, testcase_dir_path)
    except ObjectDoesNotExist:
        return '找不到模块信息'
    run_time = time.strftime('%Y-%m-%d %H-%M-%S', time.localtime(time.time()))
    runner.run(testcase_dir_path)

    shutil.rmtree(testcase_dir_path)
    add_test_reports(run_time, report_name=name, **runner.summary)

    if receiver != '':
        send_html_reports(receiver, runner)

    return runner.summary


@shared_task
def suite_hrun(name, base_url, suite, receiver):
    """
    异步运行模块
    :param env_name: str: 环境地址
    :param project: str：项目所属模块
    :param module: str：模块名称
    :return:
    """
    logger.setup_logger('INFO')
    kwargs = {
        "failfast": False,
    }
    runner = HttpRunner(**kwargs)
    suite = list(suite)

    testcase_dir_path = os.path.join(os.getcwd(), "suite")
    testcase_dir_path = os.path.join(testcase_dir_path, get_time_stamp())

    try:
        for value in suite:
            run_by_suite(value[0], base_url, testcase_dir_path)
    except ObjectDoesNotExist:
        return '找不到Suite信息'

    run_time = time.strftime('%Y-%m-%d %H-%M-%S', time.localtime(time.time()))
    runner.run(testcase_dir_path)

    shutil.rmtree(testcase_dir_path)
    add_test_reports(run_time, report_name=name, **runner.summary)

    if receiver != '':
        send_html_reports(receiver, runner)

    return runner.summary


def send_html_reports(receiver, runner):
    report_dir_path = os.path.join(os.getcwd(), "reports")

    if os.path.exists(report_dir_path):
        shutil.rmtree(report_dir_path)

    html_report_name = runner.summary.get('time')['start_at'] + '.html'
    report_dir_path = os.path.join(report_dir_path, html_report_name)

    runner.gen_html_report()

    send_email_reports(receiver, report_dir_path)

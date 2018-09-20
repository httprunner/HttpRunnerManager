import json
import logging
import os
import shutil
import sys

import paramiko
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, StreamingHttpResponse
from django.shortcuts import render_to_response
from django.utils.safestring import mark_safe
from djcelery.models import PeriodicTask
from dwebsocket import accept_websocket

from ApiManager import separator
from ApiManager.models import ProjectInfo, ModuleInfo, TestCaseInfo, UserInfo, EnvInfo, TestReports, DebugTalk, \
    TestSuite
from ApiManager.tasks import main_hrun
from ApiManager.utils.common import module_info_logic, project_info_logic, case_info_logic, config_info_logic, \
    set_filter_session, get_ajax_msg, register_info_logic, task_logic, load_modules, upload_file_logic, \
    init_filter_session, get_total_values, timestamp_to_datetime
from ApiManager.utils.operation import env_data_logic, del_module_data, del_project_data, del_test_data, copy_test_data, \
    del_report_data, add_suite_data, copy_suite_data, del_suite_data, edit_suite_data, add_test_reports
from ApiManager.utils.pagination import get_pager_info
from ApiManager.utils.runner import run_by_batch, run_test_by_type
from ApiManager.utils.task_opt import delete_task, change_task_status
from ApiManager.utils.testcase import get_time_stamp
from httprunner import HttpRunner

logger = logging.getLogger('HttpRunnerManager')

# Create your views here.



def login_check(func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('login_status'):
            return HttpResponseRedirect('/api/login/')
        return func(request, *args, **kwargs)

    return wrapper


def login(request):
    """
    登录
    :param request:
    :return:
    """
    if request.method == 'POST':
        username = request.POST.get('account')
        password = request.POST.get('password')

        if UserInfo.objects.filter(username__exact=username).filter(password__exact=password).count() == 1:
            logger.info('{username} 登录成功'.format(username=username))
            request.session["login_status"] = True
            request.session["now_account"] = username
            return HttpResponseRedirect('/api/index/')
        else:
            logger.info('{username} 登录失败, 请检查用户名或者密码'.format(username=username))
            request.session["login_status"] = False
            return render_to_response("login.html")
    elif request.method == 'GET':
        return render_to_response("login.html")


def register(request):
    """
    注册
    :param request:
    :return:
    """
    if request.is_ajax():
        user_info = json.loads(request.body.decode('utf-8'))
        msg = register_info_logic(**user_info)
        return HttpResponse(get_ajax_msg(msg, '恭喜您，账号已成功注册'))
    elif request.method == 'GET':
        return render_to_response("register.html")


@login_check
def log_out(request):
    """
    注销登录
    :param request:
    :return:
    """
    if request.method == 'GET':
        logger.info('{username}退出'.format(username=request.session['now_account']))
        try:
            del request.session['now_account']
            del request.session['login_status']
            init_filter_session(request, type=False)
        except KeyError:
            logging.error('session invalid')
        return HttpResponseRedirect("/api/login/")


@login_check
def index(request):
    """
    首页
    :param request:
    :return:
    """
    project_length = ProjectInfo.objects.count()
    module_length = ModuleInfo.objects.count()
    test_length = TestCaseInfo.objects.filter(type__exact=1).count()
    suite_length = TestSuite.objects.count()

    total = get_total_values()
    manage_info = {
        'project_length': project_length,
        'module_length': module_length,
        'test_length': test_length,
        'suite_length': suite_length,
        'account': request.session["now_account"],
        'total': total
    }

    init_filter_session(request)
    return render_to_response('index.html', manage_info)


@login_check
def add_project(request):
    """
    新增项目
    :param request:
    :return:
    """
    account = request.session["now_account"]
    if request.is_ajax():
        project_info = json.loads(request.body.decode('utf-8'))
        msg = project_info_logic(**project_info)
        return HttpResponse(get_ajax_msg(msg, '/api/project_list/1/'))

    elif request.method == 'GET':
        manage_info = {
            'account': account
        }
        return render_to_response('add_project.html', manage_info)


@login_check
def add_module(request):
    """
    新增模块
    :param request:
    :return:
    """
    account = request.session["now_account"]
    if request.is_ajax():
        module_info = json.loads(request.body.decode('utf-8'))
        msg = module_info_logic(**module_info)
        return HttpResponse(get_ajax_msg(msg, '/api/module_list/1/'))
    elif request.method == 'GET':
        manage_info = {
            'account': account,
            'data': ProjectInfo.objects.all().values('project_name')
        }
        return render_to_response('add_module.html', manage_info)


@login_check
def add_case(request):
    """
    新增用例
    :param request:
    :return:
    """
    account = request.session["now_account"]
    if request.is_ajax():
        testcase_info = json.loads(request.body.decode('utf-8'))
        msg = case_info_logic(**testcase_info)
        return HttpResponse(get_ajax_msg(msg, '/api/test_list/1/'))
    elif request.method == 'GET':
        manage_info = {
            'account': account,
            'project': ProjectInfo.objects.all().values('project_name').order_by('-create_time')
        }
        return render_to_response('add_case.html', manage_info)


@login_check
def add_config(request):
    """
    新增配置
    :param request:
    :return:
    """
    account = request.session["now_account"]
    if request.is_ajax():
        testconfig_info = json.loads(request.body.decode('utf-8'))
        msg = config_info_logic(**testconfig_info)
        return HttpResponse(get_ajax_msg(msg, '/api/config_list/1/'))
    elif request.method == 'GET':
        manage_info = {
            'account': account,
            'project': ProjectInfo.objects.all().values('project_name').order_by('-create_time')
        }
        return render_to_response('add_config.html', manage_info)


@login_check
def run_test(request):
    """
    运行用例
    :param request:
    :return:
    """

    kwargs = {
        "failfast": False,
    }
    runner = HttpRunner(**kwargs)

    testcase_dir_path = os.path.join(os.getcwd(), "suite")
    testcase_dir_path = os.path.join(testcase_dir_path, get_time_stamp())

    if request.is_ajax():
        kwargs = json.loads(request.body.decode('utf-8'))
        id = kwargs.pop('id')
        base_url = kwargs.pop('env_name')
        type = kwargs.pop('type')
        run_test_by_type(id, base_url, testcase_dir_path, type)
        report_name = kwargs.get('report_name', None)
        main_hrun.delay(testcase_dir_path, report_name)
        return HttpResponse('用例执行中，请稍后查看报告即可,默认时间戳命名报告')
    else:
        id = request.POST.get('id')
        base_url = request.POST.get('env_name')
        type = request.POST.get('type', 'test')

        run_test_by_type(id, base_url, testcase_dir_path, type)
        runner.run(testcase_dir_path)
        shutil.rmtree(testcase_dir_path)
        runner.summary = timestamp_to_datetime(runner.summary, type=False)

        return render_to_response('report_template.html', runner.summary)


@login_check
def run_batch_test(request):
    """
    批量运行用例
    :param request:
    :return:
    """

    kwargs = {
        "failfast": False,
    }
    runner = HttpRunner(**kwargs)

    testcase_dir_path = os.path.join(os.getcwd(), "suite")
    testcase_dir_path = os.path.join(testcase_dir_path, get_time_stamp())

    if request.is_ajax():
        kwargs = json.loads(request.body.decode('utf-8'))
        test_list = kwargs.pop('id')
        base_url = kwargs.pop('env_name')
        type = kwargs.pop('type')
        report_name = kwargs.get('report_name', None)
        run_by_batch(test_list, base_url, testcase_dir_path, type=type)
        main_hrun.delay(testcase_dir_path, report_name)
        return HttpResponse('用例执行中，请稍后查看报告即可,默认时间戳命名报告')
    else:
        type = request.POST.get('type', None)
        base_url = request.POST.get('env_name')
        test_list = request.body.decode('utf-8').split('&')
        if type:
            run_by_batch(test_list, base_url, testcase_dir_path, type=type, mode=True)
        else:
            run_by_batch(test_list, base_url, testcase_dir_path)

        runner.run(testcase_dir_path)

        shutil.rmtree(testcase_dir_path)
        runner.summary = timestamp_to_datetime(runner.summary,type=False)

        return render_to_response('report_template.html', runner.summary)


@login_check
def project_list(request, id):
    """
    项目列表
    :param request:
    :param id: str or int：当前页
    :return:
    """

    account = request.session["now_account"]
    if request.is_ajax():
        project_info = json.loads(request.body.decode('utf-8'))
        if 'mode' in project_info.keys():
            msg = del_project_data(project_info.pop('id'))
        else:
            msg = project_info_logic(type=False, **project_info)
        return HttpResponse(get_ajax_msg(msg, 'ok'))
    else:
        filter_query = set_filter_session(request)
        pro_list = get_pager_info(
            ProjectInfo, filter_query, '/api/project_list/', id)
        manage_info = {
            'account': account,
            'project': pro_list[1],
            'page_list': pro_list[0],
            'info': filter_query,
            'sum': pro_list[2],
            'env': EnvInfo.objects.all().order_by('-create_time'),
            'project_all': ProjectInfo.objects.all().order_by('-update_time')
        }
        return render_to_response('project_list.html', manage_info)


@login_check
def module_list(request, id):
    """
    模块列表
    :param request:
    :param id: str or int：当前页
    :return:
    """
    account = request.session["now_account"]
    if request.is_ajax():
        module_info = json.loads(request.body.decode('utf-8'))
        if 'mode' in module_info.keys():  # del module
            msg = del_module_data(module_info.pop('id'))
        else:
            msg = module_info_logic(type=False, **module_info)
        return HttpResponse(get_ajax_msg(msg, 'ok'))
    else:
        filter_query = set_filter_session(request)
        module_list = get_pager_info(
            ModuleInfo, filter_query, '/api/module_list/', id)
        manage_info = {
            'account': account,
            'module': module_list[1],
            'page_list': module_list[0],
            'info': filter_query,
            'sum': module_list[2],
            'env': EnvInfo.objects.all().order_by('-create_time'),
            'project': ProjectInfo.objects.all().order_by('-update_time')
        }
        return render_to_response('module_list.html', manage_info)


@login_check
def test_list(request, id):
    """
    用例列表
    :param request:
    :param id: str or int：当前页
    :return:
    """

    account = request.session["now_account"]
    if request.is_ajax():
        test_info = json.loads(request.body.decode('utf-8'))

        if test_info.get('mode') == 'del':
            msg = del_test_data(test_info.pop('id'))
        elif test_info.get('mode') == 'copy':
            msg = copy_test_data(test_info.get('data').pop('index'), test_info.get('data').pop('name'))
        return HttpResponse(get_ajax_msg(msg, 'ok'))

    else:
        filter_query = set_filter_session(request)
        test_list = get_pager_info(
            TestCaseInfo, filter_query, '/api/test_list/', id)
        manage_info = {
            'account': account,
            'test': test_list[1],
            'page_list': test_list[0],
            'info': filter_query,
            'env': EnvInfo.objects.all().order_by('-create_time'),
            'project': ProjectInfo.objects.all().order_by('-update_time')
        }
        return render_to_response('test_list.html', manage_info)


@login_check
def config_list(request, id):
    """
    配置列表
    :param request:
    :param id: str or int：当前页
    :return:
    """
    account = request.session["now_account"]
    if request.is_ajax():
        test_info = json.loads(request.body.decode('utf-8'))

        if test_info.get('mode') == 'del':
            msg = del_test_data(test_info.pop('id'))
        elif test_info.get('mode') == 'copy':
            msg = copy_test_data(test_info.get('data').pop('index'), test_info.get('data').pop('name'))
        return HttpResponse(get_ajax_msg(msg, 'ok'))
    else:
        filter_query = set_filter_session(request)
        test_list = get_pager_info(
            TestCaseInfo, filter_query, '/api/config_list/', id)
        manage_info = {
            'account': account,
            'test': test_list[1],
            'page_list': test_list[0],
            'info': filter_query,
            'project': ProjectInfo.objects.all().order_by('-update_time')
        }
        return render_to_response('config_list.html', manage_info)


@login_check
def edit_case(request, id=None):
    """
    编辑用例
    :param request:
    :param id:
    :return:
    """

    account = request.session["now_account"]
    if request.is_ajax():
        testcase_lists = json.loads(request.body.decode('utf-8'))
        msg = case_info_logic(type=False, **testcase_lists)
        return HttpResponse(get_ajax_msg(msg, '/api/test_list/1/'))

    test_info = TestCaseInfo.objects.get_case_by_id(id)
    request = eval(test_info[0].request)
    include = eval(test_info[0].include)
    manage_info = {
        'account': account,
        'info': test_info[0],
        'request': request['test'],
        'include': include,
        'project': ProjectInfo.objects.all().values('project_name').order_by('-create_time')
    }
    return render_to_response('edit_case.html', manage_info)


@login_check
def edit_config(request, id=None):
    """
    编辑配置
    :param request:
    :param id:
    :return:
    """

    account = request.session["now_account"]
    if request.is_ajax():
        testconfig_lists = json.loads(request.body.decode('utf-8'))
        msg = config_info_logic(type=False, **testconfig_lists)
        return HttpResponse(get_ajax_msg(msg, '/api/config_list/1/'))

    config_info = TestCaseInfo.objects.get_case_by_id(id)
    request = eval(config_info[0].request)
    manage_info = {
        'account': account,
        'info': config_info[0],
        'request': request['config'],
        'project': ProjectInfo.objects.all().values(
            'project_name').order_by('-create_time')
    }
    return render_to_response('edit_config.html', manage_info)


@login_check
def env_set(request):
    """
    环境设置
    :param request:
    :return:
    """

    account = request.session["now_account"]
    if request.is_ajax():
        env_lists = json.loads(request.body.decode('utf-8'))
        msg = env_data_logic(**env_lists)
        return HttpResponse(get_ajax_msg(msg, 'ok'))

    elif request.method == 'GET':
        return render_to_response('env_list.html', {'account': account})


@login_check
def env_list(request, id):
    """
    环境列表
    :param request:
    :param id: str or int：当前页
    :return:
    """

    account = request.session["now_account"]
    if request.method == 'GET':
        env_lists = get_pager_info(
            EnvInfo, None, '/api/env_list/', id)
        manage_info = {
            'account': account,
            'env': env_lists[1],
            'page_list': env_lists[0],
        }
        return render_to_response('env_list.html', manage_info)


@login_check
def report_list(request, id):
    """
    报告列表
    :param request:
    :param id: str or int：当前页
    :return:
    """

    if request.is_ajax():
        report_info = json.loads(request.body.decode('utf-8'))

        if report_info.get('mode') == 'del':
            msg = del_report_data(report_info.pop('id'))
        return HttpResponse(get_ajax_msg(msg, 'ok'))
    else:
        filter_query = set_filter_session(request)
        report_list = get_pager_info(
            TestReports, filter_query, '/api/report_list/', id)
        manage_info = {
            'account': request.session["now_account"],
            'report': report_list[1],
            'page_list': report_list[0],
            'info': filter_query
        }
        return render_to_response('report_list.html', manage_info)


@login_check
def view_report(request, id):
    """
    查看报告
    :param request:
    :param id: str or int：报告名称索引
    :return:
    """
    reports = TestReports.objects.get(id=id).reports
    return render_to_response('view_report.html', {"reports": mark_safe(reports)})


@login_check
def periodictask(request, id):
    """
    定时任务列表
    :param request:
    :param id: str or int：当前页
    :return:
    """

    account = request.session["now_account"]
    if request.is_ajax():
        kwargs = json.loads(request.body.decode('utf-8'))
        mode = kwargs.pop('mode')
        id = kwargs.pop('id')
        msg = delete_task(id) if mode == 'del' else change_task_status(id, mode)
        return HttpResponse(get_ajax_msg(msg, 'ok'))
    else:
        filter_query = set_filter_session(request)
        task_list = get_pager_info(
            PeriodicTask, filter_query, '/api/periodictask/', id)
        manage_info = {
            'account': account,
            'task': task_list[1],
            'page_list': task_list[0],
            'info': filter_query
        }
    return render_to_response('periodictask_list.html', manage_info)


@login_check
def add_task(request):
    """
    添加任务
    :param request:
    :return:
    """

    account = request.session["now_account"]
    if request.is_ajax():
        kwargs = json.loads(request.body.decode('utf-8'))
        msg = task_logic(**kwargs)
        return HttpResponse(get_ajax_msg(msg, '/api/periodictask/1/'))
    elif request.method == 'GET':
        info = {
            'account': account,
            'env': EnvInfo.objects.all().order_by('-create_time'),
            'project': ProjectInfo.objects.all().order_by('-create_time')
        }
        return render_to_response('add_task.html', info)


@login_check
def upload_file(request):
    account = request.session["now_account"]
    if request.method == 'POST':
        try:
            project_name = request.POST.get('project')
            module_name = request.POST.get('module')
        except KeyError as e:
            return JsonResponse({"status": e})

        if project_name == '请选择' or module_name == '请选择':
            return JsonResponse({"status": '项目或模块不能为空'})

        upload_path = sys.path[0] + separator + 'upload' + separator

        if os.path.exists(upload_path):
            shutil.rmtree(upload_path)

        os.mkdir(upload_path)

        upload_obj = request.FILES.getlist('upload')
        file_list = []
        for i in range(len(upload_obj)):
            temp_path = upload_path + upload_obj[i].name
            file_list.append(temp_path)
            try:
                with open(temp_path, 'wb') as data:
                    for line in upload_obj[i].chunks():
                        data.write(line)
            except IOError as e:
                return JsonResponse({"status": e})

        upload_file_logic(file_list, project_name, module_name, account)

        return JsonResponse({'status': '/api/test_list/1/'})


@login_check
def get_project_info(request):
    """
     获取项目相关信息
     :param request:
     :return:
     """

    if request.is_ajax():
        project_info = json.loads(request.body.decode('utf-8'))

        msg = load_modules(**project_info.pop('task'))
        return HttpResponse(msg)


@login_check
def download_report(request, id):
    if request.method == 'GET':

        summary = TestReports.objects.get(id=id)
        reports = summary.reports
        start_at = summary.start_at

        if os.path.exists(os.path.join(os.getcwd(), "reports")):
            shutil.rmtree(os.path.join(os.getcwd(), "reports"))
        os.makedirs(os.path.join(os.getcwd(), "reports"))

        report_path = os.path.join(os.getcwd(), "reports{}{}.html".format(separator, start_at.replace(":", "-")))
        with open(report_path, 'w+', encoding='utf-8') as stream:
            stream.write(reports)

        def file_iterator(file_name, chunk_size=512):
            with open(file_name, encoding='utf-8') as f:
                while True:
                    c = f.read(chunk_size)
                    if c:
                        yield c
                    else:
                        break

        response = StreamingHttpResponse(file_iterator(report_path))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format(start_at.replace(":", "-") + '.html')
        return response


@login_check
def debugtalk(request, id=None):
    if request.method == 'GET':
        debugtalk = DebugTalk.objects.values('id', 'debugtalk').get(id=id)
        return render_to_response('debugtalk.html', debugtalk)
    else:
        id = request.POST.get('id')
        debugtalk = request.POST.get('debugtalk')
        code = debugtalk.replace('new_line', '\r\n')
        obj = DebugTalk.objects.get(id=id)
        obj.debugtalk = code
        obj.save()
        return HttpResponseRedirect('/api/debugtalk_list/1/')


@login_check
def debugtalk_list(request, id):
    """
       debugtalk.py列表
       :param request:
       :param id: str or int：当前页
       :return:
       """

    account = request.session["now_account"]
    debugtalk = get_pager_info(
        DebugTalk, None, '/api/debugtalk_list/', id)
    manage_info = {
        'account': account,
        'debugtalk': debugtalk[1],
        'page_list': debugtalk[0],
    }
    return render_to_response('debugtalk_list.html', manage_info)


@login_check
def suite_list(request, id):
    account = request.session["now_account"]
    if request.is_ajax():
        suite_info = json.loads(request.body.decode('utf-8'))

        if suite_info.get('mode') == 'del':
            msg = del_suite_data(suite_info.pop('id'))
        elif suite_info.get('mode') == 'copy':
            msg = copy_suite_data(suite_info.get('data').pop('index'), suite_info.get('data').pop('name'))
        return HttpResponse(get_ajax_msg(msg, 'ok'))
    else:
        filter_query = set_filter_session(request)
        pro_list = get_pager_info(
            TestSuite, filter_query, '/api/suite_list/', id)
        manage_info = {
            'account': account,
            'suite': pro_list[1],
            'page_list': pro_list[0],
            'info': filter_query,
            'sum': pro_list[2],
            'env': EnvInfo.objects.all().order_by('-create_time'),
            'project': ProjectInfo.objects.all().order_by('-update_time')
        }
        return render_to_response('suite_list.html', manage_info)


@login_check
def add_suite(request):
    account = request.session["now_account"]
    if request.is_ajax():
        kwargs = json.loads(request.body.decode('utf-8'))
        msg = add_suite_data(**kwargs)
        return HttpResponse(get_ajax_msg(msg, '/api/suite_list/1/'))

    elif request.method == 'GET':
        manage_info = {
            'account': account,
            'project': ProjectInfo.objects.all().values('project_name').order_by('-create_time')
        }
        return render_to_response('add_suite.html', manage_info)


@login_check
def edit_suite(request, id=None):
    account = request.session["now_account"]
    if request.is_ajax():
        kwargs = json.loads(request.body.decode('utf-8'))
        msg = edit_suite_data(**kwargs)
        return HttpResponse(get_ajax_msg(msg, '/api/suite_list/1/'))

    suite_info = TestSuite.objects.get(id=id)
    manage_info = {
        'account': account,
        'info': suite_info,
        'project': ProjectInfo.objects.all().values(
            'project_name').order_by('-create_time')
    }
    return render_to_response('edit_suite.html', manage_info)


@login_check
@accept_websocket
def echo(request):
    if not request.is_websocket():
        return render_to_response('echo.html')
    else:
        servers = []
        for message in request.websocket:
            try:
                servers.append(message.decode('utf-8'))
            except AttributeError:
                pass
            if len(servers) == 4:
                break
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(servers[0], 22, username=servers[1], password=servers[2], timeout=10)
        while True:
            cmd = servers[3]
            stdin, stdout, stderr = client.exec_command(cmd)
            for i, line in enumerate(stdout):
                request.websocket.send(bytes(line, encoding='utf8'))
            client.close()

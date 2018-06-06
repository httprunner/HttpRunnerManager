import json
import logging
import os
import platform
import shutil
import sys

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, StreamingHttpResponse
from django.shortcuts import render_to_response
from djcelery.models import PeriodicTask

from ApiManager.models import ProjectInfo, ModuleInfo, TestCaseInfo, UserInfo, EnvInfo, TestReports
from ApiManager.tasks import main_hrun
from ApiManager.utils.common import module_info_logic, project_info_logic, case_info_logic, config_info_logic, \
    set_filter_session, get_ajax_msg, register_info_logic, task_logic, load_modules, upload_file_logic, \
    init_filter_session, get_total_values
from ApiManager.utils.operation import env_data_logic, del_module_data, del_project_data, del_test_data, copy_test_data, \
    del_report_data
from ApiManager.utils.pagination import get_pager_info
from ApiManager.utils.runner import run_by_single, run_by_batch, run_by_module, run_by_project
from ApiManager.utils.task_opt import delete_task, change_task_status
from httprunner import HttpRunner

logger = logging.getLogger('HttpRunnerManager')


# Create your views here.


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


def index(request):
    """
    首页
    :param request:
    :return:
    """
    if request.session.get('login_status'):
        project_length = ProjectInfo.objects.count()
        module_length = ModuleInfo.objects.count()
        test_length = TestCaseInfo.objects.filter(type__exact=1).count()
        config_length = TestCaseInfo.objects.filter(type__exact=2).count()

        total = get_total_values()
        manage_info = {
            'project_length': project_length,
            'module_length': module_length,
            'test_length': test_length,
            'config_length': config_length,
            'account': request.session["now_account"],
            'total': total
        }

        init_filter_session(request)
        return render_to_response('index.html', manage_info)
    else:
        return HttpResponseRedirect("/api/login/")


def add_project(request):
    """
    新增项目
    :param request:
    :return:
    """
    if request.session.get('login_status'):
        acount = request.session["now_account"]
        if request.is_ajax():
            try:
                project_info = json.loads(request.body.decode('utf-8'))
            except ValueError:
                logger.error('项目信息解析异常: {project_info}'.format(project_info=project_info))
                return HttpResponse('项目信息新增异常')
            msg = project_info_logic(**project_info)
            return HttpResponse(get_ajax_msg(msg, '/api/project_list/1/'))

        elif request.method == 'GET':
            manage_info = {
                'account': acount
            }
            return render_to_response('add_project.html', manage_info)
    else:
        return HttpResponseRedirect("/api/login/")


def add_module(request):
    """
    新增模块
    :param request:
    :return:
    """
    if request.session.get('login_status'):
        acount = request.session["now_account"]
        if request.is_ajax():
            try:
                module_info = json.loads(request.body.decode('utf-8'))
            except ValueError:
                logger.error('模块信息解析异常：{module_info}'.format(module_info=module_info))
            msg = module_info_logic(**module_info)
            return HttpResponse(get_ajax_msg(msg, '/api/module_list/1/'))
        elif request.method == 'GET':
            manage_info = {
                'account': acount,
                'data': ProjectInfo.objects.all().values('project_name')
            }
            return render_to_response('add_module.html', manage_info)
    else:
        return HttpResponseRedirect("/api/login/")


def add_case(request):
    """
    新增用例
    :param request:
    :return:
    """
    if request.session.get('login_status'):
        acount = request.session["now_account"]
        if request.is_ajax():
            try:
                testcase_info = json.loads(request.body.decode('utf-8'))
            except ValueError:
                logger.error('用例信息解析异常：{testcase_info}'.format(testcase_info=testcase_info))
                return '用例信息解析异常'
            msg = case_info_logic(**testcase_info)
            return HttpResponse(get_ajax_msg(msg, '/api/test_list/1/'))
        elif request.method == 'GET':
            manage_info = {
                'account': acount,
                'project': ProjectInfo.objects.all().values('project_name').order_by('-create_time')
            }
            return render_to_response('add_case.html', manage_info)
    else:
        return HttpResponseRedirect("/api/login/")


def add_config(request):
    """
    新增配置
    :param request:
    :return:
    """
    if request.session.get('login_status'):
        acount = request.session["now_account"]
        if request.is_ajax():
            try:
                testconfig_info = json.loads(request.body.decode('utf-8'))
            except ValueError:
                logger.error('配置信息解析失败：{testconfig_info}'.format(testconfig_info=testconfig_info))
                return '配置信息解析异常'
            msg = config_info_logic(**testconfig_info)
            return HttpResponse(get_ajax_msg(msg, '/api/config_list/1/'))
        elif request.method == 'GET':
            manage_info = {
                'account': acount,
                'project': ProjectInfo.objects.all().values('project_name').order_by('-create_time')
            }
            return render_to_response('add_config.html', manage_info)
    else:
        return HttpResponseRedirect("/api/login/")


def run_test(request):
    """
    运行用例
    :param request:
    :return:
    """
    if request.session.get('login_status'):
        kwargs = {
            "failfast": False,
        }
        runner = HttpRunner(**kwargs)
        if request.is_ajax():
            try:
                kwargs = json.loads(request.body.decode('utf-8'))
            except ValueError:
                logging.error('待运行用例信息解析异常：{kwargs}'.format(kwargs=kwargs))
                return HttpResponse('信息解析异常，请重试')
            id = kwargs.pop('id')
            base_url = kwargs.pop('env_name')
            type = kwargs.pop('type')
            testcases_dict = run_by_module(id, base_url) if type == 'module' \
                else run_by_project(id, base_url)
            report_name = kwargs.get('report_name', None)
            if not testcases_dict:
                return HttpResponse('没有用例哦')
            main_hrun.delay(testcases_dict, report_name)
            return HttpResponse('用例执行中，请稍后查看报告即可,默认时间戳命名报告')
        else:
            id = request.POST.get('id')
            base_url = request.POST.get('env_name')
            type = request.POST.get('type', None)
            if type:
                testcases_dict = run_by_module(id, base_url) if type == 'module' \
                    else run_by_project(id, base_url)
            else:
                testcases_dict = run_by_single(id, base_url)
            if testcases_dict:
                runner.run(testcases_dict)
                return render_to_response('report_template.html', runner.summary)
            else:
                return HttpResponseRedirect('/api/index/')
    else:
        return HttpResponseRedirect("/api/login/")


def run_batch_test(request):
    """
    批量运行用例
    :param request:
    :return:
    """
    if request.session.get('login_status'):
        kwargs = {
            "failfast": False,
        }
        runner = HttpRunner(**kwargs)
        if request.is_ajax():
            try:
                kwargs = json.loads(request.body.decode('utf-8'))
            except ValueError:
                logging.error('待运行用例信息解析异常：{kwargs}'.format(kwargs=kwargs))
                return HttpResponse('信息解析异常，请重试')
            test_list = kwargs.pop('id')
            base_url = kwargs.pop('env_name')
            type = kwargs.pop('type')
            report_name = kwargs.get('report_name', None)
            testcases_dict = run_by_batch(test_list, base_url, type=type)
            if not testcases_dict:
                return HttpResponse('没有用例哦')
            main_hrun.delay(testcases_dict, report_name)
            return HttpResponse('用例执行中，请稍后查看报告即可,默认时间戳命名报告')
        else:
            type = request.POST.get('type', None)
            base_url = request.POST.get('env_name')
            test_list = request.body.decode('utf-8').split('&')
            if type:
                testcases_lists = run_by_batch(test_list, base_url, type=type, mode=True)
            else:
                testcases_lists = run_by_batch(test_list, base_url)
            if testcases_lists:
                runner.run(testcases_lists)
                return render_to_response('report_template.html', runner.summary)
            else:  # 没有用例默认重定向到首页
                return HttpResponseRedirect('/api/index/')
    else:
        return HttpResponseRedirect("/api/login/")


def project_list(request, id):
    """
    项目列表
    :param request:
    :param id: str or int：当前页
    :return:
    """
    if request.session.get('login_status'):
        acount = request.session["now_account"]
        if request.is_ajax():
            try:
                project_info = json.loads(request.body.decode('utf-8'))
            except ValueError:
                logging.debug('项目信息解析异常：{project_info}'.format(project_info=project_info))
                return HttpResponse('项目信息解析异常')
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
                'account': acount,
                'project': pro_list[1],
                'page_list': pro_list[0],
                'info': filter_query,
                'sum': pro_list[2],
                'env': EnvInfo.objects.all().order_by('-create_time')
            }
            return render_to_response('project_list.html', manage_info)
    else:
        return HttpResponseRedirect("/api/login/")


def module_list(request, id):
    """
    模块列表
    :param request:
    :param id: str or int：当前页
    :return:
    """
    if request.session.get('login_status'):
        acount = request.session["now_account"]
        if request.is_ajax():
            try:
                module_info = json.loads(request.body.decode('utf-8'))
            except ValueError:
                logging.error('模块信息解析异常：{module_info}'.format(module_info=module_info))
                return HttpResponse('模块信息解析异常')
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
                'account': acount,
                'module': module_list[1],
                'page_list': module_list[0],
                'info': filter_query,
                'sum': module_list[2],
                'env': EnvInfo.objects.all().order_by('-create_time')
            }
            return render_to_response('module_list.html', manage_info)
    else:
        return HttpResponseRedirect("/api/login/")


def test_list(request, id):
    """
    用例列表
    :param request:
    :param id: str or int：当前页
    :return:
    """
    if request.session.get('login_status'):
        acount = request.session["now_account"]
        if request.is_ajax():
            try:
                test_info = json.loads(request.body.decode('utf-8'))
            except ValueError:
                logging.error('用例信息解析异常：{test_info}'.format(test_info=test_info))
                return HttpResponse('用例信息解析异常')
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
                'account': acount,
                'test': test_list[1],
                'page_list': test_list[0],
                'info': filter_query,
                'env': EnvInfo.objects.all().order_by('-create_time')
            }
            return render_to_response('test_list.html', manage_info)
    else:
        return HttpResponseRedirect("/api/login/")


def config_list(request, id):
    """
    配置列表
    :param request:
    :param id: str or int：当前页
    :return:
    """
    if request.session.get('login_status'):
        acount = request.session["now_account"]
        if request.is_ajax():
            try:
                test_info = json.loads(request.body.decode('utf-8'))
            except ValueError:
                logging.error('配置信息解析异常：{test_info}'.format(test_info=test_info))
                return HttpResponse('配置信息解析异常')
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
                'account': acount,
                'test': test_list[1],
                'page_list': test_list[0],
                'info': filter_query
            }
            return render_to_response('config_list.html', manage_info)
    else:
        return HttpResponseRedirect("/api/login/")


def edit_case(request, id=None):
    """
    编辑用例
    :param request:
    :param id:
    :return:
    """
    if request.session.get('login_status'):
        acount = request.session["now_account"]
        if request.is_ajax():
            try:
                testcase_lists = json.loads(request.body.decode('utf-8'))
            except ValueError:
                logger.error('用例信息解析异常：{testcase_lists}'.format(testcase_lists=testcase_lists))
                return HttpResponse('用例信息解析异常')
            msg = case_info_logic(type=False, **testcase_lists)
            return HttpResponse(get_ajax_msg(msg, '/api/test_list/1/'))

        test_info = TestCaseInfo.objects.get_case_by_id(id)
        request = eval(test_info[0].request)
        include = eval(test_info[0].include)
        manage_info = {
            'account': acount,
            'info': test_info[0],
            'request': request['test'],
            'include': include,
            'project': ProjectInfo.objects.all().values('project_name').order_by('-create_time')
        }
        return render_to_response('edit_case.html', manage_info)

    else:
        return HttpResponseRedirect("/api/login/")


def edit_config(request, id=None):
    """
    编辑配置
    :param request:
    :param id:
    :return:
    """
    if request.session.get('login_status'):
        acount = request.session["now_account"]
        if request.is_ajax():
            try:
                testconfig_lists = json.loads(request.body.decode('utf-8'))
            except ValueError:
                logger.error('配置更新处理之前数据：{testconfig_lists}'.format(testconfig_lists=testconfig_lists))
            msg = config_info_logic(type=False, **testconfig_lists)
            return HttpResponse(get_ajax_msg(msg, '/api/config_list/1/'))

        config_info = TestCaseInfo.objects.get_case_by_id(id)
        request = eval(config_info[0].request)
        manage_info = {
            'account': acount,
            'info': config_info[0],
            'request': request['config'],
            'project': ProjectInfo.objects.all().values(
                'project_name').order_by('-create_time')
        }
        return render_to_response('edit_config.html', manage_info)
    else:
        return HttpResponseRedirect("/api/login/")


def env_set(request):
    """
    环境设置
    :param request:
    :return:
    """
    if request.session.get('login_status'):
        acount = request.session["now_account"]
        if request.is_ajax():
            try:
                env_lists = json.loads(request.body.decode('utf-8'))
            except ValueError:
                logging.error('环境信息解析异常：{env_lists}'.format(env_lists=env_lists))
                return HttpResponse('环境信息查询异常，请重试')
            msg = env_data_logic(**env_lists)
            return HttpResponse(get_ajax_msg(msg, 'ok'))

        elif request.method == 'GET':
            return render_to_response('env_list.html', {'account': acount})

    else:
        return HttpResponseRedirect("/api/login/")


def env_list(request, id):
    """
    环境列表
    :param request:
    :param id: str or int：当前页
    :return:
    """
    if request.session.get('login_status'):
        acount = request.session["now_account"]
        if request.method == 'GET':
            env_lists = get_pager_info(
                EnvInfo, None, '/api/env_list/', id)
            manage_info = {
                'account': acount,
                'env': env_lists[1],
                'page_list': env_lists[0],
            }
            return render_to_response('env_list.html', manage_info)
    else:
        return HttpResponseRedirect('/api/login/')


def report_list(request, id):
    """
    报告列表
    :param request:
    :param id: str or int：当前页
    :return:
    """
    if request.session.get('login_status'):
        if request.is_ajax():
            try:
                report_info = json.loads(request.body.decode('utf-8'))
            except ValueError:
                logging.error('报告信息解析异常：{report_info}'.format(report_info=report_info))
                return HttpResponse('报告信息解析异常')
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
    else:
        return HttpResponseRedirect("/api/login/")


def view_report(request, id):
    """
    查看报告
    :param request:
    :param id: str or int：报告名称索引
    :return:
    """
    if request.session.get('login_status'):
        reports = eval(TestReports.objects.get(id=id).reports)
        reports.get('time')['start_at'] = TestReports.objects.get(id=id).start_at
        return render_to_response('report_template.html', reports)
    else:
        return HttpResponseRedirect("/api/login/")


def periodictask(request, id):
    """
    定时任务列表
    :param request:
    :param id: str or int：当前页
    :return:
    """
    if request.session.get('login_status'):
        acount = request.session["now_account"]
        if request.is_ajax():
            try:
                kwargs = json.loads(request.body.decode('utf-8'))
            except ValueError:
                logging.error('定时任务信息解析异常: {kwargs}'.format(kwargs=kwargs))
                return HttpResponse('定时任务信息解析异常，请重试')
            mode = kwargs.pop('mode')
            id = kwargs.pop('id')
            msg = delete_task(id) if mode == 'del' else change_task_status(id, mode)
            return HttpResponse(get_ajax_msg(msg, 'ok'))
        else:
            filter_query = set_filter_session(request)
            task_list = get_pager_info(
                PeriodicTask, filter_query, '/api/periodictask/', id)
            manage_info = {
                'account': acount,
                'task': task_list[1],
                'page_list': task_list[0],
                'info': filter_query
            }
        return render_to_response('periodictask_list.html', manage_info)
    else:
        return HttpResponseRedirect("/api/login/")


def add_task(request):
    """
    添加任务
    :param request:
    :return:
    """
    if request.session.get('login_status'):
        acount = request.session["now_account"]
        if request.is_ajax():
            try:
                kwargs = json.loads(request.body.decode('utf-8'))
            except ValueError:
                logging.error('定时任务信息解析异常: {kwargs}'.format(kwargs=kwargs))
                return HttpResponse('定时任务信息解析异常，请重试')
            msg = task_logic(**kwargs)
            return HttpResponse(get_ajax_msg(msg, '/api/periodictask/1/'))
        elif request.method == 'GET':
            info = {
                'account': acount,
                'env': EnvInfo.objects.all().order_by('-create_time'),
                'project': ProjectInfo.objects.all().order_by('-create_time')
            }
            return render_to_response('add_task.html', info)
    else:
        return HttpResponseRedirect("/api/login/")


def upload_file(request):
    if request.session.get('login_status'):
        account = request.session["now_account"]
        separator = '\\' if platform.system() == 'Windows' else '/'
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
        else:
            return HttpResponseRedirect("/api/login/")


def get_project_info(request):
    """
     获取项目相关信息
     :param request:
     :return:
     """
    if request.session.get('login_status'):
        if request.is_ajax():
            try:
                project_info = json.loads(request.body.decode('utf-8'))
            except ValueError:
                logger.error('获取项目信息异常：{project_info}'.format(project_info=project_info))
                return HttpResponse('项目信息解析异常')
            msg = load_modules(**project_info.pop('task'))
            return HttpResponse(msg)
    else:
        return HttpResponseRedirect("/api/login/")


def download_report(request, id):
    if request.method == 'GET':
        report_dir_path = os.path.join(os.getcwd(), "reports")
        if os.path.exists(report_dir_path):
            shutil.rmtree(report_dir_path)

        runner = HttpRunner()
        runner.summary = eval(TestReports.objects.get(id=id).reports)
        runner.gen_html_report()

        html_report_name = runner.summary.get('time')['start_at'] + '.html'
        report_dir_path = os.path.join(report_dir_path, html_report_name)

        def file_iterator(file_name, chunk_size=512):
            with open(file_name, encoding='utf-8') as f:
                while True:
                    c = f.read(chunk_size)
                    if c:
                        yield c
                    else:
                        break

        the_file_name = report_dir_path
        response = StreamingHttpResponse(file_iterator(the_file_name))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format(html_report_name)
        return response




def test_login_valid(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username == 'lcc' and password == 'lcc':
            return JsonResponse({"status": True, "code": "0001"})
        else:
            return JsonResponse({"status": False, "code": "0009"})


def test_login_json(request):
    if request.method == 'POST':
        info = json.loads(request.body.decode('utf-8'))
        username = info.get("username")
        password = info.get("password")
        if username == 'lcc' and password == 'lcc':
            return JsonResponse({"status": True, "code": "0001"})
        else:
            return JsonResponse({"status": False, "code": "0009"})

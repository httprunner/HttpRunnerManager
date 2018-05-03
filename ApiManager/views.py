import json
import logging

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from djcelery.models import PeriodicTask

from ApiManager.models import ProjectInfo, ModuleInfo, TestCaseInfo, UserInfo, EnvInfo, TestReports
from ApiManager.tasks import main_hrun
from ApiManager.utils.common import module_info_logic, project_info_logic, case_info_logic, config_info_logic, \
    set_filter_session, get_ajax_msg, register_info_logic, task_logic
from ApiManager.utils.operation import env_data_logic, del_module_data, del_project_data, del_test_data
from ApiManager.utils.pagination import get_pager_info
from ApiManager.utils.runner import run_by_single, run_by_batch, run_by_module, run_by_project
from ApiManager.utils.task_opt import create_task, delete_task, change_task_status
from httprunner import HttpRunner

logger = logging.getLogger('HttpRunnerManager')
# Create your views here.

'''登录'''


def login(request):
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


'''注册'''


def register(request):
    if request.is_ajax():
        user_info = json.loads(request.body.decode('utf-8'))
        msg = register_info_logic(**user_info)
        return HttpResponse(get_ajax_msg(msg, '恭喜您，账号已成功注册'))
    elif request.method == 'GET':
        return render_to_response("register.html")


'''注销'''


def log_out(request):
    if request.method == 'GET':
        logger.info('{username}退出'.format(username=request.session['now_account']))
        try:
            del request.session['now_account']
        except Exception:
            logging.error('session invalid')
        return HttpResponseRedirect("/api/login/")


'''首页'''


def index(request):
    if request.session.get('login_status'):
        project_length = ProjectInfo.objects.count()
        module_length = ModuleInfo.objects.count()
        test_length = TestCaseInfo.objects.filter(type__exact=1).count()
        config_length = TestCaseInfo.objects.filter(type__exact=2).count()
        manage_info = {
            'project_length': project_length,
            'module_length': module_length,
            'test_length': test_length,
            'config_length': config_length,
            'account': request.session["now_account"]
        }
        return render_to_response('index.html', manage_info)
    else:
        return HttpResponseRedirect("/api/login/")


'''添加项目'''


def add_project(request):
    if request.session.get('login_status'):
        if request.is_ajax():
            try:
                project_info = json.loads(request.body.decode('utf-8'))
            except ValueError:
                logger.error('项目信息解析异常: {project_info}'.format(project_info=project_info))
                return HttpResponse('项目信息新增异常')
            msg = project_info_logic(**project_info)
            return HttpResponse(get_ajax_msg(msg, '项目添加成功'))

        elif request.method == 'GET':
            manage_info = {
                'account': request.session["now_account"]
            }
            return render_to_response('add_project.html', manage_info)
    else:
        return HttpResponseRedirect("/api/login/")


'''添加模块'''


def add_module(request):
    if request.session.get('login_status'):
        if request.is_ajax():
            try:
                module_info = json.loads(request.body.decode('utf-8'))
            except ValueError:
                logger.error('模块信息解析异常：{module_info}'.format(module_info=module_info))
            msg = module_info_logic(**module_info)
            return HttpResponse(get_ajax_msg(msg, '模块添加成功'))
        elif request.method == 'GET':
            manage_info = {
                'account': request.session["now_account"],
                'data': ProjectInfo.objects.all().values('project_name')
            }
            return render_to_response('add_module.html', manage_info)
    else:
        return HttpResponseRedirect("/api/login/")


'''
添加用例
'''


def add_case(request):
    if request.session.get('login_status'):
        if request.is_ajax():
            try:
                testcase_info = json.loads(request.body.decode('utf-8'))
            except ValueError:
                logger.error('用例信息解析异常：{testcase_info}'.format(testcase_info=testcase_info))
                return '用例信息解析异常'
            msg = case_info_logic(**testcase_info)
            return HttpResponse(get_ajax_msg(msg, '用例添加成功'))
        elif request.method == 'GET':
            manage_info = {
                'account': request.session["now_account"],
                'project': ProjectInfo.objects.all().values('project_name').order_by('-create_time')
            }
            return render_to_response('add_case.html', manage_info)
    else:
        return HttpResponseRedirect("/api/login/")


'''添加配置'''


def add_config(request):
    if request.session.get('login_status'):
        if request.is_ajax():
            try:
                testconfig_info = json.loads(request.body.decode('utf-8'))
            except ValueError:
                logger.error('配置信息解析失败：{testconfig_info}'.format(testconfig_info=testconfig_info))
                return '配置信息解析异常'
            msg = config_info_logic(**testconfig_info)
            return HttpResponse(get_ajax_msg(msg, '配置添加成功'))
        elif request.method == 'GET':
            manage_info = {
                'account': request.session["now_account"],
                'project': ProjectInfo.objects.all().values('project_name').order_by('-create_time')
            }
            return render_to_response('add_config.html', manage_info)
    else:
        return HttpResponseRedirect("/api/login/")


'''单个执行'''


def run_test(request):
    if request.session.get('login_status'):
        if request.is_ajax():
            try:
                kwargs = json.loads(request.body.decode('utf-8'))
            except ValueError:
                logging.error('待运行用例信息解析异常：{kwargs}'.format(kwargs=kwargs))
                return HttpResponse('信息解析异常，请重试')
            id = kwargs.pop('id')
            base_url = kwargs.pop('env_name')
            type = kwargs.pop('type')
            testcases_dict = run_by_module(id, base_url) if type == 'module' else run_by_project(id, base_url)
            if not testcases_dict:
                return HttpResponse('没有用例哦')
            main_hrun.delay(testcases_dict)
            return HttpResponse('用例执行中，请稍后查看报告即可,默认时间戳命名报告')
        else:
            kwargs = {
                "failfast": False,
            }
            runner = HttpRunner(**kwargs)
            index = request.POST.get('index')
            base_url = request.POST.get('env_name')
            testcases_dict = run_by_single(index, base_url)
            runner.run(testcases_dict)
            return render_to_response('report_template.html', runner.summary)
    else:
        return HttpResponseRedirect("/api/login/")


'''批量运行'''


def run_batch_test(request):
    if request.session.get('login_status'):
        if request.is_ajax():
            try:
                kwargs = json.loads(request.body.decode('utf-8'))
            except ValueError:
                logging.error('待运行用例信息解析异常：{kwargs}'.format(kwargs=kwargs))
                return HttpResponse('信息解析异常，请重试')
            test_list = kwargs.pop('id')
            base_url = kwargs.pop('env_name')
            type = kwargs.pop('type')
            testcases_dict = run_by_batch(test_list, base_url, type)
            if not testcases_dict:
                return HttpResponse('没有用例哦')
            main_hrun.delay(testcases_dict)
            return HttpResponse('用例执行中，请稍后查看报告即可,默认时间戳命名报告')
        else:
            base_url = request.POST.get('env_name')
            test_list = request.body.decode('utf-8').split('&')
            testcases_lists = run_by_batch(test_list, base_url)
            kwargs = {
                "failfast": False,
            }
            runner = HttpRunner(**kwargs)
            runner.run(testcases_lists)
            return render_to_response('report_template.html', runner.summary)
    else:
        return HttpResponseRedirect("/api/login/")


'''项目列表'''


def project_list(request, id):
    if request.session.get('login_status'):
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
                'account': request.session["now_account"],
                'project': pro_list[1],
                'page_list': pro_list[0],
                'info': filter_query,
                'sum': pro_list[2],
                'env': EnvInfo.objects.all().order_by('-create_time')
            }
            return render_to_response('project_list.html', manage_info)
    else:
        return HttpResponseRedirect("/api/login/")


'''模块列表'''


def module_list(request, id):
    if request.session.get('login_status'):
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
                'account': request.session["now_account"],
                'module': module_list[1],
                'page_list': module_list[0],
                'info': filter_query,
                'sum': module_list[2],
                'env': EnvInfo.objects.all().order_by('-create_time')
            }
            return render_to_response('module_list.html', manage_info)
    else:
        return HttpResponseRedirect("/api/login/")


'''用例列表'''


def test_list(request, id):
    if request.session.get('login_status'):
        if request.is_ajax():
            try:
                test_info = json.loads(request.body.decode('utf-8'))
            except ValueError:
                logging.error('用例信息解析异常：{test_info}'.format(test_info=test_info))
                return HttpResponse('用例信息解析异常')
            if 'mode' in test_info.keys():
                msg = del_test_data(test_info.pop('id'))
            return HttpResponse(get_ajax_msg(msg, 'ok'))

        else:
            filter_query = set_filter_session(request)
            test_list = get_pager_info(
                TestCaseInfo, filter_query, '/api/test_list/', id)
            manage_info = {
                'account': request.session["now_account"],
                'test': test_list[1],
                'page_list': test_list[0],
                'info': filter_query,
                'env': EnvInfo.objects.all().order_by('-create_time')
            }
            return render_to_response('test_list.html', manage_info)
    else:
        return HttpResponseRedirect("/api/login/")


'''配置列表'''


def config_list(request, id):
    if request.session.get('login_status'):
        if request.is_ajax():
            try:
                test_info = json.loads(request.body.decode('utf-8'))
            except ValueError:
                logging.error('配置信息解析异常：{test_info}'.format(test_info=test_info))
                return HttpResponse('配置信息解析异常')
            if 'mode' in test_info.keys():
                msg = del_test_data(test_info.pop('id'))
            return HttpResponse(get_ajax_msg(msg, 'ok'))
        else:
            filter_query = set_filter_session(request)
            test_list = get_pager_info(
                TestCaseInfo, filter_query, '/api/config_list/', id)
            manage_info = {
                'account': request.session["now_account"],
                'test': test_list[1],
                'page_list': test_list[0],
                'info': filter_query
            }
            return render_to_response('config_list.html', manage_info)
    else:
        return HttpResponseRedirect("/api/login/")


'''用例编辑'''


def edit_case(request):
    if request.session.get('login_status'):
        if request.is_ajax():
            try:
                testcase_lists = json.loads(request.body.decode('utf-8'))
            except ValueError:
                logger.error('用例信息解析异常：{testcase_lists}'.format(testcase_lists=testcase_lists))
                return HttpResponse('用例信息解析异常')
            msg = case_info_logic(type=False, **testcase_lists)
            return HttpResponse(get_ajax_msg(msg, '用例更新成功'))

        elif request.method == 'POST':
            id = request.POST.get('id')
            account = request.POST.get('account')
            test_info = TestCaseInfo.objects.get_case_by_id(id)
            request = eval(test_info[0].request)
            manage_info = {
                'account': account,
                'info': test_info[0],
                'request': request['test'],
                'project': ProjectInfo.objects.all().values('project_name').order_by('-create_time')
            }
            return render_to_response('edit_case.html', manage_info)
    else:
        return HttpResponseRedirect("/api/login/")


'''配置编辑'''


def edit_config(request):
    if request.session.get('login_status'):
        if request.is_ajax():
            testconfig_lists = json.loads(request.body.decode('utf-8'))
            logger.error('配置更新处理之前数据：{testconfig_lists}'.format(testconfig_lists=testconfig_lists))
            msg = config_info_logic(type=False, **testconfig_lists)
            return HttpResponse(get_ajax_msg(msg, '配置更新成功'))

        elif request.method == 'POST':
            id = request.POST.get('id')
            account = request.POST.get('account')
            test_info = TestCaseInfo.objects.get_case_by_id(id)
            request = eval(test_info[0].request)
            manage_info = {
                'account': account,
                'info': test_info[0],
                'request': request['config'],
                'project': ProjectInfo.objects.all().values(
                    'project_name').order_by('-create_time')
            }
            return render_to_response('edit_config.html', manage_info)
        else:
            return HttpResponseRedirect("/api/login/")


'''环境设置'''


def env_set(request):
    if request.session.get('login_status'):
        if request.is_ajax():
            try:
                env_lists = json.loads(request.body.decode('utf-8'))
            except ValueError:
                logging.error('环境信息解析异常：{env_lists}'.format(env_lists=env_lists))
                return HttpResponse('环境信息查询异常，请重试')
            msg = env_data_logic(**env_lists)
            return HttpResponse(get_ajax_msg(msg, 'ok'))

        elif request.method == 'GET':
            return render_to_response('env_list.html', {'account': request.session["now_account"]})

    else:
        return HttpResponseRedirect("/api/login/")


'''环境列表'''


def env_list(request, id):
    if request.session.get('login_status'):
        if request.method == 'GET':
            env_lists = get_pager_info(
                EnvInfo, None, '/api/env_list/', id)
            manage_info = {
                'account': request.session["now_account"],
                'env': env_lists[1],
                'page_list': env_lists[0],
            }
            return render_to_response('env_list.html', manage_info)
    else:
        return HttpResponseRedirect('/api/login/')

    '''test celery'''


def report_list(request, id):
    if request.session.get('login_status'):
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
    if request.session.get('login_status'):
        reports = eval(TestReports.objects.get(id=id).reports)
        reports.get('time')['start_at'] = TestReports.objects.get(id=id).start_at
        return render_to_response('report_template.html', reports)
    else:
        return HttpResponseRedirect("/api/login/")


def periodictask(request, id):
    if request.session.get('login_status'):
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
                'account': request.session["now_account"],
                'task': task_list[1],
                'page_list': task_list[0],
                'info': filter_query
            }
        return render_to_response('periodictask_list.html', manage_info)
    else:
        return HttpResponseRedirect("/api/login/")


def add_task(request):
    if request.session.get('login_status'):
        if request.is_ajax():
            try:
                kwargs = json.loads(request.body.decode('utf-8'))
            except ValueError:
                logging.error('定时任务信息解析异常: {kwargs}'.format(kwargs=kwargs))
                return HttpResponse('定时任务信息解析异常，请重试')
            msg = task_logic(**kwargs)
            return HttpResponse(get_ajax_msg(msg, '任务添加成功'))
        elif request.method == 'GET':
            info = {
                'env': EnvInfo.objects.all().order_by('-create_time'),
                'project': ProjectInfo.objects.all().order_by('-create_time')
            }
            return render_to_response('add_task.html', info)
    else:
        return HttpResponseRedirect("/api/login/")


'''测试代码'''


def test_api(request):
    if request.method == 'GET':
        if request.GET.get('username') == 'lcc':
            return HttpResponse(json.dumps({'status': 'ok'}))
        else:
            return HttpResponse('illegal')
    elif request.method == 'POST':

        if request.POST.get('username') == 'lcc' and request.POST.get('password') == 'lcc':
            a = {'code': 'success', 'status': True}
            return HttpResponse(json.dumps(a))
        elif json.loads(request.body.decode('utf-8')).get('username') == 'yinquanwang':
            return HttpResponse('this is a json post request')
        else:
            return HttpResponse('this is a post request')


def test_tasks(request, id):
    create_task(str(id), 'ApiManager.tasks.add', {"x": 1, "y": 2}, {
        'day_of_week': 0,
        'month_of_year': '*',  # 月份
        'day_of_month': '*',  # 日期
        'hour': '*',  # 小时
        'minute': '*',  # 分钟
    })
    delete_task('6')
    return HttpResponse('ok')

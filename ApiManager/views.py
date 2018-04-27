import json
import logging

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response

from ApiManager.models import ProjectInfo, ModuleInfo, TestCaseInfo, UserInfo, EnvInfo
from ApiManager.tasks import add
from ApiManager.utils.common import module_info_logic, project_info_logic, case_info_logic, config_info_logic, \
    set_filter_session, get_ajax_msg, register_info_logic
from ApiManager.utils.operation import env_data_logic, del_module_data, del_project_data, del_test_data
from ApiManager.utils.pagination import get_pager_info
from ApiManager.utils.runner import run_by_single
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
        del request.session['now_account']
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
                testcase_lists = json.loads(request.body.decode('utf-8'))
            except ValueError:
                logger.error('用例信息解析异常：{testcase_lists}'.format(testcase_lists=testcase_lists))
            msg = case_info_logic(**testcase_lists)
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
            testconfig_lists = json.loads(request.body.decode('utf-8'))
            logger.debug('处理前配置信息：{testconfig_lists}'.format(testconfig_lists=testconfig_lists))
            msg = config_info_logic(**testconfig_lists)
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
        kwargs = {
            "failfast": False,
        }
        runner = HttpRunner(**kwargs)
        if request.method == 'POST':
            mode = request.POST.get('mode')
            id = request.POST.get('id')
            if mode == 'run_by_test':
                test = run_by_single(id)
                runner.run(test)
                return render_to_response('report_template.html', runner.summary)
    else:
        return HttpResponseRedirect("/api/login/")


'''添加接口'''


def add_api(request):
    if request.session.get('login_status'):
        return render_to_response('add_api.html')
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
                'sum': pro_list[2]
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
            }
            return render_to_response('module_list.html', manage_info)
    else:
        return HttpResponseRedirect("/api/login/")


'''配置或用例列表'''


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
                'info': filter_query
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
                'request': request['config']
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


def test_celery(request):
    add.delay(1, 2)
    return HttpResponse('ok')


'''测试代码'''


def test_api(request):
    if request.method == 'GET':
        if request.GET.get('username') == 'lcc':
            return HttpResponse(json.dumps({'status': 'ok'}))
        else:
            return HttpResponse('illegal')
    elif request.method == 'POST':

        if request.POST.get('username') == 'lcc' and request.POST.get('password') == 'lcc':
            a = {'login': 'success', 'status': True}
            return HttpResponse(json.dumps(a))
        elif json.loads(request.body.decode('utf-8')).get('username') == 'yinquanwang':
            return HttpResponse('this is a json post request')
        else:
            return HttpResponse('this is a post request')

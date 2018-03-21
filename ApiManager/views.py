import json
import os

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response

from ApiManager.logic.common import module_info_logic, project_info_logic, case_info_logic, config_info_logic, \
    set_filter_session, get_ajax_msg, register_info_logic, yml_parser
from ApiManager.logic.operation import change_status
from ApiManager.logic.pagination import get_pager_info
from ApiManager.logic.runner import run_by_batch, get_result, run_by_single, run_by_module, run_by_project
from ApiManager.models import ProjectInfo, ModuleInfo, TestCaseInfo, UserInfo
from ApiManager.tasks import add
from httprunner.cli import main_ate

# Create your views here.

'''登录'''


def login(request):
    if request.method == 'POST':
        username = request.POST.get('account')
        password = request.POST.get('password')
        if UserInfo.objects.filter(username__exact=username).filter(password__exact=password).count() == 1:
            request.session["login_status"] = True
            request.session["now_account"] = username
            return HttpResponseRedirect('/api/index/')
        else:
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
        del request.session['now_account']
        return HttpResponseRedirect("/api/login/")


'''首页'''


def index(request):
    if request.session.get('login_status'):
        project_length = ProjectInfo.objects.count()
        module_length = ModuleInfo.objects.count()
        test_length = TestCaseInfo.objects.filter(type__exact=1).count()
        manage_info = {
            'project_length': project_length,
            'module_length': module_length,
            'test_length': test_length,
            'account': request.session["now_account"]
        }
        return render_to_response('index.html', manage_info)
    else:
        return HttpResponseRedirect("/api/login/")


'''添加项目'''


def add_project(request):
    if request.session.get('login_status'):
        if request.is_ajax():
            project_info = json.loads(request.body.decode('utf-8'))
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
            module_info = json.loads(request.body.decode('utf-8'))
            msg = module_info_logic(**module_info)
            return HttpResponse(get_ajax_msg(msg, '模块添加成功'))
        elif request.method == 'GET':
            manage_info = {
                'account': request.session["now_account"],
                'data': ProjectInfo.objects.all().values('pro_name')
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
            testcase_lists = json.loads(request.body.decode('utf-8'))
            msg = case_info_logic(**testcase_lists)
            return HttpResponse(get_ajax_msg(msg, '用例添加成功'))
        elif request.method == 'GET':
            manage_info = {
                'account': request.session["now_account"],
                'project': ProjectInfo.objects.all().values('pro_name').order_by('-create_time')
            }
            return render_to_response('add_case.html', manage_info)
    else:
        return HttpResponse('session invalid')


'''添加配置'''


def add_config(request):
    if request.session.get('login_status'):
        if request.is_ajax():
            testconfig_lists = json.loads(request.body.decode('utf-8'))
            msg = config_info_logic(**testconfig_lists)
            return HttpResponse(get_ajax_msg(msg, '配置添加成功'))
        elif request.method == 'GET':
            manage_info = {
                'account': request.session["now_account"],
                'project': ProjectInfo.objects.all().values('pro_name').order_by('-create_time')
            }
            return render_to_response('add_config.html', manage_info)
    else:
        return HttpResponse('session invalid')


'''单个执行'''


def run_test(request):
    if request.session.get('login_status'):
        if request.method == 'POST':
            mode = request.POST.get('mode')
            id = request.POST.get('id')
            if mode == 'run_by_test':
                result = main_ate(run_by_single(id))
            elif mode == 'run_by_module':
                test_lists = run_by_module(id)
                result = get_result(test_lists)
            elif mode == 'run_by_project':
                test_lists = run_by_project(id)
                result = get_result(test_lists)
            return render_to_response('report_template.html', result)
    else:
        return HttpResponseRedirect("/api/login/")


'''批量执行'''


def run_batch_test(request):
    if request.session.get('login_status'):
        if request.method == 'POST':
            test_lists = run_by_batch(request.body.decode('ascii').split('&'))
            result = get_result(test_lists)
            return render_to_response('report_template.html', result)
    else:
        return render_to_response("login.html")


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
            project_info = json.loads(request.body.decode('utf-8'))

            if 'status' in project_info.keys():
                msg = change_status(ProjectInfo, **project_info)
                return HttpResponse(get_ajax_msg(msg, '项目状态已更改！'))
            else:
                msg = project_info_logic(type=False, **project_info)
                return HttpResponse(get_ajax_msg(msg, '项目信息更新成功'))
        else:
            filter_query = set_filter_session(request)
            pro_list = get_pager_info(
                ProjectInfo, filter_query, '/api/project_list/', id)
            manage_info = {
                'account': request.session["now_account"],
                'project': pro_list[1],
                'page_list': pro_list[0],
                'info': filter_query
            }
            return render_to_response('project_list.html', manage_info)
    else:
        return HttpResponseRedirect("/api/login/")


'''模块列表'''


def module_list(request, id):
    if request.session.get('login_status'):
        if request.is_ajax():
            module_info = json.loads(request.body.decode('utf-8'))

            if 'status' in module_info.keys():
                msg = change_status(ModuleInfo, **module_info)
                return HttpResponse(get_ajax_msg(msg, '模块状态已更改！'))
            else:
                msg = module_info_logic(type=False, **module_info)
                return HttpResponse(get_ajax_msg(msg, '模块信息更新成功'))
        else:
            filter_query = set_filter_session(request)
            module_list = get_pager_info(
                ModuleInfo, filter_query, '/api/module_list/', id)
            manage_info = {
                'account': request.session["now_account"],
                'module': module_list[1],
                'page_list': module_list[0],
                'info': filter_query
            }
            return render_to_response('module_list.html', manage_info)
    else:
        return HttpResponseRedirect("/api/login/")


'''配置或用例列表'''


def test_list(request, id):
    if request.session.get('login_status'):
        if request.is_ajax():
            test_info = json.loads(request.body.decode('utf-8'))
            if 'status' in test_info.keys():
                msg = change_status(TestCaseInfo, **test_info)
                return HttpResponse(get_ajax_msg(msg, '用例已更改！'))
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
            test_info = json.loads(request.body.decode('utf-8'))
            if 'status' in test_info.keys():
                msg = change_status(TestCaseInfo, **test_info)
                return HttpResponse(get_ajax_msg(msg, '配置已更改！'))
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
            testcase_lists = json.loads(request.body.decode('utf-8'))
            msg = case_info_logic(**testcase_lists, type=False)
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
                'project': ProjectInfo.objects.all().values('pro_name').order_by('-create_time')
            }
            return render_to_response('edit_case.html', manage_info)
    else:
        return HttpResponseRedirect("/api/login/")


'''配置编辑'''


def edit_config(request):
    if request.session.get('login_status'):
        if request.is_ajax():
            testconfig_lists = json.loads(request.body.decode('utf-8'))
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


def upload(request):
    """
    实现文件上传，
    :param request:
    :return:
    """
    if request.method == 'GET':
        return HttpResponse('上传失败，请使用POST方法上传文件')
    elif request.method == 'POST':
        obj = request.FILES.get('file')
        temp_save = os.path.join('upload', obj.name)
        f = open(temp_save, 'wb')
        for line in obj.chunks():
            f.write(line)
        f.close()
        yml_parser(temp_save)

        return HttpResponse('上传成功')


